from backend import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("🚀 Starting VendorSync Backend on http://localhost:5000")
    print("📊 API Endpoints:")
    print("   POST /login")
    print("   POST /register") 
    print("   GET  /dashboard")
    print("   GET  /vendors")
    print("   POST /orders")
    app.run(host='0.0.0.0', port=5000, debug=True)