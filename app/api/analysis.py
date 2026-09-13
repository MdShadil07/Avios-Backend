from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.ai.graph import complaint_graph


router = APIRouter(
    prefix="/api/intake",
    tags=["AI Intake"],
)


class ComplaintAnalysisRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=10,
        description="Raw customer complaint text",
    )


@router.post("/analyze")
def analyze_complaint(
    request: ComplaintAnalysisRequest,
):
    initial_state = {
        "raw_text": request.text,
        "errors": [],
    }

    result = complaint_graph.invoke(
        initial_state
    )

    return {
        "extracted_data": result.get(
            "extracted_data",
            {},
        ),
        "completeness": result.get(
            "completeness",
            {},
        ),
        "duplicates": result.get(
            "duplicates",
            [],
        ),
        "risk_assessment": result.get(
            "risk_assessment",
            {},
        ),
        "errors": result.get(
            "errors",
            [],
        ),
    }