#!/usr/bin/env python3
"""
Medical Device Change Assessment & Documentation Tool - Web Portal

main.py의 CLI 대화형 흐름을 웹 폼으로 옮긴 버전.
평가/문서 생성 로직(src/assessor_*.py, src/doc_*.py)은 수정 없이 그대로 재사용한다.

실행:
    streamlit run app.py
"""

import sys
from pathlib import Path
from io import BytesIO
from datetime import datetime

import streamlit as st
from deep_translator import GoogleTranslator

sys.path.insert(0, str(Path(__file__).parent / "src"))

from assessor_fda import assess_fda
from assessor_hc import assess_hc
from assessor_eu import assess_eu
from doc_fda import build_fda_document
from doc_hc import build_hc_document
from doc_eu import build_eu_document


st.set_page_config(page_title="의료기기 변경 평가 도구", page_icon="🏥", layout="wide")

st.title("🏥 의료기기 변경 평가 및 인허가 문서 자동 생성 도구")
st.caption("FDA / Health Canada / EU MDR 가이던스 기반 변경 중대성 평가")

CATEGORY_MAP = {
    "Labeling / Nomenclature (라벨링 / 명칭)": "labeling",
    "Design / Hardware (설계 / 하드웨어)": "design",
    "Software / Firmware (소프트웨어 / 펌웨어)": "software",
    "Materials (재료)": "material",
    "Manufacturing Process (제조 공정)": "manufacturing",
    "Performance Spec (성능 사양)": "performance",
    "Intended Use (사용 목적)": "intended_use",
    "Sterilization (멸균)": "sterilization",
    "Other": "other",
}

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def sequential_yesno(items, prefix):
    """
    items: [{"key": str, "text": str, "header": str}, ...]
    각 문항을 예/아니오로 하나씩 순서대로 보여주고, 답변이 되어야
    (Yes든 No든) 다음 문항이 나타난다. 아직 답하지 않은 문항 이후는 렌더링하지 않는다.
    Returns: {key: True|False|None}
    """
    answers = {}
    last_header = None
    for item in items:
        header = item.get("header")
        if header and header != last_header:
            st.markdown(f"**{header}**")
            last_header = header

        state_key = f"{prefix}_{item['key']}"
        choice = st.radio(
            item["text"],
            ("예 (Yes)", "아니오 (No)"),
            index=None,
            key=state_key,
            horizontal=True,
        )
        answers[item["key"]] = None if choice is None else choice.startswith("예")

        if answers[item["key"]] is None:
            break

    return answers


def progress_caption(answers, required_keys):
    answered = sum(1 for k in required_keys if answers.get(k) is not None)
    st.caption(f"진행 상황: {answered} / {len(required_keys)} 문항 답변 완료")


def translate_ko_to_en(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    return GoogleTranslator(source="ko", target="en").translate(text)


# ===== 1. Product Info =====
st.header("1. 제품 정보")
c1, c2 = st.columns(2)
with c1:
    model_name = st.text_input("모델명 (Model Name)")
    device_class = st.text_input("의료기기 등급", value="Class II / IIb")
    manufacturer = st.text_input("제조사 (Legal Manufacturer)", value="Ray Co., Ltd.")
    manufacturer_address = st.text_input(
        "제조사 주소",
        value="1F~3F, 4F(Part), 5F, 265 Daeji-ro, Suji-gu, Yongin-si, Gyeonggi-do, Republic of Korea, 16882",
    )
with c2:
    fda_k510 = st.text_input("FDA 510(k) Number", value="N/A")
    fda_product_code = st.text_input("FDA Product Code", value="N/A")
    fda_regulation_number = st.text_input("FDA Regulation Number", value="N/A")
    hc_licence_no = st.text_input("Health Canada Licence No.", value="N/A")
    eu_cert_number = st.text_input("EU NB Certificate Number", value="N/A")
    eu_notified_body = st.text_input("EU Notified Body", value="N/A")
    eu_basic_udi_di = st.text_input("EU Basic UDI-DI", value="N/A")

product_info = {
    "modelName": model_name,
    "deviceClass": device_class,
    "manufacturer": manufacturer,
    "manufacturerAddress": manufacturer_address,
    "fdaK510": fda_k510,
    "fdaProductCode": fda_product_code,
    "fdaRegulationNumber": fda_regulation_number,
    "hcLicenceNo": hc_licence_no,
    "euCertNumber": eu_cert_number,
    "euNotifiedBody": eu_notified_body,
    "euBasicUDIDI": eu_basic_udi_di,
}

# ===== 2. Change Info =====
st.header("2. 변경 사항 입력")
category_label = st.selectbox("변경 카테고리", list(CATEGORY_MAP.keys()))
component_name = st.text_input("변경 대상 구성품 (e.g., Detector, PCB, Sensor)")
change_title = st.text_input("변경 사항 한줄 요약")
c3, c4 = st.columns(2)
with c3:
    before_value = st.text_area("변경 전 (Before)")
with c4:
    after_value = st.text_area("변경 후 (After)")
reason = st.text_area("변경 사유 (Reason)")
description = st.text_area("변경 상세 설명 (Description)")

EN_FIELD_KEYS = ["en_componentName", "en_changeTitle", "en_beforeValue", "en_afterValue", "en_reason", "en_description"]

if st.button("🌐 한→ 영 번역"):
    try:
        st.session_state["change_info_en"] = {
            "componentName": translate_ko_to_en(component_name),
            "changeTitle": translate_ko_to_en(change_title),
            "beforeValue": translate_ko_to_en(before_value),
            "afterValue": translate_ko_to_en(after_value),
            "reason": translate_ko_to_en(reason),
            "description": translate_ko_to_en(description),
        }
        # 위젯 키가 이미 있으면 새 번역 결과가 반영되지 않으므로(값이 고정됨) 초기화한다
        for k in EN_FIELD_KEYS:
            st.session_state.pop(k, None)
    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {e}")

use_english = False
if "change_info_en" in st.session_state:
    st.markdown("**번역 결과 (영문 — 검토 후 필요하면 직접 수정 가능)**")
    en = st.session_state["change_info_en"]
    en["componentName"] = st.text_input("Component (English)", value=en["componentName"], key="en_componentName")
    en["changeTitle"] = st.text_input("Change Summary (English)", value=en["changeTitle"], key="en_changeTitle")
    ec1, ec2 = st.columns(2)
    with ec1:
        en["beforeValue"] = st.text_area("Before (English)", value=en["beforeValue"], key="en_beforeValue")
    with ec2:
        en["afterValue"] = st.text_area("After (English)", value=en["afterValue"], key="en_afterValue")
    en["reason"] = st.text_area("Reason (English)", value=en["reason"], key="en_reason")
    en["description"] = st.text_area("Description (English)", value=en["description"], key="en_description")
    st.session_state["change_info_en"] = en

    use_english = st.checkbox("평가 실행 및 문서 생성에 이 영문 번역본 사용", value=True, key="use_english_toggle")

if use_english:
    _c = st.session_state["change_info_en"]
    change_info = {
        "category": CATEGORY_MAP[category_label],
        "componentName": _c["componentName"],
        "changeTitle": _c["changeTitle"],
        "beforeValue": _c["beforeValue"],
        "afterValue": _c["afterValue"],
        "reason": _c["reason"],
        "description": _c["description"],
    }
else:
    change_info = {
        "category": CATEGORY_MAP[category_label],
        "componentName": component_name,
        "changeTitle": change_title,
        "beforeValue": before_value,
        "afterValue": after_value,
        "reason": reason,
        "description": description,
    }

# ===== 3. Country Selection =====
st.header("3. 평가 대상 국가 선택")
countries = st.multiselect(
    "평가할 국가/지역을 선택하세요 (복수 선택 가능)",
    ["FDA", "HC", "EU"],
    default=["FDA", "HC", "EU"],
)

# ===== 4. Per-country Questionnaires =====
st.header("4. 국가별 가이던스 기반 중대성 평가")
answers_by_country = {}

FDA_ITEMS = [
    {"key": "A1", "header": "Flowchart A: Labeling Changes", "text": "A1. 의도된 용도(Indications for Use) 변경이 있습니까?"},
    {"key": "A2", "header": "Flowchart A: Labeling Changes", "text": "A2. 금기사항(Contraindication) 추가/수정이 있습니까?"},
    {"key": "A3", "header": "Flowchart A: Labeling Changes", "text": "A3. 경고/주의/이상반응 표기에 새로운 정보가 추가됩니까?"},
    {"key": "A4", "header": "Flowchart A: Labeling Changes", "text": "A4. 라벨 변경이 임상적 기능/성능에 영향을 줄 수 있습니까?"},
    {"key": "B1", "header": "Flowchart B: Technology / Engineering / Performance", "text": "B1. 작동 원리(Operating Principle) 변경이 있습니까?"},
    {"key": "B2", "header": "Flowchart B: Technology / Engineering / Performance", "text": "B2. 에너지 유형(Energy Type) 변경이 있습니까?"},
    {"key": "B3", "header": "Flowchart B: Technology / Engineering / Performance", "text": "B3. 환경 사양(Environmental Spec) 변경이 있습니까?"},
    {"key": "B4", "header": "Flowchart B: Technology / Engineering / Performance", "text": "B4. 사용 인터페이스(Use of Device) 변경이 있습니까?"},
    {"key": "B5", "header": "Flowchart B: Technology / Engineering / Performance", "text": "B5. 설계 / 구성품 / 사양 변경이 있습니까? (단순 명칭 변경은 제외)"},
    {"key": "B6", "header": "Flowchart B: Technology / Engineering / Performance", "text": "B6. 멸균/포장/유효기간 변경이 있습니까?"},
    {"key": "B7", "header": "Flowchart B: Technology / Engineering / Performance", "text": "B7. 변경이 성능 사양에 중대한 영향을 미칠 수 있습니까?"},
    {"key": "C1", "header": "Flowchart C: Materials", "text": "C1. 환자/사용자와 접촉하는 재료가 변경되었습니까?"},
    {"key": "C2", "header": "Flowchart C: Materials", "text": "C2. 재료 변경이 생체적합성에 영향을 줄 수 있습니까?"},
]
FDA_KEYS = [it["key"] for it in FDA_ITEMS]

if "FDA" in countries:
    with st.expander("🇺🇸 FDA — Deciding When to Submit a 510(k) for a Change to an Existing Device (Oct 2017)", expanded=True):
        fda_answers = sequential_yesno(FDA_ITEMS, prefix="fda")
        progress_caption(fda_answers, FDA_KEYS)

    answers_by_country["FDA"] = fda_answers

HC_ITEMS = [
    {"key": "a1", "header": "(a) Manufacturing Process / Facility / Equipment", "text": "a1. 제조 공정 변경이 있습니까?"},
    {"key": "a2", "header": "(a) Manufacturing Process / Facility / Equipment", "text": "a2. 제조 시설(facility) 변경이 있습니까?"},
    {"key": "a3", "header": "(a) Manufacturing Process / Facility / Equipment", "text": "a3. 주요 제조 장비(equipment) 변경이 있습니까?"},
    {"key": "b1", "header": "(b) Manufacturing Quality Control", "text": "b1. QC 절차 또는 시험 방법 변경이 있습니까?"},
    {"key": "b2", "header": "(b) Manufacturing Quality Control", "text": "b2. 합격 기준(acceptance criteria) 변경이 있습니까?"},
    {"key": "c1", "header": "(c) Design / Performance / Material / Energy / Software", "text": "c1. 설계 변경이 있습니까? (단순 명칭 변경은 제외)"},
    {"key": "c2", "header": "(c) Design / Performance / Material / Energy / Software", "text": "c2. 성능 사양(performance specification) 변경이 있습니까?"},
    {"key": "c3", "header": "(c) Design / Performance / Material / Energy / Software", "text": "c3. 환자 접촉 재료 변경이 있습니까?"},
    {"key": "c4", "header": "(c) Design / Performance / Material / Energy / Software", "text": "c4. 에너지원(energy source) 변경이 있습니까?"},
    {"key": "c5", "header": "(c) Design / Performance / Material / Energy / Software", "text": "c5. 소프트웨어 변경이 있습니까? (사이버보안 패치 등 minor 제외)"},
    {"key": "c6", "header": "(c) Design / Performance / Material / Energy / Software", "text": "c6. 액세서리 추가/변경이 있습니까?"},
    {"key": "d1", "header": "(d) Intended Use", "text": "d1. 사용 목적(intended use) 확장 또는 변경이 있습니까?"},
    {"key": "d2", "header": "(d) Intended Use", "text": "d2. 금기사항(contraindication) 추가/삭제가 있습니까?"},
    {"key": "d3", "header": "(d) Intended Use", "text": "d3. 환자군(patient population) 변경이 있습니까?"},
    {"key": "d4", "header": "(d) Intended Use", "text": "d4. 사용 기간(period of use) 변경이 있습니까?"},
]
HC_KEYS = [it["key"] for it in HC_ITEMS]

if "HC" in countries:
    with st.expander("🇨🇦 Health Canada — Guidance on the Interpretation of Significant Change (Types of Changes)", expanded=True):
        hc_answers = sequential_yesno(HC_ITEMS, prefix="hc")
        progress_caption(hc_answers, HC_KEYS)

    answers_by_country["HC"] = hc_answers

EU_BASE_ITEMS = [
    {"key": "A1", "header": "Chart A: Design / Performance Specification", "text": "A.01. 설계 또는 성능 사양에 변경이 있고 사용 목적에 영향을 줍니까?"},
    {"key": "A2", "header": "Chart A: Design / Performance Specification", "text": "A.02. 작동 원리(operating principle) 변경이 있습니까?"},
    {"key": "A3", "header": "Chart A: Design / Performance Specification", "text": "A.03. 에너지원(source of energy) 변경이 있습니까?"},
    {"key": "A4", "header": "Chart A: Design / Performance Specification", "text": "A.04. 알고리즘 또는 알람 변경이 있습니까?"},
    {"key": "A5", "header": "Chart A: Design / Performance Specification", "text": "A.05. 사용자 인터페이스 / 인체공학 / 전달 방식 변경이 있습니까?"},
    {"key": "A6", "header": "Chart A: Design / Performance Specification", "text": "A.06. 성능 또는 기능 변경이 있습니까?"},
    {"key": "B1", "header": "Chart B: Intended Purpose", "text": "B.01. 사용 목적이 확장 또는 제한되었습니까?"},
    {"key": "B2", "header": "Chart B: Intended Purpose", "text": "B.02. 적응증 / 금기 / 환자군 / 사용자 변경이 있습니까?"},
    {"key": "C1", "header": "Chart C: Software", "text": "C.01. OS / 아키텍처 / DB 구조에 신규 또는 주요 변경이 있습니까?"},
    {"key": "C2", "header": "Chart C: Software", "text": "C.02. 신규 진단/치료 기능, 신규 사용자 상호작용, 의료 목적 변경이 있습니까?"},
    {"key": "C3", "header": "Chart C: Software", "text": "C.03. 진단 정보의 해석에 영향을 주는 변경이 있습니까?"},
    {"key": "D1", "header": "Chart D: Substance / Material", "text": "D.01. 인체 조직/체액 접촉 재료/물질 변경이 있습니까?"},
    {"key": "D2", "header": "Chart D: Substance / Material", "text": "D.02. 핵심 구성품 또는 재료의 공급사(supplier) 변경이 있습니까? (단순 명칭 변경은 제외)"},
    {"key": "E_applicable", "header": "Chart E: Sterilisation", "text": "E.00. 본 장비가 멸균 의료기기입니까?"},
]
EU_STERILE_ITEMS = [
    {"key": "E1", "header": "Chart E: Sterilisation", "text": "E.01. 멸균 방법 변경이 있습니까?"},
    {"key": "E2", "header": "Chart E: Sterilisation", "text": "E.02. 포장 / 멸균 배리어 시스템 변경이 있습니까?"},
]

if "EU" in countries:
    with st.expander("🇪🇺 EU MDR — MDCG 2020-3 Rev.1 (Article 120 MDR)", expanded=True):
        raw_e_applicable = st.session_state.get("eu_E_applicable")
        e_applicable_val = None if raw_e_applicable is None else raw_e_applicable.startswith("예")

        eu_items = list(EU_BASE_ITEMS)
        eu_required_keys = [it["key"] for it in EU_BASE_ITEMS]
        if e_applicable_val is True:
            eu_items += EU_STERILE_ITEMS
            eu_required_keys += [it["key"] for it in EU_STERILE_ITEMS]

        eu_answers = sequential_yesno(eu_items, prefix="eu")

        if e_applicable_val is False:
            eu_answers["E1"] = False
            eu_answers["E2"] = False
            st.caption("→ 비멸균 장비이므로 Chart E는 N/A")

        progress_caption(eu_answers, eu_required_keys)

    answers_by_country["EU"] = eu_answers

# ===== 5. Run Assessment =====
st.header("5. 평가 실행")

required_keys_by_country = {}
if "FDA" in countries:
    required_keys_by_country["FDA"] = FDA_KEYS
if "HC" in countries:
    required_keys_by_country["HC"] = HC_KEYS
if "EU" in countries:
    required_keys_by_country["EU"] = eu_required_keys

incomplete_countries = [
    c for c in countries
    if any(answers_by_country[c].get(k) is None for k in required_keys_by_country[c])
]
all_ready = bool(countries) and not incomplete_countries

if not countries:
    st.warning("최소 1개 국가를 선택해야 평가를 실행할 수 있습니다.")
elif incomplete_countries:
    st.info(f"{', '.join(incomplete_countries)} 질문에 아직 답변하지 않은 문항이 있습니다. 위에서 모든 문항에 답하면 평가를 실행할 수 있습니다.")

if st.button("▶ 평가 실행", type="primary", disabled=not all_ready):
    results = []
    for country in countries:
        answers = answers_by_country[country]
        if country == "FDA":
            result = assess_fda(answers, change_info)
        elif country == "HC":
            result = assess_hc(answers, change_info)
        elif country == "EU":
            result = assess_eu(answers, change_info)
        results.append({"country": country, "answers": answers, "result": result})

    st.session_state["assessment_results"] = results
    st.session_state["product_info"] = product_info
    st.session_state["change_info"] = change_info
    st.session_state.pop("generated_files", None)

if "assessment_results" in st.session_state:
    results = st.session_state["assessment_results"]

    st.subheader("평가 결과 요약")
    for r in results:
        result = r["result"]
        if result["isSignificant"]:
            st.error(f"⚠️ **{r['country']}** — Significant (중대한 변경) → {result['requiredAction']}")
        else:
            st.success(f"✅ **{r['country']}** — Not Significant (중대하지 않은 변경) → {result['requiredAction']}")
        with st.expander(f"{r['country']} 상세 내역"):
            st.write(result["summary"])

    non_sig = [r for r in results if not r["result"]["isSignificant"]]

    # ===== 6. Document Generation =====
    if non_sig:
        st.header("6. 인허가 문서 생성")
        st.info(f"{len(non_sig)}개 국가({', '.join(r['country'] for r in non_sig)})에서 중대하지 않은 변경으로 판정되어 문서를 생성할 수 있습니다.")

        with st.form("doc_meta_form"):
            doc_number_prefix = st.text_input("문서 번호 prefix (e.g., LTF-2026)", value="DOC-2026")
            revision_no = st.text_input("Revision No.", value="00")
            effective_date = st.text_input("Effective Date (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"))
            prepared_by = st.text_input("작성자 (Prepared by)", value="[Name]")
            reviewed_by = st.text_input("검토자 (Reviewed by)", value="[Name]")
            approved_by = st.text_input("승인자 (Approved by)", value="[Name]")
            generate_clicked = st.form_submit_button("📄 문서 생성")

        if generate_clicked:
            metadata = {
                "docNumberPrefix": doc_number_prefix,
                "revisionNo": revision_no,
                "effectiveDate": effective_date,
                "preparedBy": prepared_by,
                "reviewedBy": reviewed_by,
                "approvedBy": approved_by,
            }
            saved_product_info = st.session_state["product_info"]
            saved_change_info = st.session_state["change_info"]
            model_name_safe = (saved_product_info.get("modelName") or "Device").replace(" ", "_")

            generated_files = {}
            for item in non_sig:
                country = item["country"]
                result = item["result"]
                doc_meta = dict(metadata)
                doc_meta["docNumber"] = f"{metadata['docNumberPrefix']}-{country}-{datetime.now().strftime('%H%M%S')}"

                if country == "FDA":
                    doc = build_fda_document(saved_product_info, saved_change_info, result, doc_meta)
                    filename = f"FDA_non-signification_{model_name_safe}.docx"
                elif country == "HC":
                    doc = build_hc_document(saved_product_info, saved_change_info, result, doc_meta)
                    filename = f"HC_non-signification_{model_name_safe}.docx"
                elif country == "EU":
                    doc = build_eu_document(saved_product_info, saved_change_info, result, doc_meta)
                    filename = f"EU_non-signification_{model_name_safe}.docx"

                buf = BytesIO()
                doc.save(buf)
                generated_files[filename] = buf.getvalue()

            st.session_state["generated_files"] = generated_files

    else:
        st.warning("모든 선택 국가에서 중대한 변경으로 판정되어, 본 도구는 문서를 생성하지 않습니다. 별도 인허가 절차(신규 510(k) / Licence Amendment / NB Notification)가 필요합니다.")

if "generated_files" in st.session_state and st.session_state["generated_files"]:
    st.subheader("생성된 문서 다운로드")
    for filename, data in st.session_state["generated_files"].items():
        st.download_button(
            label=f"⬇ {filename}",
            data=data,
            file_name=filename,
            mime=DOCX_MIME,
            key=f"dl_{filename}",
        )
