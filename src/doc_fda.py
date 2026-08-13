"""
FDA Letter to File document builder (Python).
"""
from doc_common import (
    init_document, add_paragraph, add_bullet, add_bullet_bold,
    add_h1, add_h2, add_spacer,
    add_info_table, add_before_after_table,
    add_cover_page, add_revision_history, add_toc, add_footer,
)


def build_fda_document(product_info: dict, change_info: dict,
                       assessment: dict, metadata: dict):
    """FDA Letter to File 문서 생성"""
    doc_number = metadata.get("docNumber", "[LTF-XXXX-YYYY]")
    doc = init_document()

    # Footer (전체 섹션에 적용)
    add_footer(doc, doc_number)

    # Cover page
    add_cover_page(
        doc,
        doc_title="LETTER TO FILE",
        doc_subtitle=f"Change to Existing 510(k)-Cleared Device\n{change_info['changeTitle']}",
        doc_number=doc_number,
        rev_no=metadata.get("revisionNo", "00"),
        effective_date=metadata.get("effectiveDate", "[YYYY-MM-DD]"),
        prepared_by=metadata.get("preparedBy", ""),
        reviewed_by=metadata.get("reviewedBy", ""),
        approved_by=metadata.get("approvedBy", ""),
    )

    # Revision history
    add_revision_history(doc, metadata)

    # TOC
    add_toc(doc)

    # ===== Body =====

    # 1. Purpose
    add_h1(doc, "1. Purpose")
    add_paragraph(
        doc,
        'The purpose of this Letter to File is to document the evaluation of a change to '
        'the above-referenced 510(k)-cleared device, and to record the rationale demonstrating '
        'that a new 510(k) submission is not required pursuant to FDA Guidance "Deciding When '
        'to Submit a 510(k) for a Change to an Existing Device" (October 25, 2017).'
    )

    # 2. Device Identification
    add_h1(doc, "2. Device Identification")
    add_info_table(doc, [
        ("Model Name",              product_info.get("modelName", "[Model Name]")),
        ("Classification",          product_info.get("deviceClass", "[Class]")),
        ("Product Code",            product_info.get("fdaProductCode", "N/A")),
        ("Regulation Number",       product_info.get("fdaRegulationNumber", "N/A")),
        ("510(k) Number",           product_info.get("fdaK510", "N/A")),
        ("Manufacturer",            product_info.get("manufacturer", "[Manufacturer]")),
        ("Manufacturer Address",    product_info.get("manufacturerAddress", "[Address]")),
    ])

    # 3. Description of Change
    add_h1(doc, "3. Description of Change")
    add_h2(doc, "3.1 Nature of the Change")
    add_paragraph(doc, change_info.get("description") or change_info.get("changeTitle", ""))
    add_spacer(doc)
    add_before_after_table(doc, [
        [f"{change_info['componentName']} – Item",
         change_info.get("beforeValue", ""),
         change_info.get("afterValue", "")],
    ])
    add_spacer(doc)

    add_h2(doc, "3.2 Reason for the Change")
    add_paragraph(doc, change_info.get("reason", "[Reason for change]"))

    # 4. Regulatory Assessment
    add_h1(doc, "4. Regulatory Assessment per FDA Guidance (Oct 25, 2017)")
    add_paragraph(
        doc,
        'This change has been evaluated using the decision flowcharts provided in the FDA '
        'guidance "Deciding When to Submit a 510(k) for a Change to an Existing Device."'
    )

    for fc in assessment["flowcharts"]:
        add_h2(doc, fc["name"])
        for q in fc["questions"]:
            answer_text = "Yes" if q["answer"] else "No"
            add_bullet_bold(doc, f"{q['id']}. ", f"{q['text']} — {answer_text}.")
        conclusion = (
            "Could significantly affect — further review required."
            if fc["significant"]
            else "Not significant — Letter to File is sufficient."
        )
        add_paragraph(doc, f"Conclusion ({fc['name']}): {conclusion}", bold=True)

    # 5. Verification
    add_h1(doc, "5. Verification of Component Equivalence")
    add_paragraph(doc, "Supporting evidence has been obtained as follows:")
    add_bullet(doc,
        "Confirmation from the component manufacturer (Certificate of Conformity / official letter) "
        "that the post-change item is equivalent to the pre-change item with the exception of the "
        "change described above.")
    add_bullet(doc,
        "Confirmation that no other change has been made to hardware, firmware, performance, "
        "materials, or manufacturing process.")

    # 6. Conclusion
    add_h1(doc, "6. Conclusion")
    add_paragraph(doc, assessment["summary"])
    add_paragraph(doc,
        "This Letter to File and supporting records are retained as objective evidence of the "
        "evaluation, in accordance with 21 CFR Part 820.")

    # 7. References
    add_h1(doc, "7. References")
    add_bullet(doc, "FDA Guidance: Deciding When to Submit a 510(k) for a Change to an Existing Device (October 25, 2017)")
    add_bullet(doc, "21 CFR 807.81(a)(3) – When a 510(k) is required")
    add_bullet(doc, "21 CFR Part 820 – Quality System Regulation")
    add_bullet(doc, f"Original 510(k): {product_info.get('fdaK510', 'N/A')}")
    add_bullet(doc, "Component manufacturer Certificate of Equivalence / Letter dated [YYYY-MM-DD]")

    return doc
