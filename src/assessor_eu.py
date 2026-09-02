"""
EU MDR Assessor
Reference: MDCG 2020-3 Rev.1 (May 2023) - Guidance on significant changes regarding
           the transitional provision under Article 120 of the MDR with regard to
           devices covered by certificates according to MDD or AIMDD

이 모듈은 MDCG 2020-3 Rev.1의 실제 Main Chart(Annex, p.16)와 Chart A~E를
그대로 의사결정 트리(EU_GRAPH)로 구현한다.

Main Chart 순서 (각 게이트는 독립적으로 순서대로 확인됨):
    0. 시정조치(corrective action)로 승인된 변경인가? -> Yes면 곧바로 비중대
    1. 사용목적(Intended Purpose) 변경? -> Yes: Chart A
    2. 설계(Design) 변경? -> Yes: Chart B
    3. 소프트웨어 변경? -> Yes: Chart C
    4. 물질/재료(Substance/Material) 변경? -> Yes: Chart D
    5. 말단 멸균 방법 변경 또는 멸균에 영향 주는 포장 설계 변경(유효기간 포함)? -> Yes: Chart E
    (어느 Chart라도 "Significant"면 전체 결론은 Significant)
"""

TERMINALS = ("SIGNIFICANT", "NON_SIGNIFICANT")

EU_MAIN_ITEMS = [
    {
        "key": "MAIN0",
        "text": "이 변경은 관할 당국(competent authority)이 평가·승인한 시정조치(corrective action, "
                "예: FSCA)에 따른 것입니까?",
    },
    {"key": "MAIN_A", "text": "사용목적(Intended Purpose) 변경입니까?"},
    {"key": "MAIN_B", "text": "설계(Design) 변경입니까? (제어기전/작동원리/에너지원/알람 시스템 등)"},
    {"key": "MAIN_C", "text": "소프트웨어 변경입니까?"},
    {"key": "MAIN_D", "text": "물질(substance) 또는 재료(material) 변경입니까?"},
    {
        "key": "MAIN_E",
        "text": "말단 멸균(terminal sterilisation) 방법 변경이거나, 멸균 상태에 영향을 주는 포장 설계 "
                "변경(유효기간 연장 포함)입니까?",
    },
]

EU_GRAPH = {
    # --- Chart A: Change of Intended Purpose ---
    "A1": {"text": "사용목적의 제한(limitation)입니까? (예: 적응증/적용 부위/전달경로/대상 환자군 축소·삭제)", "yes": "NON_SIGNIFICANT", "no": "A2"},
    "A2": {"text": "사용목적의 확장(extension)입니까? (예: 신규 적응증, 신규 임상적 조건 추가)", "yes": "SIGNIFICANT", "no": "A3"},
    "A3": {"text": "신규 사용자 또는 환자군(new user or patient population)이 추가됩니까?", "yes": "SIGNIFICANT", "no": "A4"},
    "A4": {"text": "새로운 임상 적용 방식(new way of clinical application)입니까? (예: 신규 적용 부위, 전달경로, 배치 방법)", "yes": "SIGNIFICANT", "no": "NON_SIGNIFICANT"},

    # --- Chart B: Change of Design ---
    "B1": {
        "text": "내장 제어기전(built-in control mechanism), 작동원리(operating principle), 에너지원(source of energy), "
                "또는 알람 시스템(alarm system)을 변경합니까?",
        "yes": "SIGNIFICANT", "no": "B2",
    },
    "B2": {
        "text": "이 변경이 안전성 또는 성능에 영향을 주고, 이익/위험비(benefit/risk ratio)를 악화시킵니까?",
        "yes": "SIGNIFICANT", "no": "NON_SIGNIFICANT",
    },

    # --- Chart C: Software Changes ---
    "C1": {"text": "운영체제(OS) 또는 그 구성요소의 신규·주요 변경입니까?", "yes": "SIGNIFICANT", "no": "C2"},
    "C2": {"text": "아키텍처 또는 데이터베이스 구조의 신규·수정, 또는 알고리즘 변경입니까?", "yes": "SIGNIFICANT", "no": "C3"},
    "C3": {"text": "요구되던 사용자 입력이 폐루프(closed loop) 알고리즘으로 대체됩니까?", "yes": "SIGNIFICANT", "no": "C4"},
    "C4": {
        "text": "신규 사용자 인터페이스, 신규 의료 기능(medical feature), 신규 상호운용성(interoperability) 채널, "
                "또는 데이터 표시 방식 변경입니까?",
        "yes": "SIGNIFICANT", "no": "C5",
    },
    "C5": {"text": "이 변경이 이익/위험비(benefit/risk ratio)를 악화시킵니까?", "yes": "SIGNIFICANT", "no": "NON_SIGNIFICANT"},

    # --- Chart D: Changes related to a Substance or Material ---
    "D1": {"text": "인체/동물 유래 물질(material of human/animal origin)을 추가하거나 변경합니까?", "yes": "SIGNIFICANT", "no": "D2"},
    "D2": {
        "text": "약리물질(medicinal substance, MS)의 부형제(excipient) 또는 그 약리물질 자체를 변경합니까?",
        "yes": "SIGNIFICANT", "no": "D3",
    },
    "D3": {
        "text": "해당 재료/물질이 인체 조직·체액과 30일 초과 접촉하거나, 흡수성(외과적 침습기기에 한함)입니까?",
        "yes": "SIGNIFICANT", "no": "D4",
    },
    "D4": {
        "text": "이 변경이 안전성 또는 성능에 영향을 주고, 이익/위험비를 악화시킵니까?",
        "yes": "SIGNIFICANT", "no": "NON_SIGNIFICANT",
    },

    # --- Chart E: Changes related to Sterilisation ---
    "E1": {"text": "말단 멸균 방법(terminal sterilisation method)을 변경합니까?", "yes": "SIGNIFICANT", "no": "E2"},
    "E2": {"text": "무균성 보증수준(sterility assurance level, SAL)을 악화시키는 변경입니까?", "yes": "SIGNIFICANT", "no": "E3"},
    "E3": {
        "text": "포장 설계 변경이 무균성, 안정성, 또는 미생물학적 상태(밀봉 무결성 포함)에 영향을 줍니까?",
        "yes": "SIGNIFICANT", "no": "E4",
    },
    "E4": {"text": "유효기간(shelf-life) 연장입니까?", "yes": "E5", "no": "NON_SIGNIFICANT"},
    "E5": {
        "text": "그 유효기간 연장이 인증기관(Notified Body) 승인 프로토콜에 따라 검증되었습니까?",
        "yes": "NON_SIGNIFICANT", "no": "SIGNIFICANT",
    },
}

CHART_ENTRY = {
    "MAIN_A": ("A1", "Chart A: Change of Intended Purpose"),
    "MAIN_B": ("B1", "Chart B: Change of Design"),
    "MAIN_C": ("C1", "Chart C: Software Changes"),
    "MAIN_D": ("D1", "Chart D: Changes to a Substance or Material"),
    "MAIN_E": ("E1", "Chart E: Changes to Sterilisation"),
}


def walk_eu_graph(start_id: str, answers: dict):
    """
    answers: {node_id: True/False/None}. Walks EU_GRAPH from start_id following
    the recorded answers until a terminal is reached or an unanswered node is hit.
    Returns (path, outcome) where outcome is None if the walk is incomplete.
    """
    path = []
    node_id = start_id
    while node_id not in TERMINALS:
        node = EU_GRAPH[node_id]
        ans = answers.get(node_id)
        path.append({"id": node_id, "text": node["text"], "answer": ans})
        if ans is None:
            return path, None
        node_id = node["yes"] if ans else node["no"]
    return path, node_id


def run_eu_questionnaire(ask, ask_yes_no, change_info: dict) -> dict:
    answers = {}

    print("  ── Main Chart ──")
    answers["MAIN0"] = ask_yes_no(f"    MAIN0. {EU_MAIN_ITEMS[0]['text']}")
    if answers["MAIN0"]:
        return answers

    for item in EU_MAIN_ITEMS[1:]:
        answers[item["key"]] = ask_yes_no(f"    {item['key']}. {item['text']}")

    def walk_interactive(start_id):
        node_id = start_id
        while node_id not in TERMINALS:
            node = EU_GRAPH[node_id]
            ans = ask_yes_no(f"    {node_id}. {node['text']}")
            answers[node_id] = ans
            node_id = node["yes"] if ans else node["no"]

    for main_key, (entry_node, chart_name) in CHART_ENTRY.items():
        if answers.get(main_key):
            print(f"\n  ── {chart_name} ──")
            walk_interactive(entry_node)

    return answers


def assess_eu(answers: dict, change_info: dict) -> dict:
    a = answers
    guidance = (
        "MDCG 2020-3 Rev.1 (May 2023) – Guidance on significant changes regarding the transitional "
        "provision under Article 120 of the MDR"
    )

    if a.get("MAIN0") is True:
        result = {
            "country": "EU",
            "guidance": guidance,
            "isSignificant": False,
            "nbDetectorException": False,
            "requiredAction": "Process under QMS; no NB prior approval",
            "path": [{"id": "MAIN0", "text": EU_MAIN_ITEMS[0]["text"], "answer": True}],
            "summary": (
                "이 변경은 관할 당국이 평가·승인한 시정조치(corrective action)에 따른 것으로, "
                "MDCG 2020-3에 따라 설계/사용목적의 비중대 변경으로 간주됩니다."
            ),
        }
    else:
        path = [{"id": "MAIN0", "text": EU_MAIN_ITEMS[0]["text"], "answer": a.get("MAIN0")}]
        for item in EU_MAIN_ITEMS[1:]:
            path.append({"id": item["key"], "text": item["text"], "answer": a.get(item["key"])})

        significant = False
        any_chart_invoked = False
        for main_key, (entry_node, _chart_name) in CHART_ENTRY.items():
            if a.get(main_key):
                any_chart_invoked = True
                chart_path, outcome = walk_eu_graph(entry_node, a)
                path += chart_path
                if outcome == "SIGNIFICANT":
                    significant = True

        if significant:
            required_action = "Notified Body notification & approval required"
            summary = (
                "MDCG 2020-3 Rev.1의 결정 차트에 따라 이 변경은 설계 또는 사용목적의 중대한 변경(significant change)에 "
                "해당하는 것으로 판단되어, 인증기관(Notified Body)의 사전 승인이 필요합니다."
            )
        elif not any_chart_invoked:
            required_action = "Process under QMS; no NB prior approval"
            summary = (
                "이 변경은 사용목적, 설계, 소프트웨어, 물질/재료, 멸균 중 어느 항목에도 해당하지 않는 것으로 확인되어, "
                "제조사의 QMS(ISO 13485) 변경관리 절차에 따라 처리하면 됩니다."
            )
        else:
            required_action = "Process under QMS; no NB prior approval"
            summary = (
                "MDCG 2020-3 Rev.1의 해당 결정 차트를 평가한 결과 이 변경은 설계 또는 사용목적의 중대한 변경에 "
                "해당하지 않는 것으로 판단되어, 제조사의 QMS(ISO 13485) 변경관리 절차에 따라 처리하면 됩니다."
            )

        result = {
            "country": "EU",
            "guidance": guidance,
            "isSignificant": significant,
            "nbDetectorException": False,
            "requiredAction": required_action,
            "path": path,
            "summary": summary,
        }

    # NB Exception: 디텍터 추가/변경은 NB 확인에 따라 non-significant 처리 (회사 고유 사전 확인 사항)
    nb_detector_exception = "detector" in change_info.get("componentName", "").lower()
    if nb_detector_exception:
        result["isSignificant"] = False
        result["nbDetectorException"] = True
        result["requiredAction"] = "Process under QMS; no NB prior approval (NB Exception: detector change)"
        result["summary"] = (
            "NB Exception Applied: The Notified Body has confirmed that detector additions or "
            "changes are classified as non-significant changes. This change will be processed "
            "under the manufacturer's QMS (ISO 13485) change-control procedure, with records "
            "made available to the Notified Body during routine surveillance."
        )

    return result
