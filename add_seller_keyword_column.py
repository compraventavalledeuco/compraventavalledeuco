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
            engine = db.engine
            dialect = engine.dialect.name
            with engine.connect() as conn:
                column_exists = False
                if dialect == 'sqlite':
                    # Use PRAGMA to inspect columns
                    pragma_res = conn.execute(db.text("PRAGMA table_info(vehicle);"))
                    for row in pragma_res:
                        # row[1] is column name
                        if str(row[1]).lower() == 'seller_keyword':
                            column_exists = True
                            break
                else:
                    # Assume Postgres or other supporting information_schema
                    result = conn.execute(db.text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='vehicle' AND column_name='seller_keyword';
                    """))
                    if result.fetchone():
                        column_exists = True

                if column_exists:
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
