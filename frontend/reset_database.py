# reset_database.py

from app import app
from models.db_models_4 import db

with app.app_context():
    print("⚠️ Dropping all tables...")
    db.drop_all()
    print("✅ All tables dropped.")

    print("📦 Recreating tables...")
    db.create_all()
    print("✅ Database reset complete.")
