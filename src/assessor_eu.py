"""
EU MDR Assessor
Reference: MDCG 2020-3 Rev.1 - Guidance on significant changes regarding the
           transitional provision under Article 120 of the MDR

Decision Charts:
    Chart A: Change in Design or Performance Specification
    Chart B: Change of Intended Purpose
    Chart C: Change in Software
    Chart D: Change of Substance / Material
    Chart E: Change of Sterilisation
"""


def run_eu_questionnaire(ask, ask_yes_no, change_info: dict) -> dict:
    print("  ── Chart A: Design / Performance Specification ──")
    A1 = ask_yes_no("    A.01. 설계 또는 성능 사양에 변경이 있고 사용 목적에 영향을 줍니까?")
    A2 = ask_yes_no("    A.02. 작동 원리(operating principle) 변경이 있습니까?")
    A3 = ask_yes_no("    A.03. 에너지원(source of energy) 변경이 있습니까?")
    A4 = ask_yes_no("    A.04. 알고리즘 또는 알람 변경이 있습니까?")
    A5 = ask_yes_no("    A.05. 사용자 인터페이스 / 인체공학 / 전달 방식 변경이 있습니까?")
    A6 = ask_yes_no("    A.06. 성능 또는 기능 변경이 있습니까?")

    print("\n  ── Chart B: Intended Purpose ──")
    B1 = ask_yes_no("    B.01. 사용 목적이 확장 또는 제한되었습니까?")
    B2 = ask_yes_no("    B.02. 적응증 / 금기 / 환자군 / 사용자 변경이 있습니까?")

    print("\n  ── Chart C: Software ──")
    C1 = ask_yes_no("    C.01. OS / 아키텍처 / DB 구조에 신규 또는 주요 변경이 있습니까?")
    C2 = ask_yes_no("    C.02. 신규 진단/치료 기능, 신규 사용자 상호작용, 의료 목적 변경이 있습니까?")
    C3 = ask_yes_no("    C.03. 진단 정보의 해석에 영향을 주는 변경이 있습니까?")

    print("\n  ── Chart D: Substance / Material ──")
    D1 = ask_yes_no("    D.01. 인체 조직/체액 접촉 재료/물질 변경이 있습니까?")
    D2 = ask_yes_no("    D.02. 핵심 구성품 또는 재료의 공급사(supplier) 변경이 있습니까? (단순 명칭 변경은 제외)")

    print("\n  ── Chart E: Sterilisation ──")
    E_applicable = ask_yes_no("    E.00. 본 장비가 멸균 의료기기입니까?")
    E1, E2 = False, False
    if E_applicable:
        E1 = ask_yes_no("    E.01. 멸균 방법 변경이 있습니까?")
        E2 = ask_yes_no("    E.02. 포장 / 멸균 배리어 시스템 변경이 있습니까?")
    else:
        print("         → 비멸균 장비이므로 Chart E는 N/A")

    return {
        "A1": A1, "A2": A2, "A3": A3, "A4": A4, "A5": A5, "A6": A6,
        "B1": B1, "B2": B2,
        "C1": C1, "C2": C2, "C3": C3,
        "D1": D1, "D2": D2,
        "E_applicable": E_applicable, "E1": E1, "E2": E2
    }


def assess_eu(answers: dict, change_info: dict) -> dict:
    a = answers

    chart_a = {
        "name": "Chart A – Change in Design or Performance Specification",
        "questions": [
            {"id": "A.01", "text": "Change in design/performance spec affecting intended purpose?", "answer": a.get("A1", False), "significant": a.get("A1", False)},
            {"id": "A.02", "text": "Change in operating principle?", "answer": a.get("A2", False), "significant": a.get("A2", False)},
            {"id": "A.03", "text": "Change in source of energy?", "answer": a.get("A3", False), "significant": a.get("A3", False)},
            {"id": "A.04", "text": "Change in algorithm or alarm?", "answer": a.get("A4", False), "significant": a.get("A4", False)},
            {"id": "A.05", "text": "Change in user interface / ergonomics / method of delivery?", "answer": a.get("A5", False), "significant": a.get("A5", False)},
            {"id": "A.06", "text": "Change in performance or functionality?", "answer": a.get("A6", False), "significant": a.get("A6", False)},
        ],
        "significant": any([a.get("A1"), a.get("A2"), a.get("A3"), a.get("A4"), a.get("A5"), a.get("A6")]),
        "applicable": True,
    }

    chart_b = {
        "name": "Chart B – Change of Intended Purpose",
        "questions": [
            {"id": "B.01", "text": "Intended purpose extended/restricted?", "answer": a.get("B1", False), "significant": a.get("B1", False)},
            {"id": "B.02", "text": "Indications/contraindications/patient population/user changed?", "answer": a.get("B2", False), "significant": a.get("B2", False)},
        ],
        "significant": any([a.get("B1"), a.get("B2")]),
        "applicable": True,
    }

    chart_c = {
        "name": "Chart C – Change in Software",
        "questions": [
            {"id": "C.01", "text": "New/major change in OS, architecture, DB structure?", "answer": a.get("C1", False), "significant": a.get("C1", False)},
            {"id": "C.02", "text": "New diagnostic/therapeutic feature or change of medical purpose?", "answer": a.get("C2", False), "significant": a.get("C2", False)},
            {"id": "C.03", "text": "Change affecting interpretation of diagnostic information?", "answer": a.get("C3", False), "significant": a.get("C3", False)},
        ],
        "significant": any([a.get("C1"), a.get("C2"), a.get("C3")]),
        "applicable": True,
    }

    chart_d = {
        "name": "Chart D – Change of Substance / Material",
        "questions": [
            {"id": "D.01", "text": "Change in material/substance contacting body tissues/fluids?", "answer": a.get("D1", False), "significant": a.get("D1", False)},
            {"id": "D.02", "text": "Change of supplier of critical component/material?", "answer": a.get("D2", False), "significant": a.get("D2", False)},
        ],
        "significant": any([a.get("D1"), a.get("D2")]),
        "applicable": True,
    }

    e_applicable = a.get("E_applicable", False)
    chart_e = {
        "name": "Chart E – Change of Sterilisation",
        "questions": [
            {"id": "E.01", "text": "Change in sterilisation method?", "answer": a.get("E1", False), "significant": a.get("E1", False)},
            {"id": "E.02", "text": "Change in packaging / sterile barrier system?", "answer": a.get("E2", False), "significant": a.get("E2", False)},
        ] if e_applicable else [],
        "significant": (a.get("E1", False) or a.get("E2", False)) if e_applicable else False,
        "applicable": e_applicable,
    }

    is_significant = (
        chart_a["significant"] or chart_b["significant"] or
        chart_c["significant"] or chart_d["significant"] or chart_e["significant"]
    )

    # NB Exception: 디텍터 추가/변경은 NB 확인에 따라 non-significant 처리
    nb_detector_exception = "detector" in change_info.get("componentName", "").lower()
    if nb_detector_exception:
        is_significant = False

    if nb_detector_exception:
        required_action = "Process under QMS; no NB prior approval (NB Exception: detector change)"
        summary = (
            "NB Exception Applied: The Notified Body has confirmed that detector additions or "
            "changes are classified as non-significant changes. This change will be processed "
            "under the manufacturer's QMS (ISO 13485) change-control procedure, with records "
            "made available to the Notified Body during routine surveillance."
        )
    elif is_significant:
        required_action = "Notified Body notification & approval required"
        summary = (
            "The change qualifies as a significant change under MDCG 2020-3. Prior notification "
            "to and approval by the Notified Body is required before implementation."
        )
    else:
        required_action = "Process under QMS; no NB prior approval"
        summary = (
            "The change does NOT qualify as a significant change under MDCG 2020-3. The change "
            "will be processed under the manufacturer's QMS (ISO 13485) change-control procedure, "
            "with records made available to the Notified Body during routine surveillance."
        )

    return {
        "country": "EU",
        "guidance": "MDCG 2020-3 Rev.1 – Guidance on significant changes regarding the transitional provision under Article 120 of the MDR",
        "isSignificant": is_significant,
        "nbDetectorException": nb_detector_exception,
        "requiredAction": required_action,
        "charts": [chart_a, chart_b, chart_c, chart_d, chart_e],
        "summary": summary,
    }
