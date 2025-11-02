from backend.app import app, db
from backend.models.role import Role
from backend.models.user import User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create all database tables
        print("Creating database tables...")
        db.create_all()
        
        # Create default roles if they don't exist
        roles = [
            {'name': 'ADMIN', 'description': 'Administrator'},
            {'name': 'VENDOR', 'description': 'Vendor'},
            {'name': 'CLIENT', 'description': 'Client'},
            {'name': 'STAFF', 'description': 'Staff'}
        ]
        
        for role_data in roles:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(**role_data)
                db.session.add(role)
        
        # Create demo users if they don't exist
        demo_users = [
            {
                'email': 'admin@vendorsync.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'ADMIN'
            },
            {
                'email': 'vendor@example.com',
                'password': 'vendor123',
                'first_name': 'Vendor',
                'last_name': 'User',
                'role': 'VENDOR'
            },
            {
                'email': 'client@example.com',
                'password': 'client123',
                'first_name': 'Client',
                'last_name': 'User',
                'role': 'CLIENT'
            }
        ]
        
        for user_data in demo_users:
            if not User.query.filter_by(email=user_data['email']).first():
                role = Role.query.filter_by(name=user_data['role']).first()
                if role:
                    user = User(
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role_id=role.id
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
        
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
