from backend import create_app, db
from backend.auto_seed import auto_seed_database

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        auto_seed_database()
    app.run(debug=True)