from app.ai.state import ComplaintState
from app.db.database import SessionLocal
from app.models.complaint import Complaint
from app.services.duplicate_service import find_duplicate_complaints


def duplicate_node(state: ComplaintState) -> ComplaintState:
    """
    Check whether the current complaint resembles
    previously logged complaints.
    """

    extracted_data = state.get("extracted_data", {})

    # Create a temporary Complaint object from the
    # extracted AI data so that the duplicate service
    # can compare it with historical complaints.
    complaint = Complaint(
        id=0,
        complaint_number="TEMP",
        customer_name=extracted_data.get(
            "customer_name",
            "",
        ),
        contact_name=extracted_data.get("contact_name"),
        email=extracted_data.get("email"),
        phone=extracted_data.get("phone"),
        country=extracted_data.get("country"),
        product_name=extracted_data.get(
            "product_name",
            "",
        ),
        product_type=extracted_data.get("product_type"),
        strength=extracted_data.get("strength"),
        dosage_form=extracted_data.get("dosage_form"),
        batch_number=extracted_data.get("batch_number"),
        manufacturing_date=extracted_data.get(
            "manufacturing_date"
        ),
        expiry_date=extracted_data.get("expiry_date"),
        affected_quantity=extracted_data.get(
            "affected_quantity"
        ),
        defect_category=extracted_data.get(
            "defect_category"
        ),
        complaint_date=extracted_data.get("complaint_date"),
        source=extracted_data.get("source"),
        description=extracted_data.get(
            "description",
            "",
        ),
        manufacturing_site=extracted_data.get(
            "manufacturing_site"
        ),
        packaging_type=extracted_data.get(
            "packaging_type"
        ),
        storage_condition=extracted_data.get(
            "storage_condition"
        ),
        sample_available=extracted_data.get(
            "sample_available"
        ),
    )

    db = SessionLocal()

    try:
        duplicates = find_duplicate_complaints(
            db,
            complaint,
        )

        return {
            **state,
            "duplicates": duplicates,
        }

    finally:
        db.close()