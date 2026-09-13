
from uuid import uuid4
from app.models.audit import AuditLog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintUpdate,
)


router = APIRouter(
    prefix="/api/complaints",
    tags=["Complaints"],
)


@router.post(
    "",
    response_model=ComplaintResponse,
    status_code=201,
)
def create_complaint(
    complaint_data: ComplaintCreate,
    db: Session = Depends(get_db),
):
    complaint = Complaint(
        complaint_number=f"CMP-{uuid4().hex[:8].upper()}",
        **complaint_data.model_dump(),
    )

    db.add(complaint)
    db.flush()

    audit_log = AuditLog(
        complaint_id=complaint.id,
        action="Complaint Created",
        actor="QA User",
        details=f"Complaint {complaint.complaint_number} was logged after QA review.",
    )
    db.add(audit_log)

    db.commit()
    db.refresh(complaint)

    return complaint


@router.get(
    "",
    response_model=list[ComplaintResponse],
)
def get_complaints(
    db: Session = Depends(get_db),
):
    return (
        db.query(Complaint)
        .order_by(Complaint.created_at.desc())
        .all()
    )


@router.get(
    "/{complaint_id}",
    response_model=ComplaintResponse,
)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    return complaint


@router.patch(
    "/{complaint_id}",
    response_model=ComplaintResponse,
)
def update_complaint(
    complaint_id: int,
    complaint_data: ComplaintUpdate,
    db: Session = Depends(get_db),
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    update_data = complaint_data.model_dump(
        exclude_unset=True
    )

    changes = []

    for field, new_value in update_data.items():
        old_value = getattr(complaint, field)

        if old_value != new_value:
            changes.append(
                f"{field}: {old_value} -> {new_value}"
            )

            setattr(complaint, field, new_value)

    if changes:
        audit_log = AuditLog(
            complaint_id=complaint.id,
            action="Complaint Updated",
            actor="QA User",
            details="; ".join(changes),
        )

        db.add(audit_log)

    db.commit()
    db.refresh(complaint)

    return complaint


@router.get(
    "/{complaint_id}/audit",
)
def get_complaint_audit(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    return (
        db.query(AuditLog)
        .filter(AuditLog.complaint_id == complaint_id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )


from app.ai.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

@router.post(
    "/{complaint_id}/generate-response",
)
def generate_complaint_response(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    llm = get_llm()
    
    system_prompt = "You are a professional Quality Assurance representative at AIVOA, a pharmaceutical manufacturing company. Your job is to write a highly professional, empathetic, and regulatory-compliant email to a customer acknowledging their complaint."
    
    user_prompt = f"""
Please draft an email response to the customer regarding the following complaint.
Acknowledge the issue, provide the complaint number for their reference, and assure them it is under investigation. If a sample is available but not yet received, kindly request it.

Complaint Details:
Complaint Number: {complaint.complaint_number}
Customer Name: {complaint.customer_name or 'Valued Customer'}
Product: {complaint.product_name} (Batch: {complaint.batch_number or 'Unknown'})
Issue: {complaint.defect_category}
Description: {complaint.description}

Keep the email concise, polite, and professional. Do not admit fault, but apologize for any inconvenience caused.
    """

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # Ensure we record that AI drafted a response in the audit log
        audit_log = AuditLog(
            complaint_id=complaint.id,
            action="AI Email Drafted",
            actor="System (AI)",
            details="AI generated a customer response draft.",
        )
        db.add(audit_log)
        db.commit()

        return {"draft": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



