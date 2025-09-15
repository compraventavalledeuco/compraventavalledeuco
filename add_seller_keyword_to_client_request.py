#!/usr/bin/env python3
"""
Add seller_keyword column to client_request table (for submissions) in the current database.
Safe to run multiple times; it checks for existence first.
"""
import os
from app import app, db

def add_seller_keyword_to_client_request():
    with app.app_context():
        try:
            engine = db.engine
            dialect = engine.dialect.name
            with engine.connect() as conn:
                column_exists = False
                if dialect == 'sqlite':
                    # Use PRAGMA to inspect columns
                    pragma_res = conn.execute(db.text("PRAGMA table_info(client_request);"))
                    for row in pragma_res:
                        # row[1] is column name
                        if str(row[1]).lower() == 'seller_keyword':
                            column_exists = True
                            break
                else:
                    # Assume Postgres or other supporting information_schema
                    result = conn.execute(db.text(
                        """
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='client_request' AND column_name='seller_keyword';
                        """
                    ))
                    if result.fetchone():
                        column_exists = True

                if column_exists:
                    print("Column seller_keyword already exists on client_request")
                    return

                # Add column
                conn.execute(db.text("ALTER TABLE client_request ADD COLUMN seller_keyword VARCHAR(50);"))
                conn.commit()
                print("Column seller_keyword added to client_request successfully")
        except Exception as e:
            print(f"Error adding column to client_request: {e}")

if __name__ == "__main__":
    add_seller_keyword_to_client_request()
