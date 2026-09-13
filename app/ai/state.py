from typing import Any, TypedDict


class ComplaintState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    raw_text: str

    extracted_data: dict[str, Any]

    completeness: dict[str, Any]

    duplicates: list[dict[str, Any]]

    risk_assessment: dict[str, Any]

    root_cause: dict[str, Any]

    capa: dict[str, Any]

    summary: str

    errors: list[str]
