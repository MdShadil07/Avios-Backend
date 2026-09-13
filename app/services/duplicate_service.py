from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models.complaint import Complaint


def normalize_text(value: str | None) -> str:
    """
    Normalize text before comparison.
    """
    if not value:
        return ""

    return " ".join(value.lower().strip().split())


def similarity_score(
    new_complaint: Complaint,
    historical_complaint: Complaint,
) -> dict:
    """
    Calculate similarity between two complaints.

    The score is based on:
    - Batch number
    - Product name
    - Defect category
    - Complaint description
    """

    new_product = normalize_text(new_complaint.product_name)
    old_product = normalize_text(historical_complaint.product_name)

    new_batch = normalize_text(new_complaint.batch_number)
    old_batch = normalize_text(historical_complaint.batch_number)

    new_defect = normalize_text(new_complaint.defect_category)
    old_defect = normalize_text(historical_complaint.defect_category)

    new_description = normalize_text(new_complaint.description)
    old_description = normalize_text(historical_complaint.description)

    product_similarity = SequenceMatcher(
        None,
        new_product,
        old_product,
    ).ratio()

    defect_similarity = SequenceMatcher(
        None,
        new_defect,
        old_defect,
    ).ratio()

    description_similarity = SequenceMatcher(
        None,
        new_description,
        old_description,
    ).ratio()

    batch_match = bool(
        new_batch
        and old_batch
        and new_batch == old_batch
    )

    # Weighted score
    score = (
        product_similarity * 0.35
        + defect_similarity * 0.20
        + description_similarity * 0.15
        + (1.0 if batch_match else 0.0) * 0.30
    )

    return {
        "score": round(score * 100, 2),
        "batch_match": batch_match,
        "product_similarity": round(product_similarity * 100, 2),
        "defect_similarity": round(defect_similarity * 100, 2),
        "description_similarity": round(
            description_similarity * 100,
            2,
        ),
    }


def find_duplicate_complaints(
    db: Session,
    complaint: Complaint,
    limit: int = 5,
) -> list[dict]:
    """
    Find historical complaints that may be duplicates.

    Candidates are first narrowed using product, batch,
    or defect information.
    """

    query = db.query(Complaint).filter(
        Complaint.id != complaint.id
    )

    candidates = query.filter(
        (Complaint.batch_number == complaint.batch_number)
        | (Complaint.product_name == complaint.product_name)
        | (Complaint.defect_category == complaint.defect_category)
    ).all()

    matches = []

    for historical_complaint in candidates:
        comparison = similarity_score(
            complaint,
            historical_complaint,
        )

        # Only surface reasonably similar complaints.
        if comparison["score"] >= 50:
            matches.append(
                {
                    "complaint_id": historical_complaint.id,
                    "complaint_number": historical_complaint.complaint_number,
                    "product_name": historical_complaint.product_name,
                    "batch_number": historical_complaint.batch_number,
                    "defect_category": historical_complaint.defect_category,
                    "similarity_score": comparison["score"],
                    "batch_match": comparison["batch_match"],
                    "product_similarity": comparison[
                        "product_similarity"
                    ],
                    "defect_similarity": comparison[
                        "defect_similarity"
                    ],
                    "description_similarity": comparison[
                        "description_similarity"
                    ],
                }
            )

    matches.sort(
        key=lambda item: item["similarity_score"],
        reverse=True,
    )

    return matches[:limit]