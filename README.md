
---

## 2. `backend/README.md`

```md
# VendorSync API

## Live API
[https://your-app.onrender.com](https://your-app.onrender.com)

## Features
- RESTful API with Flask-RESTful
- JWT Authentication + RBAC
- Full CRUD on Purchase Orders
- SendGrid email notifications
- Cloudinary document storage
- Algolia-powered search
- PostgreSQL + SQLAlchemy

## Models (7)
- User, Role, Vendor, PurchaseOrder, Quote, Document, OrderAssignment
- Many-to-many: `OrderAssignment`

## Setup
```bash
pip install -r requirements.txt
python app.py