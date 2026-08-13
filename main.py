#!/usr/bin/env python3
"""
Medical Device Change Assessment & Documentation Tool (Python)

워크플로우:
    1. 제품 정보 입력
    2. 변경 사항 입력
    3. 국가별 가이던스 기반 중대성 평가 (FDA / HC / EU)
    4. 중대하지 않은 변경의 경우 워드 문서 자동 생성

가이던스 출처:
    - FDA: Deciding When to Submit a 510(k) for a Change to an Existing Device (Oct 2017)
    - HC : Guidance on the Interpretation of Significant Change of a Medical Device – Types of Changes
    - EU : MDCG 2020-3 Rev.1 (Article 120 MDR)
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

# Local imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from assessor_fda import run_fda_questionnaire, assess_fda
from assessor_hc import run_hc_questionnaire, assess_hc
from assessor_eu import run_eu_questionnaire, assess_eu
from doc_fda import build_fda_document
from doc_hc import build_hc_document
from doc_eu import build_eu_document


# ===== Interactive Helpers =====
def ask(question: str) -> str:
    """간단한 입력 받기"""
    return input(question).strip()


def ask_yes_no(question: str) -> bool:
    """y/n 입력 받기"""
    while True:
        ans = ask(f"{question} (y/n): ").lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("  ⚠️  유효한 입력: y, n")


def print_banner():
    print("\n" + "═" * 72)
    print("  Medical Device Change Assessment & Documentation Tool")
    print("  의료기기 변경 평가 및 인허가 문서 자동 생성 도구")
    print("═" * 72 + "\n")


def print_section(title: str):
    print("\n" + "─" * 72)
    print(f"  ▶ {title}")
    print("─" * 72)


# ===== Step 1: Product Information =====
def gather_product_info() -> dict:
    print_section("STEP 1. 제품 정보 입력")

    return {
        "modelName":            ask("  모델명 (Model Name): "),
        "deviceClass":          ask("  의료기기 등급 (e.g., Class II / IIb): "),
        "manufacturer":         ask("  제조사 (Legal Manufacturer) [Ray Co., Ltd.]: ") or "Ray Co., Ltd.",
        "manufacturerAddress":  ask("  제조사 주소 [1F~3F, 4F(Part), 5F, 265 Daeji-ro, Suji-gu, Yongin-si, Gyeonggi-do, Republic of Korea, 16882]: ") or "1F~3F, 4F(Part), 5F, 265 Daeji-ro, Suji-gu, Yongin-si, Gyeonggi-do, Republic of Korea, 16882",
        "fdaK510":              ask("  FDA 510(k) Number (없으면 Enter): ") or "N/A",
        "fdaProductCode":       ask("  FDA Product Code (없으면 Enter): ") or "N/A",
        "fdaRegulationNumber":  ask("  FDA Regulation Number (없으면 Enter): ") or "N/A",
        "hcLicenceNo":          ask("  Health Canada Licence No. (없으면 Enter): ") or "N/A",
        "euCertNumber":         ask("  EU NB Certificate Number (없으면 Enter): ") or "N/A",
        "euNotifiedBody":       ask("  EU Notified Body (없으면 Enter): ") or "N/A",
        "euBasicUDIDI":         ask("  EU Basic UDI-DI (없으면 Enter): ") or "N/A",
    }


# ===== Step 2: Change Description =====
def gather_change_info() -> dict:
    print_section("STEP 2. 변경 사항 입력")

    print("\n  변경 카테고리 선택:")
    print("    1) Labeling / Nomenclature  (라벨링 / 명칭)")
    print("    2) Design / Hardware        (설계 / 하드웨어)")
    print("    3) Software / Firmware      (소프트웨어 / 펌웨어)")
    print("    4) Materials                (재료)")
    print("    5) Manufacturing Process    (제조 공정)")
    print("    6) Performance Spec         (성능 사양)")
    print("    7) Intended Use             (사용 목적)")
    print("    8) Sterilization            (멸균)")
    print("    9) Other")

    category_map = {
        "1": "labeling", "2": "design", "3": "software",
        "4": "material", "5": "manufacturing", "6": "performance",
        "7": "intended_use", "8": "sterilization", "9": "other"
    }

    while True:
        choice = ask("  카테고리 선택 (1-9): ")
        if choice in category_map:
            break
        print("  ⚠️  1-9 중 하나를 입력하세요.")

    return {
        "category":      category_map[choice],
        "componentName": ask("  변경 대상 구성품 (e.g., Detector, PCB, Sensor): "),
        "changeTitle":   ask("  변경 사항 한줄 요약: "),
        "beforeValue":   ask("  변경 전 (Before): "),
        "afterValue":    ask("  변경 후 (After): "),
        "reason":        ask("  변경 사유 (Reason): "),
        "description":   ask("  변경 상세 설명 (Description): "),
    }


# ===== Step 3: Country Selection =====
def select_countries() -> list:
    print_section("STEP 3. 평가 대상 국가 선택")
    print("\n  평가할 국가/지역을 선택하세요 (복수 선택 가능):")

    targets = []
    if ask_yes_no("    🇺🇸  FDA (미국) 평가하시겠습니까?"):
        targets.append("FDA")
    if ask_yes_no("    🇨🇦  Health Canada (캐나다) 평가하시겠습니까?"):
        targets.append("HC")
    if ask_yes_no("    🇪🇺  EU MDR (유럽) 평가하시겠습니까?"):
        targets.append("EU")

    if not targets:
        print("\n  ⚠️  최소 1개 국가를 선택해야 합니다.")
        return select_countries()

    return targets


def run_assessment(country: str, product_info: dict, change_info: dict) -> dict:
    print_section(f"STEP 3-{country}. {country} 가이던스 기반 중대성 평가")

    if country == "FDA":
        print("\n  [참조 가이던스] FDA \"Deciding When to Submit a 510(k) for a")
        print("                   Change to an Existing Device\" (Oct 2017)")
        print("  URL: https://www.fda.gov/regulatory-information/search-fda-guidance-")
        print("       documents/deciding-when-submit-510k-change-existing-device\n")
        answers = run_fda_questionnaire(ask, ask_yes_no, change_info)
        result = assess_fda(answers, change_info)

    elif country == "HC":
        print("\n  [참조 가이던스] Health Canada – Types of Changes")
        print("  URL: https://www.canada.ca/en/health-canada/services/drugs-health-")
        print("       products/medical-devices/application-information/guidance-")
        print("       documents/interpret-significant-change-medical-device/types-")
        print("       of-changes.html\n")
        answers = run_hc_questionnaire(ask, ask_yes_no, change_info)
        result = assess_hc(answers, change_info)

    elif country == "EU":
        print("\n  [참조 가이던스] MDCG 2020-3 Rev.1 (EU MDR Article 120)")
        print("  URL: https://health.ec.europa.eu/medical-devices-sector/new-")
        print("       regulations/guidance-mdcg-endorsed-documents-and-other-")
        print("       guidance_en\n")
        answers = run_eu_questionnaire(ask, ask_yes_no, change_info)
        result = assess_eu(answers, change_info)

    # Print result
    flag = "⚠️  중대한 변경 (Significant)" if result["isSignificant"] else "✅ 중대하지 않은 변경 (Not Significant)"
    print("\n  ┌─ 평가 결과 ─────────────────────────────────────────────────────┐")
    print(f"  │  국가/지역  : {country}")
    print(f"  │  판정       : {flag}")
    print(f"  │  필요 조치  : {result['requiredAction']}")
    print("  └────────────────────────────────────────────────────────────────┘")

    return {"country": country, "answers": answers, "result": result}


# ===== Step 4: Document Generation =====
def generate_documents(product_info: dict, change_info: dict, assessment_results: list) -> list:
    print_section("STEP 4. 인허가 문서 생성")

    non_sig = [r for r in assessment_results if not r["result"]["isSignificant"]]

    if not non_sig:
        print("\n  ⚠️  모든 국가에서 중대한 변경으로 판정되었습니다.")
        print("  → 별도 인허가 절차(신규 510(k) / Licence Amendment / NB Notification)가 필요합니다.")
        print("  → 본 도구는 중대하지 않은 변경에 대한 문서만 생성합니다.\n")
        return []

    if len(non_sig) < len(assessment_results):
        print("\n  ℹ️  일부 국가에서만 중대하지 않은 변경으로 판정되었습니다.")
        print("  → 중대하지 않은 변경에 대해서만 문서를 생성합니다.\n")

    print("\n  ▶ 제품 정보 확인")
    print(f"    모델명        : {product_info.get('modelName', '[N/A]')}")
    print(f"    제조사        : {product_info.get('manufacturer', '[N/A]')}")
    print(f"    제조사 주소   : {product_info.get('manufacturerAddress', '[N/A]')}")
    print(f"    FDA 510(k)    : {product_info.get('fdaK510', 'N/A')}")
    print(f"    HC Licence No.: {product_info.get('hcLicenceNo', 'N/A')}")
    print(f"    EU Cert No.   : {product_info.get('euCertNumber', 'N/A')}")
    if not ask_yes_no("\n  위 제품 정보로 문서를 생성하시겠습니까?"):
        print("  → 문서 생성을 취소했습니다. 제품 정보를 수정 후 다시 실행해 주세요.")
        return []

    print("\n  ▶ 문서 메타데이터 입력")
    metadata = {
        "docNumberPrefix": ask("  문서 번호 prefix (e.g., LTF-2026): ") or "DOC-2026",
        "revisionNo":      ask("  Revision No. (default: 00): ") or "00",
        "effectiveDate":   ask("  Effective Date (YYYY-MM-DD): ") or datetime.now().strftime("%Y-%m-%d"),
        "preparedBy":      ask("  작성자 (Prepared by): ") or "[Name]",
        "reviewedBy":      ask("  검토자 (Reviewed by): ") or "[Name]",
        "approvedBy":      ask("  승인자 (Approved by): ") or "[Name]",
    }

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    model_name = product_info.get("modelName", "Device").replace(" ", "_")

    generated = []
    for item in non_sig:
        country = item["country"]
        result = item["result"]

        doc_meta = dict(metadata)
        doc_meta["docNumber"] = f"{metadata['docNumberPrefix']}-{country}-{datetime.now().strftime('%H%M%S')}"

        if country == "FDA":
            doc = build_fda_document(product_info, change_info, result, doc_meta)
            filename = f"FDA_non-signification_{model_name}.docx"
        elif country == "HC":
            doc = build_hc_document(product_info, change_info, result, doc_meta)
            filename = f"HC_non-signification_{model_name}.docx"
        elif country == "EU":
            doc = build_eu_document(product_info, change_info, result, doc_meta)
            filename = f"EU_non-signification_{model_name}.docx"

        out_path = output_dir / filename
        doc.save(str(out_path))
        generated.append(str(out_path))

        print(f"  ✅ {country} 문서 생성 완료: {filename}")

    return generated


# ===== Main =====
def main():
    print_banner()

    try:
        product_info = gather_product_info()
        change_info = gather_change_info()
        countries = select_countries()

        assessment_results = []
        for country in countries:
            result = run_assessment(country, product_info, change_info)
            assessment_results.append(result)

        # Summary
        print_section("평가 결과 요약")
        print()
        print("  ┌──────┬──────────────────────────────┬─────────────────────────────┐")
        print("  │ 국가 │ 판정                         │ 필요 조치                    │")
        print("  ├──────┼──────────────────────────────┼─────────────────────────────┤")
        for r in assessment_results:
            flag = "⚠️  Significant         " if r["result"]["isSignificant"] else "✅ Not Significant      "
            country_pad = r["country"].ljust(4)
            action_pad = r["result"]["requiredAction"][:27].ljust(27)
            print(f"  │ {country_pad} │ {flag.ljust(28)} │ {action_pad} │")
        print("  └──────┴──────────────────────────────┴─────────────────────────────┘")

        generated = generate_documents(product_info, change_info, assessment_results)

        if generated:
            print("\n" + "═" * 72)
            print(f"  🎉 작업 완료! 총 {len(generated)}개 문서가 생성되었습니다.")
            print("═" * 72)
            for f in generated:
                print(f"     📄 {f}")
            print()

    except KeyboardInterrupt:
        print("\n\n  ⚠️  사용자가 작업을 취소했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


# ===== Config-based Auto Run =====
def run_from_config(config_path: str, auto_confirm: bool = False):
    print_banner()
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    print(f"📋 Config 모드 실행: {config_path}\n")

    product_info = config["productInfo"]
    change_info = config["changeInfo"]
    countries = config["countries"]
    metadata = config["metadata"]
    auto_answers = config["autoAnswers"]

    assessment_results = []
    for country in countries:
        ans = auto_answers.get(country, {})
        if country == "FDA":
            result = assess_fda(ans, change_info)
        elif country == "HC":
            result = assess_hc(ans, change_info)
        elif country == "EU":
            result = assess_eu(ans, change_info)

        flag = "⚠️  Significant" if result["isSignificant"] else "✅ Not Significant"
        print(f"  [{country}] {flag} - {result['requiredAction']}")
        assessment_results.append({"country": country, "answers": ans, "result": result})

    non_sig = [r for r in assessment_results if not r["result"]["isSignificant"]]

    print("\n  ▶ 제품 정보 확인")
    print(f"    모델명        : {product_info.get('modelName', '[N/A]')}")
    print(f"    제조사        : {product_info.get('manufacturer', '[N/A]')}")
    print(f"    제조사 주소   : {product_info.get('manufacturerAddress', '[N/A]')}")
    print(f"    FDA 510(k)    : {product_info.get('fdaK510', 'N/A')}")
    print(f"    HC Licence No.: {product_info.get('hcLicenceNo', 'N/A')}")
    print(f"    EU Cert No.   : {product_info.get('euCertNumber', 'N/A')}")
    if auto_confirm:
        print("\n  → 제품 정보 확인 완료. 문서 생성을 진행합니다.")
    else:
        confirm = input("\n  위 제품 정보로 문서를 생성하시겠습니까? (y/n): ").strip().lower()
        if confirm not in ("y", "yes"):
            print("  → 문서 생성을 취소했습니다. config 파일의 productInfo를 수정 후 다시 실행해 주세요.")
            return []

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    model_name = product_info.get("modelName", "Device").replace(" ", "_")

    generated = []
    for item in non_sig:
        country = item["country"]
        result = item["result"]
        doc_meta = dict(metadata)
        doc_meta["docNumber"] = f"{metadata['docNumberPrefix']}-{country}-{datetime.now().strftime('%H%M%S')}"

        if country == "FDA":
            doc = build_fda_document(product_info, change_info, result, doc_meta)
            filename = f"FDA_non-signification_{model_name}.docx"
        elif country == "HC":
            doc = build_hc_document(product_info, change_info, result, doc_meta)
            filename = f"HC_non-signification_{model_name}.docx"
        elif country == "EU":
            doc = build_eu_document(product_info, change_info, result, doc_meta)
            filename = f"EU_non-signification_{model_name}.docx"

        out_path = output_dir / filename
        doc.save(str(out_path))
        generated.append(str(out_path))
        print(f"  ✅ Generated: {filename}")

    print(f"\n🎉 {len(generated)}개 문서 생성 완료\n")
    return generated


# ===== Entry =====
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "--config":
        auto_yes = "--yes" in args or "-y" in args
        run_from_config(args[1], auto_confirm=auto_yes)
    elif args and args[0] in ("--help", "-h"):
        print("""
사용법:
  python main.py                       # 대화형 모드
  python main.py --config <file.json>  # Config 파일 기반 자동 실행
  python main.py --help                # 도움말
""")
    else:
        main()
