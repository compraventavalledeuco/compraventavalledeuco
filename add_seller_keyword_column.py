#!/usr/bin/env python3
"""
Script to add seller_keyword column to vehicle table in Heroku PostgreSQL
"""

import os
from app import app, db

def add_seller_keyword_column():
    """Add seller_keyword column to vehicle table"""
    with app.app_context():
        try:
            # Check if column already exists
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='vehicle' AND column_name='seller_keyword';
                """))
                
                if result.fetchone():
                    print("Column seller_keyword already exists")
                    return
                
                # Add the column
                conn.execute(db.text("ALTER TABLE vehicle ADD COLUMN seller_keyword VARCHAR(255);"))
                conn.commit()
            print("Column seller_keyword added successfully")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_seller_keyword_column()
