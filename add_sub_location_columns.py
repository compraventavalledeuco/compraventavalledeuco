import os
from sqlalchemy import create_engine, inspect, text

# Load DATABASE_URL similar to app.py
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///vehicle_marketplace.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)


def column_exists(table_name: str, column_name: str) -> bool:
    try:
        cols = inspector.get_columns(table_name)
        return any(col.get('name') == column_name for col in cols)
    except Exception:
        return False


def add_column_sql(table: str, column: str, coltype: str):
    # SQLite and others support simple ALTER TABLE ADD COLUMN
    ddl = f"ALTER TABLE {table} ADD COLUMN {column} {coltype}"
    with engine.begin() as conn:
        try:
            conn.execute(text(ddl))
            print(f"✓ Added column {column} to {table}")
        except Exception as e:
            # If already exists or other errors, print and continue
            print(f"! Skipped adding {column} to {table}: {e}")


def main():
    # Vehicle.sub_location
    if not column_exists('vehicle', 'sub_location'):
        # VARCHAR length 50 as in models.py
        # SQLite ignores length, MySQL/Postgres will accept
        add_column_sql('vehicle', 'sub_location', 'VARCHAR(50)')
    else:
        print("= Column vehicle.sub_location already exists")

    # ClientRequest.sub_location
    if not column_exists('client_request', 'sub_location'):
        add_column_sql('client_request', 'sub_location', 'VARCHAR(50)')
    else:
        print("= Column client_request.sub_location already exists")


if __name__ == '__main__':
    main()
