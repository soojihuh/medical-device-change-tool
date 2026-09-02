"""
Health Canada Assessor
Reference: Guidance on how to interpret "significant change" of a medical device: Types of changes
https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/
guidance-documents/interpret-significant-change-medical-device/types-changes.html

이 페이지는 CMDR 34(2)(a)-(d) 문구를 그대로 4분류하지 않고, 아래처럼 별도 주제
섹션으로 나눠 각 섹션의 판정 기준을 서술한다 (FDA/EU와 달리 공식 Yes/No 플로우차트가
아니라 원칙+예시 위주). 이 모듈은 각 섹션의 핵심 판정 기준을 의사결정 트리로 옮긴 것이다.

포함된 섹션 (회사 제품이 비-IVD 활성기기라 관련성이 높은 것 위주):
    - Changes to manufacturing processes, facilities or equipment
    - Changes to manufacturing quality control procedures
    - Changes in design
    - Changes to sterilization and sterile barrier packaging
    - Changes to software
    - Changes in materials for non in vitro diagnostic devices
    - Changes to labelling

제외된 섹션 (회사 제품과 관련성이 낮음): IVD 기기 재료 변경, Class III/IV와 호환되는
Class II 기기 개정, 진단 초음파 시스템 변경.
"""

TERMINALS = ("SIGNIFICANT", "NON_SIGNIFICANT")

HC_MAIN_ITEMS = [
    {"key": "G_MFG", "text": "제조 공정(manufacturing process), 시설, 또는 장비 변경입니까?"},
    {"key": "G_QC", "text": "제조 품질관리(QC) 절차 변경입니까? (시험/검사 기준, 합격판정기준 등)"},
    {"key": "G_DESIGN", "text": "설계(design) 변경입니까? (제어기전, 작동원리, 설계사양, 구성품/액세서리, 사용자 인터페이스 등)"},
    {"key": "G_STERILE", "text": "멸균(sterilization) 방법 또는 멸균 배리어 포장 변경입니까?"},
    {"key": "G_SW", "text": "소프트웨어(software/firmware) 변경입니까?"},
    {"key": "G_MATERIAL", "text": "재료(material) 변경입니까? (비-IVD 기기 기준)"},
    {"key": "G_LABEL", "text": "라벨링(labelling) 변경입니까? (라벨, 사용설명서, 마케팅 자료 등)"},
]

HC_GRAPH = {
    # --- Changes to manufacturing processes, facilities or equipment ---
    "MFG1": {
        "text": "최종 제품의 공차(tolerance)를 완화하여 더 넓은 변동을 허용합니까? (성능에 영향 가능)",
        "yes": "SIGNIFICANT", "no": "MFG2",
    },
    "MFG2": {
        "text": "이 변경이 기기 사양, 성능, 또는 재료 특성에 영향을 줄 수 있습니까?",
        "yes": "MFG3", "no": "NON_SIGNIFICANT",
    },
    "MFG3": {
        "text": "신규 멸균 시설이거나, 동물유래재료 처리시설(abattoir)의 변경입니까?",
        "yes": "SIGNIFICANT", "no": "MFG4",
    },
    "MFG4": {
        "text": "(신규 제조시설 추가라면) 제조사명/주소가 유지되고, 기존과 동일 사양의 공정·장비를 사용하며, "
                "공급자 수입검사(incoming inspection) 기준도 변경되지 않았습니까?",
        "yes": "NON_SIGNIFICANT", "no": "SIGNIFICANT",
    },

    # --- Changes to manufacturing quality control procedures ---
    "QC1": {
        "text": "시험/검사 기준을 완화하거나, 합격판정기준(AQL)을 높이거나, 완제품 특성·성능을 확인하는 시험을 "
                "제거·수정합니까?",
        "yes": "SIGNIFICANT", "no": "NON_SIGNIFICANT",
    },

    # --- Changes in design ---
    "D1": {"text": "제어기전(control mechanism) 또는 작동원리(operating principle) 변경입니까?", "yes": "SIGNIFICANT", "no": "D2"},
    "D2": {
        "text": "설계사양(치수/재질/성능·기술사양/UI/S·W 등) 변경이 적응증·사용목적, 임상데이터 요구, 또는 "
                "위험 프로파일 중 하나 이상에 영향을 줍니까?",
        "yes": "SIGNIFICANT", "no": "D3",
    },
    "D3": {
        "text": "구성품/액세서리 변경이 기기 전체의 안전성·기능에 영향을 주거나, 사용자 상호작용 방식을 실질적으로 "
                "바꾸거나, 새로운 방식(신규 워크플로우/환자군/적응증)으로 사용되게 합니까?",
        "yes": "SIGNIFICANT", "no": "D4",
    },
    "D4": {
        "text": "환자/사용자 인터페이스 변경이 기기 사용 방식이나 상호작용에 영향을 줍니까? (단순 외관/편의 개선은 제외)",
        "yes": "SIGNIFICANT", "no": "NON_SIGNIFICANT",
    },

    # --- Changes to sterilization and sterile barrier packaging ---
    "S1": {
        "text": "멸균 방법을 변경하거나(예: EO→감마), 무균성보증수준(SAL)을 낮추거나, 임계 공정변수(가스농도/방사선량/"
                "노출시간 등)를 변경합니까?",
        "yes": "SIGNIFICANT", "no": "S2",
    },
    "S2": {
        "text": "제조공정/환경/재료 변화로 기존 검증보다 사멸시키기 어려운 유기체가 유입되거나, 생물학적 부하"
                "(bioburden)가 기존 검증 최대치를 초과합니까?",
        "yes": "SIGNIFICANT", "no": "S3",
    },
    "S3": {
        "text": "포장(재질/크기/형태/실링 등) 변경이 멸균제 침투·잔류, 멸균 유효성, 또는 무균 배리어의 무결성에 "
                "영향을 줍니까?",
        "yes": "SIGNIFICANT", "no": "NON_SIGNIFICANT",
    },

    # --- Changes to software ---
    "SW1": {
        "text": "의도된 사용과 관련된 기능/성능 사양에 영향을 주거나, 새로운 위험을 유발·기존 위험을 변경하거나, "
                "새로운/수정된 위험관리조치가 필요합니까?",
        "yes": "SIGNIFICANT", "no": "SW2",
    },
    "SW2": {
        "text": "프로그래밍 언어를 재작성하거나, 드라이버를 수정하거나, OS 커널이 달라지는 변경입니까? "
                "(예: Windows→Linux, 주요 OS 버전 변경)",
        "yes": "SIGNIFICANT", "no": "SW3",
    },
    "SW3": {
        "text": "사이버보안 강화, 원래 사양으로 되돌리는 버그 수정, 의료 목적이 없는 기능 추가(인쇄/언어 등), 또는 "
                "단순 외관(UI 색상/로고 등)만 변경하는 것입니까?",
        "yes": "NON_SIGNIFICANT", "no": "SW4",
    },
    "SW4": {
        "text": "위험평가 결과, 이 변경이 기기의 안전성 또는 유효성에 영향을 줄 수 있습니까?",
        "yes": "SIGNIFICANT", "no": "NON_SIGNIFICANT",
    },

    # --- Changes in materials for non in vitro diagnostic devices ---
    "M1": {
        "text": "재료의 공급원(source)/공급사만 바뀌고, 재료 종류·배합·화학조성·가공방법은 변경되지 않았습니까?",
        "yes": "NON_SIGNIFICANT", "no": "M2",
    },
    "M2": {"text": "인체 또는 동물 유래 물질을 추가하거나 그런 물질로 변경합니까?", "yes": "SIGNIFICANT", "no": "M3"},
    "M3": {"text": "변경된 재료가 신체 조직 또는 체액에 직접 또는 간접적으로 접촉합니까?", "yes": "M4", "no": "NON_SIGNIFICANT"},
    "M4": {
        "text": "동일 제조사의 유사 설계·동일 적응증 기기에 이미 사용된 재료이며, 그 비교 기기가 동일하거나 더 높은 "
                "위험등급·접촉위험도·접촉기간을 가지고 있어 Health Canada에 이미 검토된 상태입니까?",
        "yes": "NON_SIGNIFICANT", "no": "M5",
    },
    "M5": {
        "text": "이 재료가 체내 흡수되거나, 30일 이상 체내 잔류하거나, 중심 심혈관계/중추신경계와 접촉하는 침습기기에 "
                "사용됩니까?",
        "yes": "M5a", "no": "M6",
    },
    "M5a": {
        "text": "이 변경이 (FDA List 7 기준을 충족하는) 색소(colourant) 변경뿐이고 다른 변경사항이 없습니까?",
        "yes": "NON_SIGNIFICANT", "no": "SIGNIFICANT",
    },
    "M6": {
        "text": "위험평가 결과 새롭거나 증가된 생체적합성(biocompatibility) 우려가 확인됩니까?",
        "yes": "SIGNIFICANT", "no": "NON_SIGNIFICANT",
    },

    # --- Changes to labelling ---
    "L1": {
        "text": "적응증(indications) 또는 사용목적(intended use)을 확장하거나, 새로운 환자 하위군(특히 더 취약하거나 "
                "고위험군)을 추가합니까?",
        "yes": "SIGNIFICANT", "no": "L2",
    },
    "L2": {
        "text": "금기사항(contraindication)을 추가·삭제하거나, 기존 경고·주의사항을 삭제합니까?",
        "yes": "SIGNIFICANT", "no": "L3",
    },
    "L3": {
        "text": "새로운 임상적 효능(clinical benefit) 주장을 추가하거나(새 근거자료 필요), 이전에 검토되지 않은 방법으로 "
                "유효기간(shelf-life)을 연장·변경합니까?",
        "yes": "SIGNIFICANT", "no": "L4",
    },
    "L4": {
        "text": "다른 제조사 기기와의 신규 호환성(compatibility) 주장을 추가하거나, 자기공명(MR) 안전성 주장을 "
                "변경합니까?",
        "yes": "SIGNIFICANT", "no": "L5",
    },
    "L5": {
        "text": "이 라벨링 변경이 기존 승인 범위 내 단순 명확화, 편집상 수정, 다국어 추가(타 규제기관 요구), 또는 "
                "판매중단 기기 참조 제거 등에 해당합니까?",
        "yes": "NON_SIGNIFICANT", "no": "SIGNIFICANT",
    },
}

CHART_ENTRY = {
    "G_MFG": ("MFG1", "제조 공정/시설/장비 변경"),
    "G_QC": ("QC1", "제조 품질관리(QC) 절차 변경"),
    "G_DESIGN": ("D1", "설계(Design) 변경"),
    "G_STERILE": ("S1", "멸균 및 멸균 배리어 포장 변경"),
    "G_SW": ("SW1", "소프트웨어 변경"),
    "G_MATERIAL": ("M1", "재료 변경 (비-IVD)"),
    "G_LABEL": ("L1", "라벨링 변경"),
}


def walk_hc_graph(start_id: str, answers: dict):
    """
    answers: {node_id: True/False/None}. Walks HC_GRAPH from start_id following
    the recorded answers until a terminal is reached or an unanswered node is hit.
    Returns (path, outcome) where outcome is None if the walk is incomplete.
    """
    path = []
    node_id = start_id
    while node_id not in TERMINALS:
        node = HC_GRAPH[node_id]
        ans = answers.get(node_id)
        path.append({"id": node_id, "text": node["text"], "answer": ans})
        if ans is None:
            return path, None
        node_id = node["yes"] if ans else node["no"]
    return path, node_id


def run_hc_questionnaire(ask, ask_yes_no, change_info: dict) -> dict:
    answers = {}

    for item in HC_MAIN_ITEMS:
        answers[item["key"]] = ask_yes_no(f"    {item['key']}. {item['text']}")

    def walk_interactive(start_id):
        node_id = start_id
        while node_id not in TERMINALS:
            node = HC_GRAPH[node_id]
            ans = ask_yes_no(f"    {node_id}. {node['text']}")
            answers[node_id] = ans
            node_id = node["yes"] if ans else node["no"]

    for main_key, (entry_node, chart_name) in CHART_ENTRY.items():
        if answers.get(main_key):
            print(f"\n  ── {chart_name} ──")
            walk_interactive(entry_node)

    return answers


def assess_hc(answers: dict, change_info: dict) -> dict:
    a = answers
    guidance = (
        'Health Canada Guidance Document: Guidance on how to interpret "significant change" of a '
        "medical device: Types of changes"
    )

    path = [{"id": item["key"], "text": item["text"], "answer": a.get(item["key"])} for item in HC_MAIN_ITEMS]

    significant = False
    any_chart_invoked = False
    for main_key, (entry_node, _chart_name) in CHART_ENTRY.items():
        if a.get(main_key):
            any_chart_invoked = True
            chart_path, outcome = walk_hc_graph(entry_node, a)
            path += chart_path
            if outcome == "SIGNIFICANT":
                significant = True

    if significant:
        required_action = "Licence Amendment Application required"
        summary = (
            "Health Canada 가이던스의 해당 항목 판정 기준에 따라 이 변경은 CMDR Section 34에 따른 중대한 변경으로 "
            "판단되어, Licence Amendment 신청이 필요합니다."
        )
    elif not any_chart_invoked:
        required_action = "Internal record only; no Licence Amendment"
        summary = (
            "이 변경은 제조 공정/QC/설계/멸균/소프트웨어/재료/라벨링 중 어느 항목에도 해당하지 않는 것으로 확인되어, "
            "내부 기록만 유지하면 됩니다."
        )
    else:
        required_action = "Internal record only; no Licence Amendment"
        summary = (
            "Health Canada 가이던스의 해당 항목 판정 기준을 평가한 결과 이 변경은 중대한 변경에 해당하지 않는 것으로 "
            "판단되어, 제조사의 ISO 13485/MDSAP 인증 QMS 하에 처리하면 되며 내부 기록만 유지하면 됩니다."
        )

    return {
        "country": "HC",
        "guidance": guidance,
        "isSignificant": significant,
        "requiredAction": required_action,
        "path": path,
        "summary": summary,
    }
