"""
FDA 510(k) change review document builder (Python).
Lean format matching the company's actual "Review of changes to 510(k)" template
(no cover page / TOC / revision history — just the change details and the
flowchart-based review results, in English for submission).
"""
from doc_common import init_document, add_paragraph, add_spacer, add_page_break, add_info_table

FDA_GUIDANCE_TITLE = "Deciding when to Submit a 510(k) for a change to an Existing Device"

# Which MAIN-chart gate leads into which lettered chart, for the "(Go to Chart X)" note.
CHART_LETTER = {"MAIN2": "A", "MAIN3": "B", "MAIN4": "C"}


def _qa_line(doc, text_en: str, answer, suffix: str = ""):
    add_paragraph(doc, text_en, after_pt=2)
    arrow = "YES" if answer else "NO"
    add_paragraph(doc, f"→ {arrow}{suffix}", after_pt=10)


def build_fda_document(product_info: dict, change_info: dict,
                       assessment: dict, metadata: dict):
    """FDA 510(k) 변경 검토 문서 생성 (회사 실제 제출 양식)"""
    doc = init_document()

    # ===== Change details =====
    add_paragraph(doc, "Change the Existing device for 510(k)", bold=True)
    add_spacer(doc)

    add_paragraph(doc, "1) Existing device", bold=True)
    add_paragraph(doc, f"- {product_info.get('fdaK510', 'N/A')} ({product_info.get('modelName', '[Model Name]')})")
    add_spacer(doc)

    add_paragraph(doc, "2) Change Details", bold=True)
    add_paragraph(doc, "(1) Existing registration details", bold=True)
    add_paragraph(doc, change_info.get("componentName", ""), bold=True)
    add_info_table(doc, [("Before", change_info.get("beforeValue", ""))])
    add_spacer(doc)

    add_paragraph(doc, "(2) Change request", bold=True)
    add_paragraph(doc, change_info.get("componentName", ""), bold=True)
    add_info_table(doc, [("After", change_info.get("afterValue", ""))])
    add_spacer(doc)
    add_paragraph(doc, change_info.get("description") or change_info.get("changeTitle", ""))
    add_spacer(doc)

    add_paragraph(doc, "(3) Reason for change", bold=True)
    add_paragraph(doc, change_info.get("reason", "[Reason for change]"))

    add_page_break(doc)

    # ===== Assessment results =====
    add_paragraph(
        doc,
        f'The results of reviewing the changes in accordance with "{FDA_GUIDANCE_TITLE}".',
        bold=True,
    )
    add_spacer(doc)

    add_paragraph(doc, "- Main Chart", bold=True)
    for q in assessment["path"]:
        if q["answer"] is None or not q["id"].startswith("MAIN"):
            continue
        suffix = ""
        if q["answer"] and q["id"] in CHART_LETTER:
            suffix = f" (Go to Chart {CHART_LETTER[q['id']]})"
        _qa_line(doc, q["text_en"], q["answer"], suffix)

    last_chart_letter = None
    for q in assessment["path"]:
        if q["answer"] is None or q["id"].startswith("MAIN"):
            continue
        chart_letter = q["id"][0]
        if chart_letter != last_chart_letter:
            add_spacer(doc)
            add_paragraph(doc, f"- Chart {chart_letter}", bold=True)
            last_chart_letter = chart_letter
        _qa_line(doc, f"{q['id']}: {q['text_en']}", q["answer"])

    add_spacer(doc)
    if assessment.get("manualReviewRequired"):
        result_label = "Manual Review Required (IVD — Flowchart D not supported)"
    elif assessment["isSignificant"]:
        result_label = "New 510(k)"
    else:
        result_label = "Documentation"

    add_paragraph(doc, f"Result: {result_label}")
    add_spacer(doc)
    add_paragraph(doc, f"The change is considered a {result_label}.", bold=True)

    return doc
