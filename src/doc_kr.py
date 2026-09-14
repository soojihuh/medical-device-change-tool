"""
국내(식약처/MFDS) 변경사항 검토서 문서 생성 (Python).
"의료기기 허가·신고·심사 등에 관한 규정" [별표 3]/[별표 4]에 따른 경미한 변경사항 판단 근거를
정리한 내부 검토기록. 이 도구는 "경미한 변경 대상"(즉시보고/연차보고)으로 판정된 건에 대해서만
문서를 생성한다 — 변경허가·인증, 임상자료심사, 신규 허가 대상은 별도 인허가 절차가 필요하다.
"""
from doc_common import init_document, add_paragraph, add_spacer, add_page_break, add_info_table

KR_GUIDANCE_TITLE = "의료기기 허가·신고·심사 등에 관한 규정 [별표 3]/[별표 4] (제19조 관련)"


def _qa_line(doc, text: str, answer):
    add_paragraph(doc, text, after_pt=2)
    add_paragraph(doc, f"→ {'예' if answer else '아니오'}", after_pt=10)


def build_kr_document(product_info: dict, change_info: dict,
                      assessment: dict, metadata: dict):
    """국내 경미한 변경사항 검토서 생성"""
    doc = init_document()

    add_paragraph(doc, "국내 의료기기 변경사항 검토서 (경미한 변경사항 판단)", bold=True)
    add_spacer(doc)

    add_paragraph(doc, "1) 대상 제품", bold=True)
    add_paragraph(doc, f"- {product_info.get('krPermitNo', 'N/A')} ({product_info.get('modelName', '[모델명]')})")
    add_paragraph(doc, f"- 검토일: {metadata.get('effectiveDate', '[YYYY-MM-DD]')}")
    add_spacer(doc)

    add_paragraph(doc, "2) 변경 사항", bold=True)
    add_paragraph(doc, "(1) 변경 전 항목", bold=True)
    add_paragraph(doc, change_info.get("componentName", ""), bold=True)
    add_info_table(doc, [("변경 전", change_info.get("beforeValue", ""))])
    add_spacer(doc)

    add_paragraph(doc, "(2) 변경 후 항목", bold=True)
    add_paragraph(doc, change_info.get("componentName", ""), bold=True)
    add_info_table(doc, [("변경 후", change_info.get("afterValue", ""))])
    add_spacer(doc)
    add_paragraph(doc, change_info.get("description") or change_info.get("changeTitle", ""))
    add_spacer(doc)

    add_paragraph(doc, "(3) 변경 사유", bold=True)
    add_paragraph(doc, change_info.get("reason", "[변경 사유]"))

    add_page_break(doc)

    # ===== 판단 근거 =====
    add_paragraph(doc, f"{KR_GUIDANCE_TITLE}에 따른 변경대상 판단 결과", bold=True)
    add_spacer(doc)

    add_paragraph(doc, "- 판단 흐름", bold=True)
    for q in assessment["path"]:
        if q["answer"] is None:
            continue
        _qa_line(doc, f"{q['id']}: {q['text']}", q["answer"])

    add_spacer(doc)
    result_label = assessment.get("requiredAction", "")
    add_paragraph(doc, f"결론: {result_label}")
    add_spacer(doc)
    add_paragraph(doc, assessment.get("summary", ""), bold=True)
    add_spacer(doc)
    add_spacer(doc)

    add_paragraph(doc, "서명", bold=True)
    add_info_table(doc, [
        ("작성자", metadata.get("preparedBy", "")),
        ("검토자", metadata.get("reviewedBy", "")),
        ("승인자", metadata.get("approvedBy", "")),
    ])

    return doc
