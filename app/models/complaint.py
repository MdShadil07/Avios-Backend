from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    complaint_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Open",
        nullable=False,
    )

    customer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    contact_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    product_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    strength: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    dosage_form: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    batch_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    manufacturing_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    expiry_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    affected_quantity: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    defect_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    complaint_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    manufacturing_site: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    packaging_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    storage_condition: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    sample_available: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    ai_risk_level: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )