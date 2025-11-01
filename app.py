from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

# Enable CORS for specific origins
CORS(app, origins=["http://localhost:3000", "https://chic-kashata-589433.netlify.app"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Demo users database
USERS_DB = {
    'admin@vendorsync.com': {
        'id': 1, 'password': 'admin123', 'role': 'manager', 
        'first_name': 'Admin', 'last_name': 'User'
    },
    'vendor@example.com': {
        'id': 2, 'password': 'vendor123', 'role': 'vendor',
        'first_name': 'Vendor', 'last_name': 'User'
    },
    'client@example.com': {
        'id': 3, 'password': 'client123', 'role': 'client',
        'first_name': 'Client', 'last_name': 'User'
    }
}

# Counter for new user IDs
NEXT_USER_ID = 4

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400
    
    email = data['email'].lower()
    password = data['password']
    
    if email not in USERS_DB or USERS_DB[email]['password'] != password:
        return jsonify({'message': 'Invalid email or password'}), 401
    
    user = USERS_DB[email]
    token = create_access_token(identity={'user_id': user['id'], 'role': user['role']})
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'email': email,
            'role': user['role'],
            'name': f"{user['first_name']} {user['last_name']}",
            'first_name': user['first_name'],
            'last_name': user['last_name']
        }
    }), 200

@app.route('/users', methods=['POST'])
def register():
    global NEXT_USER_ID
    data = request.get_json()
    
    required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
    for field in required_fields:
        if not data or not data.get(field):
            return jsonify({'message': f'{field} is required'}), 400
    
    email = data['email'].lower()
    
    if email in USERS_DB:
        return jsonify({'message': 'User already exists'}), 400
    
    # Create new user
    USERS_DB[email] = {
        'id': NEXT_USER_ID,
        'password': data['password'],
        'role': data['role'].lower(),
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'phone': data.get('phone', ''),
        'company_name': data.get('company_name', '')
    }
    
    user_id = NEXT_USER_ID
    NEXT_USER_ID += 1
    
    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user_id,
            'email': email,
            'role': data['role']
        }
    }), 201

if __name__ == '__main__':
    print("Starting Vendor Sync Backend...")
    print("Demo accounts available:")
    print("- admin@vendorsync.com / admin123 (manager)")
    print("- vendor@example.com / vendor123 (vendor)")
    print("- client@example.com / client123 (client)")
    app.run(debug=True, port=5000, host='0.0.0.0')