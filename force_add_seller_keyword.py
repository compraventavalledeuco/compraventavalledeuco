#!/usr/bin/env python3
"""
Force add seller_keyword column to vehicle table - bypasses existence check
"""
import os
os.environ.setdefault("SKIP_ROUTES", "1")

from app import app, db

def force_add_seller_keyword():
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Force add the column without checking
                conn.execute(db.text("ALTER TABLE vehicle ADD COLUMN seller_keyword VARCHAR(255);"))
                conn.commit()
                print("✅ seller_keyword column added to vehicle table")
        except Exception as e:
            error_msg = str(e).lower()
            if 'already exists' in error_msg or 'duplicate column' in error_msg:
                print("✅ seller_keyword column already exists in vehicle table")
            else:
                print(f"❌ Error adding column: {e}")
                
        # Now verify it exists by listing all columns
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT column_name FROM information_schema.columns WHERE table_name='vehicle' ORDER BY column_name;"))
                columns = [row[0] for row in result.fetchall()]
                print(f"\n📋 Vehicle table columns: {columns}")
                
                if 'seller_keyword' in columns:
                    print("✅ seller_keyword column confirmed in vehicle table")
                else:
                    print("❌ seller_keyword column NOT found in vehicle table")
        except Exception as e:
            print(f"Error verifying columns: {e}")

if __name__ == "__main__":
    force_add_seller_keyword()
