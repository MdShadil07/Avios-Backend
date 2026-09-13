import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.ai.llm import get_llm
from app.ai.state import ComplaintState


RISK_PROMPT = """
You are a pharmaceutical Quality Assurance risk assessment assistant.

Assess the initial risk of the customer complaint.

Use only the information provided.

Risk levels:

- Minor:
  Low impact, limited quality concern, unlikely to affect product
  quality or patient safety.

- Major:
  Significant quality concern that requires formal investigation,
  but there is no clear evidence of immediate serious patient harm.

- Critical:
  Potential serious patient safety impact, contamination,
  incorrect product/strength, serious adverse event, or another
  condition that may require immediate escalation.

Important:

1. Do not invent facts.
2. Explain the reasoning clearly.
3. Make the recommended action QA-oriented (e.g. "investigate -> assess scope -> QA determines escalation/recall").
4. Avoid overly aggressive actions without evidence (e.g. do not independently recommend a recall without QA evaluation).
5. The assessment is only an initial recommendation. A qualified QA professional must make the final decision.

Return ONLY valid JSON with exactly these fields:

{
  "risk_level": "Minor | Major | Critical",
  "reasoning": "short explanation",
  "recommended_action": "short recommended QA action"
}
"""


def risk_node(state: ComplaintState) -> ComplaintState:
    extracted_data = state.get("extracted_data", {})

    complaint_context = {
        "product_name": extracted_data.get("product_name"),
        "product_type": extracted_data.get("product_type"),
        "batch_number": extracted_data.get("batch_number"),
        "affected_quantity": extracted_data.get(
            "affected_quantity"
        ),
        "defect_category": extracted_data.get(
            "defect_category"
        ),
        "description": extracted_data.get("description"),
        "packaging_type": extracted_data.get(
            "packaging_type"
        ),
        "sample_available": extracted_data.get(
            "sample_available"
        ),
    }

    llm = get_llm()

    messages = [
        SystemMessage(content=RISK_PROMPT),
        HumanMessage(
            content=(
                "Complaint information:\n\n"
                + json.dumps(
                    complaint_context,
                    indent=2,
                )
            )
        ),
    ]

    try:
        response = llm.invoke(messages)

        content = response.content

        # Handle models that wrap JSON in markdown fences.
        content = content.strip()

        if content.startswith("```"):
            content = content.replace(
                "```json",
                "",
            )
            content = content.replace(
                "```",
                "",
            )
            content = content.strip()

        risk_assessment = json.loads(content)

        risk_level = risk_assessment.get(
            "risk_level"
        )

        if risk_level not in {
            "Minor",
            "Major",
            "Critical",
        }:
            raise ValueError(
                "AI returned an invalid risk level."
            )

        return {
            **state,
            "risk_assessment": {
                "risk_level": risk_level,
                "reasoning": risk_assessment.get(
                    "reasoning",
                    "",
                ),
                "recommended_action": risk_assessment.get(
                    "recommended_action",
                    "",
                ),
            },
        }

    except Exception as exc:
        return {
            **state,
            "risk_assessment": {
                "risk_level": "Unknown",
                "reasoning": "",
                "recommended_action": "",
            },
            "errors": [
                *state.get("errors", []),
                f"Risk assessment failed: {str(exc)}",
            ],
        }