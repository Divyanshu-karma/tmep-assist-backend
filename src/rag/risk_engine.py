# src/rag/risk_engine.py

import re
from typing import List, Dict, Optional


# -------------------------------------------------
# Risk Mapping Configuration (UNCHANGED)
# -------------------------------------------------

RISK_MAPPING = {
    "HIGH": [
        "1207",
        "1203",
        "1210",
        "1211",
        "1206",
        "1204",
        "1209.01(c)",  # specific override
    ],
    "MEDIUM-HIGH": [
        "1209",
        "1202",
        "1202.04",
        "1301",
        "1302",
        "1303",
        "1304",
        "1212",
    ],
    "MEDIUM": [
        "904",
        "807",
        "1213",
        "1402",
    ],
    "MEDIUM-LOW": [
        "300",
        "400",
        "600",
        "700",
    ],
    "LOW": [
        "100",
        "200",
        "304",
        "500",
    ]
}


# -------------------------------------------------
# 🔹 Strongly Recommended Improvement:
# Precompute sorted prefix rules once (longest prefix first)
# -------------------------------------------------

_SORTED_RULES = sorted(
    [
        (risk, prefix.lower())
        for risk, prefixes in RISK_MAPPING.items()
        for prefix in prefixes
    ],
    key=lambda x: len(x[1]),
    reverse=True,
)


# -------------------------------------------------
# Section Classification
# -------------------------------------------------

def classify_section(section_id: str) -> str:
    """
    Determine risk level based on TMEP section prefix.
    Longest prefix match wins.
    """

    # 🔹 Required Improvement: normalize case
    section_id = section_id.strip().lower()

    for risk, prefix in _SORTED_RULES:
        # 🔹 Required Improvement: normalized prefix comparison
        if section_id.startswith(prefix):
            return risk

    # 🔹 Strongly Recommended: safer fallback
    return "MEDIUM"


# -------------------------------------------------
# LLM Output Parsing
# -------------------------------------------------

def parse_llm_output(text: str) -> List[Dict]:
    """
    Extract structured issues from LLM output.
    Returns list of dictionaries.

    🔹 Required Improvements:
    - Flexible spacing tolerance
    - Case-insensitive parsing
    - Optional § symbol tolerance
    """

    pattern = (
        r"ISSUE:\s*(.*?)\s*"
        r"TMEP\s*CITATION:\s*§?\s*([\d\.\(\)a-zA-Z]+)\s*"
        r"TMEP-BASED\s*EXPLANATION:\s*(.*?)(?=\nISSUE:|\Z)"
    )

    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    issues = []

    for issue, citation, explanation in matches:
        issues.append({
            "issue": issue.strip(),
            "citation": citation.strip(),
            "explanation": explanation.strip(),
        })

    return issues


# -------------------------------------------------
# Risk Engine Application
# -------------------------------------------------

def apply_risk_engine(
    llm_text: str,
    retrieved_sections: Optional[List[str]] = None
) -> str:
    """
    Convert LLM structured output into final risk-assigned report.

    🔹 Advanced Improvement:
    Optional validation of citations against retrieved sections.
    """

    issues = parse_llm_output(llm_text)

    if not issues:
        return "NO APPLICABLE TMEP PROVISION FOUND."

    # 🔹 Advanced Safeguard: Validate citations against retrieved sections
    if retrieved_sections:
        normalized_retrieved = {
            s.strip().lower() for s in retrieved_sections
        }

        validated_issues = []
        for item in issues:
            if item["citation"].strip().lower() in normalized_retrieved:
                validated_issues.append(item)

        issues = validated_issues

        if not issues:
            return "NO APPLICABLE TMEP PROVISION FOUND."

    final_blocks = []

    for item in issues:
        risk = classify_section(item["citation"])

        block = (
            f"RISK CATEGORY: {risk}\n\n"
            f"ISSUE:\n{item['issue']}\n\n"
            f"TMEP CITATION:\n§{item['citation']}\n\n"
            f"REASONING:\n{item['explanation']}\n\n"
        )

        final_blocks.append(block)

    final_blocks.append(
        "Disclaimer: This assessment is generated for research and "
        "decision-support purposes only. It is not legal advice."
    )

    return "\n".join(final_blocks)











# src/rag/risk_engine.py

# RISK_MAPPING = {
#     "HIGH": [
#         "1207",
#         "1203",
#         "1210",
#         "1211",
#         "1206",
#         "1204",
#         "1209.01(c)",  # specific override
#     ],
#     "MEDIUM-HIGH": [
#         "1209",
#         "1202",
#         "1202.04",
#         "1301",
#         "1302",
#         "1303",
#         "1304",
#         "1212",
#     ],
#     "MEDIUM": [
#         "904",
#         "807",
#         "1213",
#         "1402",
#     ],
#     "MEDIUM-LOW": [
#         "300",
#         "400",
#         "600",
#         "700",
#     ],
#     "LOW": [
#         "100",
#         "200",
#         "304",
#         "500",
#     ]
# }

# def classify_section(section_id: str) -> str:
#     """
#     Determine risk level based on TMEP section prefix.
#     Longest prefix match wins.
#     """

#     section_id = section_id.strip()

#     # Build list of (risk, prefix) pairs
#     rules = []
#     for risk, prefixes in RISK_MAPPING.items():
#         for prefix in prefixes:
#             rules.append((risk, prefix))

#     # Sort by prefix length descending (longest first)
#     rules.sort(key=lambda x: len(x[1]), reverse=True)

#     # Match prefix
#     for risk, prefix in rules:
#         if section_id.startswith(prefix):
#             return risk

#     # Conservative fallback
#     return "MEDIUM-LOW"


# import re


# def parse_llm_output(text: str):
#     """
#     Extract structured issues from LLM output.
#     Returns list of dictionaries.
#     """

#     pattern = (
#         r"ISSUE:\s*(.*?)\s*"
#         r"TMEP CITATION:\s*§([\d\.\(\)a-zA-Z]+)\s*"
#         r"TMEP-BASED EXPLANATION:\s*(.*?)(?=\nISSUE:|\Z)"
#     )

#     matches = re.findall(pattern, text, re.DOTALL)

#     issues = []

#     for issue, citation, explanation in matches:
#         issues.append({
#             "issue": issue.strip(),
#             "citation": citation.strip(),
#             "explanation": explanation.strip(),
#         })

#     return issues

# def apply_risk_engine(llm_text: str) -> str:
#     """
#     Convert LLM structured output into final risk-assigned report.
#     """

#     issues = parse_llm_output(llm_text)

#     if not issues:
#         return "NO APPLICABLE TMEP PROVISION FOUND."

#     final_blocks = []

#     for item in issues:
#         risk = classify_section(item["citation"])

#         block = (
#             f"RISK CATEGORY: {risk}\n\n"
#             f"ISSUE:\n{item['issue']}\n\n"
#             f"TMEP CITATION:\n§{item['citation']}\n\n"
#             f"REASONING:\n{item['explanation']}\n\n"
#         )

#         final_blocks.append(block)

#     final_blocks.append(
#         "Disclaimer: This assessment is generated for research and "
#         "decision-support purposes only. It is not legal advice."
#     )

#     return "\n".join(final_blocks)

