from backend import create_app, db
from backend.models.role import Role
from backend.models.user import User
from backend.models.vendor import Vendor
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app()
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        roles = [
            Role(name='manager'),
            Role(name='staff'), 
            Role(name='vendor')
        ]
        for role in roles:
            db.session.add(role)
        db.session.commit()
        
        manager_role = Role.query.filter_by(name='manager').first()
        staff_role = Role.query.filter_by(name='staff').first()
        vendor_role = Role.query.filter_by(name='vendor').first()
        
        users = [
            User(
                email='manager@vendorsync.com',
                password_hash=generate_password_hash('password123'),
                first_name='John',
                last_name='Manager',
                role_id=manager_role.id,
                is_active=True
            ),
            User(
                email='staff@vendorsync.com', 
                password_hash=generate_password_hash('password123'),
                first_name='Jane',
                last_name='Staff',
                role_id=staff_role.id,
                is_active=True
            ),
            User(
                email='vendor@vendorsync.com',
                password_hash=generate_password_hash('password123'),
                first_name='Bob',
                last_name='Vendor',
                role_id=vendor_role.id,
                is_active=True
            )
        ]
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        vendors = [
            Vendor(
                name='ABC Construction Supplies',
                contact_email='vendor@vendorsync.com',
                contact_phone='+254712345678',
                address='123 Main Street',
                city='Nairobi',
                state='Nairobi',
                country='Kenya',
                business_type='Construction Materials',
                description='Leading supplier of construction materials',
                is_approved=True,
                tax_id='TAX123456'
            ),
            Vendor(
                name='BuildMax Hardware',
                contact_email='info@buildmax.com', 
                contact_phone='+254723456789',
                address='456 Industrial Area',
                city='Nairobi',
                state='Nairobi', 
                country='Kenya',
                business_type='Hardware Supplies',
                description='Quality hardware and tools',
                is_approved=True,
                tax_id='TAX789012'
            )
        ]
        for vendor in vendors:
            db.session.add(vendor)
        db.session.commit()
        
        print("Database seeded successfully!")
        print("Manager: manager@vendorsync.com / password123")
        print("Staff: staff@vendorsync.com / password123") 
        print("Vendor: vendor@vendorsync.com / password123")

if __name__ == '__main__':
    seed_database()