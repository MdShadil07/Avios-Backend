from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.ai.llm import get_llm
from app.ai.state import ComplaintState


class ComplaintExtraction(BaseModel):
    customer_name: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    country: str | None = None

    product_name: str | None = None
    product_type: Literal["API", "FDF"] | None = None
    strength: str | None = None
    dosage_form: str | None = None

    batch_number: str | None = None
    manufacturing_date: str | None = None
    expiry_date: str | None = None

    affected_quantity: str | None = None
    defect_category: str | None = None
    complaint_date: str | None = None
    source: str | None = None

    description: str | None = None

    manufacturing_site: str | None = None
    packaging_type: str | None = None
    storage_condition: str | None = None
    sample_available: Literal["Yes", "No"] | None = None


EXTRACTION_PROMPT = """
You are a pharmaceutical quality complaint extraction assistant.

Your task is to extract structured information from the customer complaint.

Important rules:

1. Extract only information explicitly present in the complaint.
2. Never invent or assume missing information.
3. If a field is not present, return null.
4. product_type must be either API or FDF when explicitly stated.
5. Preserve important details from the original complaint.
6. defect_category should be a concise pharmaceutical quality category.
7. Keep dates in the format YYYY-MM-DD whenever possible.
8. For affected_quantity, preserve both the quantity and its unit when explicitly stated. Examples:
   - "50 kg" -> "50 kg"
   - "15-20 tablets" -> "15-20 tablets"
   - "24 vials" -> "24 vials"
9. Preserve all material complaint details in the description, including:
   - what happened
   - affected quantity
   - product condition
   - packaging observations
   - potential cause stated by complainant
   - sample availability
   - patient/customer impact
   - requested action
   Do not omit meaningful details merely to make the description shorter.
10. Source classification:
    - If the complaint contains email headers such as From/To/Subject, return "Email".
    - If it is clearly submitted through a web form, return "Web".
    - If it explicitly indicates a phone call, return "Phone".
    - If the source cannot be determined, return null.
11. For sample_available, extract strictly "Yes" or "No". Return null if not explicitly stated.
"""


def extraction_node(state: ComplaintState) -> ComplaintState:
    llm = get_llm()

    structured_llm = llm.with_structured_output(ComplaintExtraction)

    messages = [
        SystemMessage(content=EXTRACTION_PROMPT),
        HumanMessage(
            content=f"Customer Complaint:\n\n{state['raw_text']}"
        ),
    ]

    try:
        result = structured_llm.invoke(messages)

        extracted_data = result.model_dump()

        return {
            **state,
            "extracted_data": extracted_data,
            "errors": [],
        }

    except Exception as exc:
        return {
            **state,
            "extracted_data": {},
            "errors": [
                f"AI extraction failed: {str(exc)}"
            ],
        }