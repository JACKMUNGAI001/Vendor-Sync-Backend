from backend import create_app, db
from backend.auto_seed import auto_seed_database

app = create_app()

with app.app_context():
    db.create_all()
    auto_seed_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)