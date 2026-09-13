
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class ComplaintCreate(BaseModel):
    """
    Data required when creating a new customer complaint.
    """

    customer_name: str
    contact_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    country: str | None = None

    product_name: str
    product_type: str | None = None
    strength: str | None = None
    dosage_form: str | None = None

    batch_number: str | None = None
    manufacturing_date: date | None = None
    expiry_date: date | None = None

    affected_quantity: str | None = None
    defect_category: str | None = None
    complaint_date: date | None = None
    source: str | None = None

    description: str

    manufacturing_site: str | None = None
    packaging_type: str | None = None
    storage_condition: str | None = None
    sample_available: str | None = None
    ai_risk_level: str | None = None


class ComplaintUpdate(BaseModel):
    """
    Data used when updating an existing complaint.

    All fields are optional because the user should be
    able to update only the field that needs correction.
    """

    customer_name: str | None = None
    contact_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    country: str | None = None

    product_name: str | None = None
    product_type: str | None = None
    strength: str | None = None
    dosage_form: str | None = None

    batch_number: str | None = None
    manufacturing_date: date | None = None
    expiry_date: date | None = None

    affected_quantity: str | None = None
    defect_category: str | None = None
    complaint_date: date | None = None
    source: str | None = None

    description: str | None = None

    manufacturing_site: str | None = None
    packaging_type: str | None = None
    storage_condition: str | None = None
    sample_available: str | None = None


class ComplaintResponse(ComplaintCreate):
    """
    Data returned by the API after creating,
    retrieving, or updating a complaint.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    complaint_number: str
    status: str
    created_at: datetime
    updated_at: datetime
