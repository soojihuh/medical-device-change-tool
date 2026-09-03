"""
Health Canada change review document builder (Python).
Follows the company's actual Health Canada notification-letter template
(RIOScan_HC_Notification_Letter_2.docx): a formal letter to Health Canada
notifying a non-significant device change under Section 43(1)(b) of the
Medical Devices Regulations (SOR/98-282), rather than an internal review memo.
"""
from doc_common import init_document, add_paragraph, add_spacer, add_generic_table

HC_GUIDANCE_TITLE = 'Guidance on how to interpret "significant change" of a medical device: Types of changes'


def build_hc_document(product_info: dict, change_info: dict,
                      assessment: dict, metadata: dict):
    """Health Canada 변경 통지 서한(Notification Letter) 생성 (회사 실제 제출 양식)"""
    doc = init_document()

    model_name = product_info.get("modelName", "[Model Name]")
    licence_no = product_info.get("hcLicenceNo", "[XXXXX]")
    manufacturer = product_info.get("manufacturer", "[Manufacturer]")
    device_class = product_info.get("deviceClass", "[Class]")
    effective_date = metadata.get("effectiveDate", "[Date, e.g., YYYY-MM-DD]")

    # ===== Letter header =====
    add_paragraph(doc, effective_date)
    add_paragraph(doc, "Health Canada", after_pt=0)
    add_paragraph(doc, "Medical Devices Bureau", after_pt=0)
    add_paragraph(doc, "Device Licensing Services Division", after_pt=0)
    add_paragraph(doc, "[Address]")
    add_spacer(doc)

    add_paragraph(
        doc,
        f"Re: Notification of Non-Significant Device Change — {model_name} "
        f"(Medical Device Licence No. {licence_no})",
        bold=True,
    )
    add_paragraph(doc, "To Whom It May Concern:")

    add_paragraph(
        doc,
        f"Pursuant to Section 43(1)(b) of the Medical Devices Regulations (SOR/98-282), "
        f"{manufacturer} hereby notifies Health Canada of a change made to the "
        f"above-referenced licensed medical device, {model_name} (a {device_class} medical device), "
        f"as part of our next annual licence renewal filing.",
    )

    # ===== Description of Change =====
    change_desc = change_info.get("description") or change_info.get("changeTitle", "")
    reason = change_info.get("reason", "")
    desc_text = f"{change_desc} {reason}".strip()
    add_paragraph(doc, f"Description of Change: {desc_text}")

    # ===== Basis for Determination =====
    add_paragraph(
        doc,
        f"Basis for Determination: {model_name} is licensed as a {device_class} medical device. "
        f"This change was assessed in accordance with Health Canada's guidance document, "
        f"{HC_GUIDANCE_TITLE}. Section 34 of the Regulations sets out the categories of changes, "
        f"under paragraphs (a) through (f), that require submission of a licence amendment application; "
        f"this change does not fall within any of these categories. Accordingly, a licence amendment "
        f"is not required for this change.",
    )

    add_paragraph(
        doc,
        f"This change has been evaluated and documented within {manufacturer}'s quality management "
        f"system (ISO 13485) under our design change control procedures, including verification and/or "
        f"validation activities confirming that the safety and performance of the device are unaffected "
        f"by this change.",
    )

    add_paragraph(
        doc,
        "In accordance with Health Canada's guidance recommending that non-significant changes be "
        "itemized in a table with a brief rationale at the time of annual licence renewal, the details "
        "of this change are provided below:",
    )
    add_spacer(doc)

    # ===== Change details table =====
    component = change_info.get("componentName", "")
    before_v = change_info.get("beforeValue", "")
    after_v = change_info.get("afterValue", "")
    device_change_cell = f"{model_name} — {component}, {before_v} → {after_v}" if component else model_name

    rationale = (
        f"{reason} " if reason else ""
    ) + (
        "Assessed against Health Canada's guidance on interpreting \"significant change\" "
        "(manufacturing process, quality control, design, sterilization, software, materials, and "
        "labelling); the change does not meet the criteria for a significant change under CMDR Section 34."
    )
    doc_refs = [
        ref for ref in [
            change_info.get("designSpecRef"),
            change_info.get("riskAssessmentRef"),
            change_info.get("vvSummaryRef"),
        ] if ref
    ]
    supporting_docs = "; ".join(doc_refs) if doc_refs else "[Attachments — spec comparison, test reports, risk assessment, as applicable]"

    add_generic_table(
        doc,
        ["Date of Change", "Device / Change", "Rationale (Why Not Significant)", "Supporting Documentation"],
        [[effective_date, device_change_cell, rationale, supporting_docs]],
        col_widths_cm=[2.7, 4.3, 6.5, 2.5],
    )
    add_spacer(doc)

    # ===== Closing =====
    add_paragraph(doc, "Should you require any additional information regarding this change, please do not hesitate to contact the undersigned.")
    add_paragraph(doc, "Sincerely,")
    add_paragraph(doc, metadata.get("preparedBy") or "[Name]", after_pt=0)
    add_paragraph(doc, "[Title]", after_pt=0)
    add_paragraph(doc, f"Regulatory Affairs, {manufacturer}", after_pt=0)
    add_paragraph(doc, "[Email] / [Phone]")

    return doc
