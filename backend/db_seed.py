from backend import create_app, db
from backend.models.user import User
from backend.models.role import Role
from backend.models.vendor import Vendor
from backend.models.purchase_order import PurchaseOrder
from backend.models.requirement import Requirement
from backend.models.quote import Quote
from datetime import datetime, timedelta

def seed_roles():
    roles = ['manager', 'staff', 'vendor']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    db.session.commit()

def seed_users():
    manager_role = Role.query.filter_by(name='manager').first()
    staff_role = Role.query.filter_by(name='staff').first()
    vendor_role = Role.query.filter_by(name='vendor').first()

    manager = User(
        email='manager@example.com',
        first_name='Default',
        last_name='Manager',
        role_id=manager_role.id if manager_role else None
    )
    manager.set_password('password123')
    db.session.add(manager)

    staff = User(
        email='staff@example.com',
        first_name='Default',
        last_name='Staff',
        role_id=staff_role.id if staff_role else None
    )
    staff.set_password('password123')
    db.session.add(staff)

    vendor_user = User(
        email='vendor@example.com',
        first_name='Default',
        last_name='Vendor',
        role_id=vendor_role.id if vendor_role else None
    )
    vendor_user.set_password('password123')
    db.session.add(vendor_user)

    db.session.commit()

def seed_vendors():
    if not Vendor.query.filter_by(name='Default Vendor').first():
        vendor = Vendor(
            name='Default Vendor',
            email='vendor@example.com',
            phone='0000000000',
            address='123 Vendor St',
            company_name='Vendor Co',
            contact_person='Vendor Contact',
            is_verified=True
        )
        db.session.add(vendor)
        db.session.commit()

def seed_data():
    manager = User.query.filter_by(email='manager@example.com').first()
    staff = User.query.filter_by(email='staff@example.com').first()
    vendor = Vendor.query.filter_by(name='Default Vendor').first()

    if manager and staff and vendor:
        # Seed Requirements
        if not Requirement.query.filter_by(item_name='Steel Rods - Grade 60').first():
            req1 = Requirement(
                item_name='Steel Rods - Grade 60',
                quantity=1000,
                specifications='High-strength steel rods for construction',
                manager_id=manager.id
            )
            db.session.add(req1)

        if not Requirement.query.filter_by(item_name='Cement - Type I Portland').first():
            req2 = Requirement(
                item_name='Cement - Type I Portland',
                quantity=500,
                specifications='Standard Portland cement',
                manager_id=manager.id
            )
            db.session.add(req2)
        db.session.commit()

        # Seed Purchase Orders
        if not PurchaseOrder.query.filter_by(order_number='PO-2025-001').first():
            po1 = PurchaseOrder(
                order_number='PO-2025-001',
                status='pending',
                manager_id=manager.id,
                vendor_id=vendor.id,
                created_at=datetime.now() - timedelta(days=5)
            )
            db.session.add(po1)

        if not PurchaseOrder.query.filter_by(order_number='PO-2025-002').first():
            po2 = PurchaseOrder(
                order_number='PO-2025-002',
                status='in progress',
                manager_id=manager.id,
                vendor_id=vendor.id,
                created_at=datetime.now() - timedelta(days=2)
            )
            db.session.add(po2)
        db.session.commit()

        # Seed Quotes
        if not Quote.query.filter_by(order_id=po1.id, vendor_id=vendor.id).first():
            quote1 = Quote(
                vendor_id=vendor.id,
                order_id=po1.id,
                price=45000.00,
                status='pending',
                notes='Includes 7-day delivery',
                created_at=datetime.now() - timedelta(days=4)
            )
            db.session.add(quote1)
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_roles()
        seed_users()
        seed_vendors()
        seed_data()
        print("Database seeded successfully.")
