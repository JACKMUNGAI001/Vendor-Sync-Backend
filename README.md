# VendorSync Backend

Construction Procurement Management System - REST API Backend

##  Quick Start

```bash
# Clone repository
git clone <repository-url>
cd Vendor-Sync-Backend

# Install dependencies
pip install flask flask-restful flask-jwt-extended flask-sqlalchemy flask-marshmallow flask-cors

# Run Flask backend
cd backend
python app.py
```

Server runs on `http://localhost:5000`

##  Authentication

### Login Endpoint
```
POST /auth/login
Content-Type: application/json

{
  "email": "admin@vendorsync.com",
  "password": "admin123"
}
```

### Demo Accounts
- **Manager**: `admin@vendorsync.com` / `admin123`
- **Vendor**: `vendor@example.com` / `vendor123`  
- **Client**: `client@example.com` / `client123`

### Response Format
```json
{
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "admin@vendorsync.com",
    "role": "manager",
    "name": "Admin User",
    "first_name": "Admin",
    "last_name": "User"
  }
}
```

##  API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | User authentication |
| GET/POST | `/users` | User management |
| GET | `/dashboard` | Dashboard analytics |
| GET/POST | `/orders` | Order management |
| GET | `/orders/vendor` | Vendor orders |
| GET | `/quotes` | Quote management |
| GET | `/documents` | Document management |
| GET | `/search` | Global search |

##  Tech Stack

- **Framework**: Flask + Flask-RESTful
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **CORS**: Enabled for frontend integration
- **Security**: Input validation and error handling

##  Project Structure

```
Vendor-Sync-Backend/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── instance/
│   │   └── vendorsync.db   # SQLite database
│   └── models/             # Database models
├── src/                    # Node.js implementation (alternative)
├── package.json            # Node.js dependencies
└── README.md
```

##  Configuration

```python
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vendorsync.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-secret-key'
```

##  CORS Setup

Configured for:
- `http://localhost:3000` (React development)
- `https://chic-kashata-589433.netlify.app` (Production frontend)

##  Development

```bash
# Start development server
cd backend
python app.py

# Database will be created automatically
# Demo data is built-in for testing
```

##  Deployment

1. Update `JWT_SECRET_KEY` in production
2. Configure production database URI
3. Set `debug=False` for production
4. Deploy to your preferred platform

##  Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test
3. Commit: `git commit -m "Add new feature"`
4. Push: `git push origin feature/new-feature`
5. Create Pull Request

##  License

MIT License - see LICENSE file for details