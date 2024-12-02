from app import app, db
from routes import init_products

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_products()
    app.run(debug=True)