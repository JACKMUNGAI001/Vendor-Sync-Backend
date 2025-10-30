from backend import db
from backend.models import Role, User, Vendor, PurchaseOrder, Quote
from werkzeug.security import generate_password_hash

def auto_seed_database():
    print("Resetting and seeding database...")
    try:
        db.drop_all()
        db.create_all()

        manager_role = Role(name="Manager")
        staff_role = Role(name="Staff")
        vendor_role = Role(name="Vendor")
        db.session.add_all([manager_role, staff_role, vendor_role])
        db.session.commit()

        manager_user = User(
            name="Manager User",
            email="manager@vendorsync.com",
            password_hash=generate_password_hash("password123"),
            role_id=manager_role.id,
        )
        staff_user = User(
            name="Staff User",
            email="staff@vendorsync.com",
            password_hash=generate_password_hash("password123"),
            role_id=staff_role.id,
        )
        vendor_user = User(
            name="Vendor User",
            email="vendor@vendorsync.com",
            password_hash=generate_password_hash("password123"),
            role_id=vendor_role.id,
        )
        db.session.add_all([manager_user, staff_user, vendor_user])
        db.session.commit()

        vendor1 = Vendor(
            user_id=vendor_user.id,
            name="ABC Construction Supplies",
            contact_email="vendor@vendorsync.com",
            contact_phone="+254712345678",
            address="123 Main Street",
            city="Nairobi",
            state="Nairobi",
            country="Kenya",
            business_type="Construction Materials",
            description="Leading supplier of construction materials",
            is_approved=True,
            tax_id="TAX123456",
            payment_terms="Net 30",
            rating=0,
            total_orders=0,
        )

        vendor2 = Vendor(
            user_id=vendor_user.id,
            name="BuildMax Hardware",
            contact_email="info@buildmax.com",
            contact_phone="+254723456789",
            address="456 Industrial Area",
            city="Nairobi",
            state="Nairobi",
            country="Kenya",
            business_type="Hardware Supplies",
            description="Quality hardware and tools",
            is_approved=True,
            tax_id="TAX789012",
            payment_terms="Net 30",
            rating=0,
            total_orders=0,
        )
        db.session.add_all([vendor1, vendor2])
        db.session.commit()

        po1 = PurchaseOrder(
            title="Office Renovation Materials",
            description="Purchase of cement, paint, and roofing sheets",
            status="Pending",
            created_by=manager_user.id,
        )
        po2 = PurchaseOrder(
            title="Electrical Wiring Supplies",
            description="Purchase of cables and lighting fixtures",
            status="Approved",
            created_by=staff_user.id,
        )
        db.session.add_all([po1, po2])
        db.session.commit()

        quote1 = Quote(
            purchase_order_id=po1.id,
            vendor_id=vendor1.id,
            price=50000,
            status="Pending",
        )
        quote2 = Quote(
            purchase_order_id=po2.id,
            vendor_id=vendor2.id,
            price=75000,
            status="Accepted",
        )
        db.session.add_all([quote1, quote2])
        db.session.commit()

        print("Database seeded successfully!")
        print("Manager: manager@vendorsync.com / password123")
        print("Staff: staff@vendorsync.com / password123")
        print("Vendor: vendor@vendorsync.com / password123")

    except Exception as e:
        print(f"Seeding error: {e}")
        db.session.rollback()
