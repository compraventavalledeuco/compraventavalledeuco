"""
Script de migración para sistema de analytics y anti-fraude
Agrega nuevas columnas a vehicle_view y crea tabla daily_stats
"""

import os
from sqlalchemy import create_engine, inspect, text

# Load DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///vehicle_marketplace.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)


def column_exists(table_name, column_name):
    """Check if column exists in table"""
    try:
        cols = inspector.get_columns(table_name)
        return any(col.get('name') == column_name for col in cols)
    except Exception:
        return False


def table_exists(table_name):
    """Check if table exists"""
    try:
        return table_name in inspector.get_table_names()
    except Exception:
        return False


def add_column_sql(table, column, coltype):
    """Add column to table if it doesn't exist"""
    if column_exists(table, column):
        print(f"[INFO] Column {table}.{column} already exists")
        return
    
    ddl = f"ALTER TABLE {table} ADD COLUMN {column} {coltype}"
    with engine.begin() as conn:
        try:
            conn.execute(text(ddl))
            print(f"[OK] Added column {table}.{column}")
        except Exception as e:
            print(f"[ERROR] Failed to add {table}.{column}: {e}")


def create_daily_stats_table():
    """Create daily_stats table if it doesn't exist"""
    if table_exists('daily_stats'):
        print("[INFO] Table daily_stats already exists")
        return
    
    ddl = """
    CREATE TABLE daily_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL UNIQUE,
        total_page_visits INTEGER DEFAULT 0,
        unique_visitors INTEGER DEFAULT 0,
        vehicle_stats TEXT,
        mobile_visitors INTEGER DEFAULT 0,
        desktop_visitors INTEGER DEFAULT 0,
        tablet_visitors INTEGER DEFAULT 0,
        top_cities TEXT,
        top_countries TEXT,
        blocked_views INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Adjust for PostgreSQL
    if 'postgresql' in DATABASE_URL:
        ddl = ddl.replace('AUTOINCREMENT', '').replace('INTEGER PRIMARY KEY', 'SERIAL PRIMARY KEY')
        ddl = ddl.replace('TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT NOW()')
    
    with engine.begin() as conn:
        try:
            conn.execute(text(ddl))
            print("[OK] Created table daily_stats")
        except Exception as e:
            print(f"[ERROR] Failed to create daily_stats table: {e}")


def main():
    print("="*60)
    print("MIGRACIÓN: Sistema de Analytics y Anti-Fraude")
    print("="*60)
    
    print("\n1. Actualizando tabla vehicle_view...")
    
    # Add new columns to vehicle_view
    add_column_sql('vehicle_view', 'session_id', 'VARCHAR(64)')
    add_column_sql('vehicle_view', 'device_type', 'VARCHAR(20)')
    add_column_sql('vehicle_view', 'browser', 'VARCHAR(50)')
    add_column_sql('vehicle_view', 'os', 'VARCHAR(50)')
    add_column_sql('vehicle_view', 'referrer', 'VARCHAR(500)')
    add_column_sql('vehicle_view', 'city', 'VARCHAR(100)')
    add_column_sql('vehicle_view', 'country', 'VARCHAR(50)')
    add_column_sql('vehicle_view', 'is_unique_today', 'BOOLEAN DEFAULT FALSE')
    add_column_sql('vehicle_view', 'is_counted', 'BOOLEAN DEFAULT TRUE')
    add_column_sql('vehicle_view', 'blocked_reason', 'VARCHAR(100)')
    
    print("\n2. Creando tabla daily_stats...")
    create_daily_stats_table()
    
    print("\n" + "="*60)
    print("MIGRACIÓN COMPLETADA")
    print("="*60)
    print("\nSistema anti-fraude configurado:")
    print("- Cooldown: 30 minutos entre vistas del mismo vehículo")
    print("- Límite diario: 10 vistas por IP del mismo vehículo")
    print("- Rate limiting: Máx 15 vistas en 5 minutos")
    print("\nNuevas funcionalidades:")
    print("- Tracking de dispositivos (mobile/desktop/tablet)")
    print("- Tracking de navegador y OS")
    print("- Geolocalización básica")
    print("- Estadísticas diarias agregadas")


if __name__ == '__main__':
    main()
