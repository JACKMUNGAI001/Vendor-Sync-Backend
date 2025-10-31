from backend import create_app, db
from backend.models.user import User
from backend.models.role import Role
from backend.models.vendor import Vendor

def seed_roles():
    roles = ['manager', 'staff', 'vendor']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    db.session.commit()

def seed_users():
    if not User.query.filter_by(email='manager@example.com').first():
        manager_role = Role.query.filter_by(name='manager').first()
        manager = User(
            email='manager@example.com',
            first_name='Default',
            last_name='Manager',
            role=manager_role
        )
        manager.set_password('password123')
        db.session.add(manager)

    if not User.query.filter_by(email='staff@example.com').first():
        staff_role = Role.query.filter_by(name='staff').first()
        staff = User(
            email='staff@example.com',
            first_name='Default',
            last_name='Staff',
            role=staff_role
        )
        staff.set_password('password123')
        db.session.add(staff)

    if not User.query.filter_by(email='vendor@example.com').first():
        vendor_role = Role.query.filter_by(name='vendor').first()
        vendor_user = User(
            email='vendor@example.com',
            first_name='Default',
            last_name='Vendor',
            role=vendor_role
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

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_roles()
        seed_users()
        seed_vendors()
        print("Database seeded successfully.")
