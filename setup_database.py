from backend import create_app, db
from backend.models.role import Role
from backend.models.user import User
from backend.models.vendor import Vendor
from werkzeug.security import generate_password_hash

def setup_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create roles if they don't exist
        roles = ['manager', 'staff', 'vendor']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name)
                db.session.add(role)
        
        db.session.commit()
        
        # Get roles
        manager_role = Role.query.filter_by(name='manager').first()
        staff_role = Role.query.filter_by(name='staff').first()
        vendor_role = Role.query.filter_by(name='vendor').first()
        
        # Create test users
        test_users = [
            {
                'email': 'manager@vendorsync.com',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Manager',
                'role': manager_role
            },
            {
                'email': 'staff@vendorsync.com',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Staff',
                'role': staff_role
            },
            {
                'email': 'vendor@vendorsync.com',
                'password': 'password123',
                'first_name': 'Bob',
                'last_name': 'Vendor',
                'role': vendor_role
            }
        ]
        
        for user_data in test_users:
            if not User.query.filter_by(email=user_data['email']).first():
                user = User(
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role_id=user_data['role'].id,
                    is_active=True
                )
                db.session.add(user)
        
        db.session.commit()
        
        # Create test vendors
        vendors = [
            {
                'name': 'ABC Construction Supplies',
                'contact_email': 'vendor@vendorsync.com',
                'contact_phone': '+254712345678',
                'business_type': 'Construction Materials',
                'description': 'Leading supplier of construction materials',
                'is_approved': True
            },
            {
                'name': 'BuildMax Hardware',
                'contact_email': 'info@buildmax.com',
                'contact_phone': '+254723456789',
                'business_type': 'Hardware Supplies',
                'description': 'Quality hardware and tools',
                'is_approved': True
            }
        ]
        
        for vendor_data in vendors:
            if not Vendor.query.filter_by(contact_email=vendor_data['contact_email']).first():
                vendor = Vendor(**vendor_data)
                db.session.add(vendor)
        
        db.session.commit()
        
        print("✅ Database setup completed successfully!")
        print("\n📋 Test Accounts:")
        print("Manager: manager@vendorsync.com / password123")
        print("Staff: staff@vendorsync.com / password123")
        print("Vendor: vendor@vendorsync.com / password123")
        
        print("\n🏪 Test Vendors:")
        vendors = Vendor.query.all()
        for vendor in vendors:
            print(f"{vendor.name} - {vendor.contact_email}")

if __name__ == '__main__':
    setup_database()