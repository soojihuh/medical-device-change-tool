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

from assessor_fda import assess_fda, FDA_GRAPH, FDA_MAIN_ITEMS, CHART_ENTRY as FDA_CHART_ENTRY
from assessor_hc import assess_hc, HC_GRAPH, HC_MAIN_ITEMS, CHART_ENTRY as HC_CHART_ENTRY
from assessor_eu import assess_eu, EU_GRAPH, EU_MAIN_ITEMS, CHART_ENTRY as EU_CHART_ENTRY
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


def render_graph_node(graph, node_id, prefix, rendered):
    """분기형 그래프(FDA_GRAPH/EU_GRAPH)의 한 노드를 렌더링(또는 이미 렌더링됐으면 재사용)한다.
    같은 노드가 서로 다른 플로우차트에서 공유될 수 있어(예: FDA의 B5, C5->B5 리다이렉트),
    한 실행(run) 안에서 위젯이 두 번 생성되지 않도록 rendered(set)로 중복을 막는다."""
    state_key = f"{prefix}_{node_id.replace('.', '_')}"
    if state_key in rendered:
        raw = st.session_state.get(state_key)
    else:
        node = graph[node_id]
        raw = st.radio(f"{node_id}. {node['text']}", ("예 (Yes)", "아니오 (No)"), index=None, key=state_key)
        rendered.add(state_key)
    return None if raw is None else raw.startswith("예")


def walk_graph_ui(graph, start_id, prefix, rendered):
    """그래프의 키에 없는 노드 id는 종결 상태(terminal)로 취급한다."""
    path = []
    node_id = start_id
    while node_id in graph:
        node = graph[node_id]
        ans = render_graph_node(graph, node_id, prefix, rendered)
        path.append({"id": node_id, "text": node["text"], "answer": ans})
        if ans is None:
            return path, None
        node_id = node["yes"] if ans else node["no"]
    return path, node_id


def translate_ko_to_en(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    result = GoogleTranslator(source="ko", target="en").translate(text)
    if not result or not result.strip():
        raise RuntimeError(
            "번역 서비스가 빈 응답을 반환했습니다. 배포 환경의 네트워크가 "
            "번역 서비스 접속을 차단하고 있을 수 있습니다."
        )
    return result


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

FDA_CHART_LABELS = {
    "MAIN2": "Flowchart A: Labeling Changes",
    "MAIN3": "Flowchart B: Technology, Engineering, and Performance Changes",
    "MAIN4": "Flowchart C: Materials Changes",
}
completeness_by_country = {}

if "FDA" in countries:
    with st.expander("🇺🇸 FDA — Deciding When to Submit a 510(k) for a Change to an Existing Device (Oct 2017)", expanded=True):
        fda_answers = {}
        fda_complete = False
        rendered_fda_nodes = set()

        st.markdown("**Main Flowchart**")
        main1_key = f"fda_{FDA_MAIN_ITEMS[0]['key']}"
        main1_choice = st.radio(f"MAIN1. {FDA_MAIN_ITEMS[0]['text']}", ("예 (Yes)", "아니오 (No)"), index=None, key=main1_key)
        fda_answers["MAIN1"] = None if main1_choice is None else main1_choice.startswith("예")

        if fda_answers["MAIN1"] is True:
            fda_complete = True
        elif fda_answers["MAIN1"] is False:
            charts_complete = True
            for item in FDA_MAIN_ITEMS[1:]:
                main_key = item["key"]
                choice = st.radio(f"{main_key}. {item['text']}", ("예 (Yes)", "아니오 (No)"), index=None, key=f"fda_{main_key}")
                gate = None if choice is None else choice.startswith("예")
                fda_answers[main_key] = gate

                if gate is None:
                    charts_complete = False
                    continue
                if gate:
                    entry_node, _label = FDA_CHART_ENTRY[main_key]
                    st.markdown(f"**{FDA_CHART_LABELS[main_key]}**")
                    path, outcome = walk_graph_ui(FDA_GRAPH, entry_node, "fda", rendered_fda_nodes)
                    for p in path:
                        fda_answers[p["id"]] = p["answer"]
                    if outcome is None:
                        charts_complete = False
            fda_complete = charts_complete

        st.caption(f"진행 상황: {'답변 완료' if fda_complete else '답변 진행 중'}")

    answers_by_country["FDA"] = fda_answers
    completeness_by_country["FDA"] = fda_complete

if "HC" in countries:
    with st.expander("🇨🇦 Health Canada — Guidance on how to interpret \"significant change\": Types of changes", expanded=True):
        hc_answers = {}
        rendered_hc_nodes = set()
        charts_complete = True

        for item in HC_MAIN_ITEMS:
            main_key = item["key"]
            choice = st.radio(f"{main_key}. {item['text']}", ("예 (Yes)", "아니오 (No)"), index=None, key=f"hc_{main_key}")
            gate = None if choice is None else choice.startswith("예")
            hc_answers[main_key] = gate

            if gate is None:
                charts_complete = False
                continue
            if gate:
                entry_node, chart_name = HC_CHART_ENTRY[main_key]
                st.markdown(f"**{chart_name}**")
                path, outcome = walk_graph_ui(HC_GRAPH, entry_node, "hc", rendered_hc_nodes)
                for p in path:
                    hc_answers[p["id"]] = p["answer"]
                if outcome is None:
                    charts_complete = False
        hc_complete = charts_complete

        st.caption(f"진행 상황: {'답변 완료' if hc_complete else '답변 진행 중'}")

    answers_by_country["HC"] = hc_answers
    completeness_by_country["HC"] = hc_complete

if "EU" in countries:
    with st.expander("🇪🇺 EU MDR — MDCG 2020-3 Rev.1 (Article 120 MDR)", expanded=True):
        eu_answers = {}
        eu_complete = False
        rendered_eu_nodes = set()

        st.markdown("**Main Chart**")
        main0_choice = st.radio(f"MAIN0. {EU_MAIN_ITEMS[0]['text']}", ("예 (Yes)", "아니오 (No)"), index=None, key="eu_MAIN0")
        eu_answers["MAIN0"] = None if main0_choice is None else main0_choice.startswith("예")

        if eu_answers["MAIN0"] is True:
            eu_complete = True
        elif eu_answers["MAIN0"] is False:
            charts_complete = True
            for item in EU_MAIN_ITEMS[1:]:
                main_key = item["key"]
                choice = st.radio(f"{main_key}. {item['text']}", ("예 (Yes)", "아니오 (No)"), index=None, key=f"eu_{main_key}")
                gate = None if choice is None else choice.startswith("예")
                eu_answers[main_key] = gate

                if gate is None:
                    charts_complete = False
                    continue
                if gate:
                    entry_node, chart_name = EU_CHART_ENTRY[main_key]
                    st.markdown(f"**{chart_name}**")
                    path, outcome = walk_graph_ui(EU_GRAPH, entry_node, "eu", rendered_eu_nodes)
                    for p in path:
                        eu_answers[p["id"]] = p["answer"]
                    if outcome is None:
                        charts_complete = False
            eu_complete = charts_complete

        st.caption(f"진행 상황: {'답변 완료' if eu_complete else '답변 진행 중'}")

    answers_by_country["EU"] = eu_answers
    completeness_by_country["EU"] = eu_complete

# ===== 5. Run Assessment =====
st.header("5. 평가 실행")

incomplete_countries = [c for c in countries if not completeness_by_country.get(c, False)]
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
        if result.get("manualReviewRequired"):
            st.warning(f"🔍 **{r['country']}** — 수동 검토 필요 → {result['requiredAction']}")
        elif result["isSignificant"]:
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
