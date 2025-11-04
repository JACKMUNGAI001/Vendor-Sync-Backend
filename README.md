

# Vendor-Sync Backend

A Flask RESTful API for vendor management system with full authentication, role-based access control, and comprehensive CRUD operations. Developed by Maureen, Wayne, and Jackson as a capstone project.

## Features

- JWT Authentication system with secure token management
- Role-Based Access Control (Admin, Manager, Vendor, Staff)
- RESTful API design with Flask-RESTful
- Comprehensive CRUD operations with pagination
- Image upload and management with Cloudinary
- Email integration with SendGrid for notifications
- Search functionality with Algolia indexing
- Data validation with Marshmallow schemas
- API documentation with Swagger UI/OpenAPI
- Database migrations with Alembic

## Tech Stack

- Python 3.10+
- Flask and Flask-RESTful
- SQLAlchemy ORM
- PostgreSQL database
- Alembic for database migrations
- Marshmallow for serialization/validation
- JWT for authentication
- Cloudinary for image storage
- SendGrid for email services
- Algolia for search indexing
- Swagger UI for API documentation
- Gunicorn for production server

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── vendor.py
│   │   ├── vendor_category.py
│   │   ├── requirement.py
│   │   ├── quote.py
│   │   ├── order.py
│   │   └── document.py
│   ├── resources/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── vendors.py
│   │   ├── vendor_categories.py
│   │   ├── requirements.py
│   │   ├── quotes.py
│   │   ├── orders.py
│   │   └── documents.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── vendor_schema.py
│   │   ├── requirement_schema.py
│   │   ├── quote_schema.py
│   │   └── order_schema.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── email_service.py
│   │   ├── cloudinary_service.py
│   │   ├── algolia_service.py
│   │   └── swagger_service.py
│   └── utils/
│       ├── decorators.py
│       ├── validators.py
│       └── date_utils.py
├── migrations/
├── tests/
├── config.py
├── requirements.txt
├── wsgi.py
├── db_seed.py
└── README.md
```

## Team Contributions

### Jackson
- Authentication System: JWT implementation, login endpoints
- User Management: User CRUD operations, role assignment
- Role-Based Access Control: Permission system and decorators
- Dashboard API: Role-based data aggregation
- Database Models: User and Role models with relationships

### Wayne
- Order Management: Full CRUD operations for purchase orders
- Order Assignments: Staff assignment system
- Status Workflow: Order status state management
- Pagination: API pagination implementation
- Database Models: PurchaseOrder and OrderAssignment models

### Maureen
- Vendor Management: Vendor registration and profile management
- Quote System: Quote submission, review, and acceptance
- Search Integration: Algolia setup and search endpoints
- Document Management: Cloudinary file upload system
- Email Notifications: SendGrid integration for business workflows
- Swagger UI: Comprehensive API documentation
- Date Utilities: Consistent date handling across API

## Prerequisites

- Python 3.10+
- PostgreSQL database
- Cloudinary account
- SendGrid account
- Algolia account

## Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit .env with your configuration:
```
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/vendor_sync
JWT_SECRET_KEY=your_jwt_secret

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# SendGrid
SENDGRID_API_KEY=your_sendgrid_key
EMAIL_FROM=no-reply@vendorsync.com

# Algolia
ALGOLIA_APP_ID=your_algolia_app_id
ALGOLIA_API_KEY=your_algolia_api_key
ALGOLIA_INDEX_NAME=vendors

# Swagger
SWAGGER_URL=/api/docs
API_URL=/api/swagger.json
```

## Database Setup

1. Create PostgreSQL database:
```bash
createdb vendor_sync
```

2. Run migrations:
```bash
flask db upgrade
```

3. Seed initial data (roles, admin user):
```bash
python db_seed.py
```

## Running the Application

### Development
```bash
flask run --host=0.0.0.0 --port=5000
```

### Production
```bash
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers=4
```

## API Documentation

Swagger UI documentation is available at `/api/docs` when running the application. This includes:

- Interactive API explorer
- Request/response schemas
- Authentication requirements
- Example requests for all endpoints

## Authentication

The API uses JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

Tokens are automatically refreshed, and endpoints are protected based on user roles.

## Role-Based Access Control

### Admin
- Full access to all resources
- User management and role assignment
- System configuration

### Manager
- Create and manage purchase orders
- Assign orders to staff
- Review and accept vendor quotes
- Vendor management

### Vendor
- View assigned purchase orders
- Submit quotes for orders
- Upload documents and invoices
- Manage vendor profile

### Staff
- View assigned orders
- Update order status
- Upload inspection documents
- Basic system access

## Endpoints

### Authentication
- `POST /api/auth/login` - User login and token generation
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout

### Users
- `GET /api/users` - List users (Admin only)
- `GET /api/users/{id}` - Get user details
- `POST /api/users` - Create user (Admin only)
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user (Admin only)

### Vendors
- `GET /api/vendors` - List vendors with pagination
- `POST /api/vendors` - Create vendor (Manager/Admin)
- `GET /api/vendors/{id}` - Get vendor details
- `PUT /api/vendors/{id}` - Update vendor
- `DELETE /api/vendors/{id}` - Delete vendor (Admin only)

### Orders
- `GET /api/orders` - List orders with pagination and filtering
- `POST /api/orders` - Create purchase order (Manager)
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}` - Update order
- `PATCH /api/orders/{id}` - Update order status
- `DELETE /api/orders/{id}` - Delete order (Manager/Admin)

### Quotes
- `GET /api/quotes` - List quotes with pagination
- `POST /api/quotes` - Submit quote (Vendor)
- `GET /api/quotes/{id}` - Get quote details
- `PATCH /api/quotes/{id}` - Accept/reject quote (Manager)

### Documents
- `POST /api/documents` - Upload document/file
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete document

### Search
- `GET /api/search` - Search across vendors, orders, quotes

## Pagination

All list endpoints support pagination with query parameters:

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10, max: 100)

Response includes pagination metadata:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "per_page": 10,
  "pages": 15
}
```

## Data Validation

Marshmallow schemas are used for:

- Input validation on all endpoints
- Data serialization for responses
- Nested relationships and complex objects
- Custom validation rules and error messages

## Email Integration

SendGrid is used for:

- User registration confirmations
- Quote submission notifications
- Order status updates
- System announcements

## Search Functionality

Algolia provides:

- Full-text search across multiple models
- Typo tolerance and fuzzy matching
- Faceted filtering and sorting
- Real-time indexing and search

## File Upload

Cloudinary handles:

- Image optimization and transformation
- Document storage with secure URLs
- File type validation
- Automatic format conversion

## Error Handling

Consistent error responses with appropriate HTTP status codes:

- 400 - Bad Request (validation errors)
- 401 - Unauthorized (authentication required)
- 403 - Forbidden (insufficient permissions)
- 404 - Not Found (resource not found)
- 422 - Unprocessable Entity (business logic errors)
- 500 - Internal Server Error

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test module
pytest tests/test_auth.py
```

## Deployment

The application is configured for deployment on Render/Railway with:

- Production Dependencies: Gunicorn, psycopg2-binary
- Database: PostgreSQL with connection pooling
- Environment Configuration: Secure environment variables
- Process Management: Gunicorn with multiple workers

### Deployment Steps:
1. Set up PostgreSQL database
2. Configure environment variables on deployment platform
3. Run database migrations: `flask db upgrade`
4. Seed initial data: `python db_seed.py`
5. Deploy application with Gunicorn

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key for session security
- `JWT_SECRET_KEY` - JWT token signing key
- `CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name
- `CLOUDINARY_API_KEY` - Cloudinary API key
- `CLOUDINARY_API_SECRET` - Cloudinary API secret
- `SENDGRID_API_KEY` - SendGrid API key for email
- `ALGOLIA_APP_ID` - Algolia application ID
- `ALGOLIA_API_KEY` - Algolia API key

## Security Features

- JWT token-based authentication with expiration
- Role-based access control with route protection
- Input validation and sanitization with Marshmallow
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration for frontend integration
- Secure password hashing with bcrypt
- File upload validation and virus scanning
- Rate limiting on authentication endpoints

## API Rate Limiting

- Authentication endpoints: 5 requests per minute
- General API endpoints: 100 requests per minute
- Search endpoints: 50 requests per minute

## Monitoring and Logging

- Structured JSON logging for production
- Error tracking and alerting
- Performance monitoring
- Database query logging in development

## Capstone Requirements Compliance

- Flask-RESTful API - Complete RESTful architecture
- JWT Authentication - Secure token-based authentication
- Role-Based Access Control - Four distinct user roles with permissions
- PostgreSQL Database - Production-ready database with proper normalization
- Marshmallow Serialization - Data validation and serialization
- CRUD Operations - Complete operations for all entities
- Pagination - Implemented on all list endpoints
- Email Integration - SendGrid for notifications
- Image Handling - Cloudinary integration with optimization
- Search Functionality - Algolia-powered search
- API Documentation - Swagger UI documentation
- Database Migrations - Alembic migration system
- Production Deployment - Render/Railway deployment ready

## License

This project is licensed under the MIT License.

## Support

For technical support or questions about this API, please contact the development team or refer to the Swagger documentation at `/api/docs`.
