from backend import create_app, db
from backend.models.user import User
from backend.models.role import Role
from backend.models.vendor import Vendor
from backend.models.vendor_category import VendorCategory
from backend.models.purchase_order import PurchaseOrder
from backend.models.requirement import Requirement
from backend.models.quote import Quote
from backend.models.order_assignment import OrderAssignment
from datetime import datetime, timedelta

def seed_roles():
    roles = ['manager', 'staff', 'vendor']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
            print(f"✓ Created role: {role_name}")
    db.session.commit()
    print("✓ Roles seeded successfully")

def seed_users():
    manager_role = Role.query.filter_by(name='manager').first()
    staff_role = Role.query.filter_by(name='staff').first()
    vendor_role = Role.query.filter_by(name='vendor').first()

    if not User.query.filter_by(email='manager@example.com').first():
        manager = User(
            email='manager@example.com',
            first_name='John',
            last_name='Manager',
            phone='0700000001',
            role_id=manager_role.id,
            is_active=True
        )
        manager.set_password('password123')
        db.session.add(manager)
        print("✓ Created manager user: manager@example.com")

    staff_users = [
        {'email': 'staff@example.com', 'first_name': 'Jane', 'last_name': 'Staff', 'phone': '0700000002'},
        {'email': 'staff2@example.com', 'first_name': 'Mike', 'last_name': 'Worker', 'phone': '0700000003'}
    ]
    
    for staff_data in staff_users:
        if not User.query.filter_by(email=staff_data['email']).first():
            staff = User(
                email=staff_data['email'],
                first_name=staff_data['first_name'],
                last_name=staff_data['last_name'],
                phone=staff_data['phone'],
                role_id=staff_role.id,
                is_active=True
            )
            staff.set_password('password123')
            db.session.add(staff)
            print(f"✓ Created staff user: {staff_data['email']}")

    vendor_users = [
        {'email': 'vendor@example.com', 'first_name': 'Sarah', 'last_name': 'Vendor', 'phone': '0700000004'},
        {'email': 'vendor2@example.com', 'first_name': 'David', 'last_name': 'Supplier', 'phone': '0700000005'}
    ]
    
    for vendor_data in vendor_users:
        if not User.query.filter_by(email=vendor_data['email']).first():
            vendor_user = User(
                email=vendor_data['email'],
                first_name=vendor_data['first_name'],
                last_name=vendor_data['last_name'],
                phone=vendor_data['phone'],
                role_id=vendor_role.id,
                is_active=True
            )
            vendor_user.set_password('password123')
            db.session.add(vendor_user)
            print(f"✓ Created vendor user: {vendor_data['email']}")

    db.session.commit()
    print("✓ Users seeded successfully")

def seed_vendor_categories():
    categories = [
        'Steel & Metal',
        'Cement & Concrete',
        'Lumber & Wood',
        'Electrical Supplies',
        'Plumbing Supplies',
        'Hardware & Tools'
    ]
    
    for cat_name in categories:
        if not VendorCategory.query.filter_by(name=cat_name).first():
            category = VendorCategory(name=cat_name)
            db.session.add(category)
            print(f"✓ Created category: {cat_name}")
    
    db.session.commit()
    print("✓ Vendor categories seeded successfully")

def seed_vendors():
    steel_category = VendorCategory.query.filter_by(name='Steel & Metal').first()
    cement_category = VendorCategory.query.filter_by(name='Cement & Concrete').first()
    lumber_category = VendorCategory.query.filter_by(name='Lumber & Wood').first()

    vendors_data = [
        {
            'name': 'Premium Steel Co',
            'email': 'vendor@example.com',
            'phone': '0700000004',
            'address': '123 Industrial Area, Nairobi',
            'company_name': 'Premium Steel Co Ltd',
            'contact_person': 'Sarah Vendor',
            'category_id': steel_category.id if steel_category else None,
            'is_verified': True
        },
        {
            'name': 'Best Cement Suppliers',
            'email': 'vendor2@example.com',
            'phone': '0700000005',
            'address': '456 Construction Ave, Nairobi',
            'company_name': 'Best Cement Suppliers Ltd',
            'contact_person': 'David Supplier',
            'category_id': cement_category.id if cement_category else None,
            'is_verified': True
        },
        {
            'name': 'Quality Lumber Ltd',
            'email': 'lumber@example.com',
            'phone': '0700000006',
            'address': '789 Woodwork Street, Nairobi',
            'company_name': 'Quality Lumber Limited',
            'contact_person': 'Robert Wood',
            'category_id': lumber_category.id if lumber_category else None,
            'is_verified': False
        }
    ]

    for vendor_data in vendors_data:
        if not Vendor.query.filter_by(email=vendor_data['email']).first():
            vendor = Vendor(**vendor_data)
            db.session.add(vendor)
            status = "verified" if vendor_data['is_verified'] else "unverified"
            print(f"✓ Created {status} vendor: {vendor_data['name']}")

    db.session.commit()
    print("✓ Vendors seeded successfully")

def seed_data():
    manager = User.query.filter_by(email='manager@example.com').first()
    staff1 = User.query.filter_by(email='staff@example.com').first()
    staff2 = User.query.filter_by(email='staff2@example.com').first()
    vendor1 = Vendor.query.filter_by(email='vendor@example.com').first()
    vendor2 = Vendor.query.filter_by(email='vendor2@example.com').first()

    if not (manager and staff1 and vendor1):
        print("⚠ Required users not found. Skipping data seeding.")
        return

    requirements_data = [
        {
            'item_name': 'Steel Rods - Grade 60',
            'quantity': 1000,
            'specifications': 'High-strength steel rods, 12mm diameter, 6m length',
            'manager_id': manager.id
        },
        {
            'item_name': 'Cement - Type I Portland',
            'quantity': 500,
            'specifications': 'Standard Portland cement, 50kg bags',
            'manager_id': manager.id
        },
        {
            'item_name': 'Construction Sand',
            'quantity': 2000,
            'specifications': 'Clean construction sand, delivered in bulk',
            'manager_id': manager.id
        }
    ]

    for req_data in requirements_data:
        if not Requirement.query.filter_by(item_name=req_data['item_name']).first():
            req = Requirement(**req_data)
            db.session.add(req)
            print(f"✓ Created requirement: {req_data['item_name']}")

    db.session.commit()

    orders_data = [
        {
            'order_number': 'PO-2025-001',
            'status': 'pending',
            'manager_id': manager.id,
            'vendor_id': vendor1.id,
            'created_at': datetime.now() - timedelta(days=5)
        },
        {
            'order_number': 'PO-2025-002',
            'status': 'ordered',
            'manager_id': manager.id,
            'vendor_id': vendor2.id,
            'created_at': datetime.now() - timedelta(days=3)
        },
        {
            'order_number': 'PO-2025-003',
            'status': 'delivered',
            'manager_id': manager.id,
            'vendor_id': vendor1.id,
            'created_at': datetime.now() - timedelta(days=10)
        }
    ]

    created_orders = []
    for order_data in orders_data:
        if not PurchaseOrder.query.filter_by(order_number=order_data['order_number']).first():
            order = PurchaseOrder(**order_data)
            db.session.add(order)
            created_orders.append(order)
            print(f"✓ Created order: {order_data['order_number']}")

    db.session.commit()

    if created_orders:
        po1 = PurchaseOrder.query.filter_by(order_number='PO-2025-001').first()
        po2 = PurchaseOrder.query.filter_by(order_number='PO-2025-002').first()
        po3 = PurchaseOrder.query.filter_by(order_number='PO-2025-003').first()

        quotes_data = [
            {
                'vendor_id': vendor1.id,
                'order_id': po1.id if po1 else None,
                'price': 45000.00,
                'status': 'pending',
                'notes': 'Includes 7-day delivery and installation',
                'created_at': datetime.now() - timedelta(days=4)
            },
            {
                'vendor_id': vendor2.id,
                'order_id': po2.id if po2 else None,
                'price': 28500.00,
                'status': 'accepted',
                'notes': 'Bulk discount applied',
                'created_at': datetime.now() - timedelta(days=2)
            },
            {
                'vendor_id': vendor1.id,
                'order_id': po3.id if po3 else None,
                'price': 67000.00,
                'status': 'accepted',
                'notes': 'Premium quality materials',
                'created_at': datetime.now() - timedelta(days=9)
            }
        ]

        for quote_data in quotes_data:
            if quote_data['order_id']:
                existing = Quote.query.filter_by(
                    order_id=quote_data['order_id'],
                    vendor_id=quote_data['vendor_id']
                ).first()
                if not existing:
                    quote = Quote(**quote_data)
                    db.session.add(quote)
                    print(f"✓ Created quote for order {quote_data['order_id']}")

        db.session.commit()

    if staff1 and staff2 and created_orders:
        po2 = PurchaseOrder.query.filter_by(order_number='PO-2025-002').first()
        po3 = PurchaseOrder.query.filter_by(order_number='PO-2025-003').first()

        if po2 and not OrderAssignment.query.filter_by(order_id=po2.id, staff_id=staff1.id).first():
            assignment1 = OrderAssignment(
                order_id=po2.id,
                staff_id=staff1.id,
                status='assigned',
                assigned_at=datetime.now() - timedelta(days=2)
            )
            db.session.add(assignment1)
            print(f"✓ Assigned order {po2.order_number} to {staff1.first_name}")

        if po3 and staff2 and not OrderAssignment.query.filter_by(order_id=po3.id, staff_id=staff2.id).first():
            assignment2 = OrderAssignment(
                order_id=po3.id,
                staff_id=staff2.id,
                status='completed',
                assigned_at=datetime.now() - timedelta(days=9)
            )
            db.session.add(assignment2)
            print(f"✓ Assigned order {po3.order_number} to {staff2.first_name}")

        db.session.commit()

    print("✓ All data seeded successfully")

def seed_all():
    print("\n" + "="*50)
    print("🌱 Starting database seeding...")
    print("="*50 + "\n")
    
    try:
        seed_roles()
        seed_users()
        seed_vendor_categories()
        seed_vendors()
        seed_data()
        
        print("\n" + "="*50)
        print("✅ Database seeding completed successfully!")
        print("="*50)
        print("\nDefault login credentials:")
        print("  Manager: manager@example.com / password123")
        print("  Staff: staff@example.com / password123")
        print("  Vendor: vendor@example.com / password123")
        print("="*50 + "\n")
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_all()