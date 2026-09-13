from typing import Any

from app.ai.state import ComplaintState


# Fields that are essential before a complaint can proceed
REQUIRED_FIELDS = [
    "customer_name",
    "product_name",
    "batch_number",
    "description",
    "defect_category",
]

# Fields that are important for investigation but may not always
# be available at the initial complaint intake stage.
IMPORTANT_FIELDS = [
    "contact_name",
    "email",
    "product_type",
    "manufacturing_date",
    "expiry_date",
    "affected_quantity",
]

# Fields that improve investigation quality but are not mandatory
# for initial complaint creation.
OPTIONAL_FIELDS = [
    "country",
    "phone",
    "strength",
    "dosage_form",
    "complaint_date",
    "source",
    "manufacturing_site",
    "packaging_type",
    "storage_condition",
    "sample_available",
]


def _is_missing(value: Any) -> bool:
    """
    Return True when a field has no meaningful value.
    """
    if value is None:
        return True

    if isinstance(value, str) and not value.strip():
        return True

    return False


def completeness_node(state: ComplaintState) -> ComplaintState:
    """
    Check whether the extracted complaint contains enough
    information for QA review and investigation.
    """

    extracted_data = state.get("extracted_data", {})

    missing_required = [
        field
        for field in REQUIRED_FIELDS
        if _is_missing(extracted_data.get(field))
    ]

    missing_important = [
        field
        for field in IMPORTANT_FIELDS
        if _is_missing(extracted_data.get(field))
    ]

    missing_optional = [
        field
        for field in OPTIONAL_FIELDS
        if _is_missing(extracted_data.get(field))
    ]

    if missing_required:
        status = "Incomplete"
    elif missing_important:
        status = "Needs Review"
    else:
        status = "Complete"

    completeness = {
        "status": status,
        "required_fields": {
            "total": len(REQUIRED_FIELDS),
            "missing": missing_required,
            "complete": len(REQUIRED_FIELDS) - len(missing_required),
        },
        "important_fields": {
            "total": len(IMPORTANT_FIELDS),
            "missing": missing_important,
            "complete": len(IMPORTANT_FIELDS) - len(missing_important),
        },
        "optional_fields": {
            "total": len(OPTIONAL_FIELDS),
            "missing": missing_optional,
            "complete": len(OPTIONAL_FIELDS) - len(missing_optional),
        },
        "total_missing": (
            len(missing_required)
            + len(missing_important)
            + len(missing_optional)
        ),
    }

    return {
        **state,
        "completeness": completeness,
    }