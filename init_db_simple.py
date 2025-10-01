"""Simple database initialization script that avoids importing routes"""
import os
os.environ["SKIP_ROUTES"] = "1"

from app import app, db, generate_password_hash_sha256
from models import Admin
import logging

logging.basicConfig(level=logging.INFO)

def init_database():
    """Initialize database tables and admin user"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            logging.info("Database tables created successfully")
            
            # Create admin user if not exists
            existing_admin = Admin.query.filter_by(username="Ryoma94").first()
            if not existing_admin:
                admin_password = os.environ.get("ADMIN_PASSWORD", "DiegoPortaz7")
                admin = Admin(
                    username="Ryoma94",
                    password_hash=generate_password_hash_sha256(admin_password)
                )
                db.session.add(admin)
                db.session.commit()
                logging.info(f"Admin user created with password: {admin_password}")
            else:
                # Update password if changed
                admin_password = os.environ.get("ADMIN_PASSWORD", "DiegoPortaz7")
                new_hash = generate_password_hash_sha256(admin_password)
                if existing_admin.password_hash != new_hash:
                    existing_admin.password_hash = new_hash
                    db.session.commit()
                    logging.info("Admin password updated")
                logging.info(f"Admin user already exists with ID: {existing_admin.id}")
            
            logging.info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Database initialization failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("Initializing database...")
    success = init_database()
    if success:
        print("Database initialization completed successfully!")
    else:
        print("Database initialization failed!")
