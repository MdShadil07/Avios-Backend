from datetime import date

from app.db.database import Base, SessionLocal, engine
from app.models.complaint import Complaint


def seed_database():
    # Make sure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Prevent duplicate seed data if the script is run again
        existing = (
            db.query(Complaint)
            .filter(
                Complaint.complaint_number == "CMP-2026-0003"
            )
            .first()
        )

        if existing:
            print("Seed complaint already exists.")
            return

        complaint = Complaint(
            complaint_number="CMP-2026-0003",
            status="Closed",

            customer_name="Global Health Laboratories",
            contact_name="Dr. Michael Rao",
            email="quality@globalhealthlabs.com",
            phone="+1-555-0198",
            country="United States",

            product_name="Metformin Hydrochloride API",
            product_type="API",
            strength=None,
            dosage_form=None,

            batch_number="MF-2426-088",
            manufacturing_date=date(2026, 6, 25),
            expiry_date=date(2028, 6, 24),

            affected_quantity="40 kg",
            defect_category="Foreign Particulate Matter",
            complaint_date=date(2026, 8, 28),
            source="Email",

            description=(
                "During incoming quality inspection, dark particulate "
                "matter was observed inside HDPE drums containing "
                "Metformin Hydrochloride API. Approximately 40 kg of "
                "material from the batch was placed on hold pending "
                "investigation."
            ),

            manufacturing_site="Hyderabad Manufacturing Site",
            packaging_type="HDPE drums",
            storage_condition="Store in a cool, dry place",
            sample_available="Yes",
        )

        db.add(complaint)
        db.commit()

        print("Seed complaint created successfully.")
        print("Complaint Number: CMP-2026-0003")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()