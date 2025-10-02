"""
Script automático para resetear las vistas de vehículos PLUS
Elimina todos los registros de VehicleView para vehículos con is_plus=True
NO pide confirmación - úsalo solo cuando estés seguro
"""

import os
from sqlalchemy import create_engine, text

# Load DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///vehicle_marketplace.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)


def reset_plus_vehicle_views_auto():
    """Elimina todas las vistas de vehículos PLUS automáticamente"""
    
    print("="*60)
    print("RESETEAR VISTAS DE VEHÍCULOS PLUS (AUTOMÁTICO)")
    print("="*60)
    
    with engine.begin() as conn:
        # Primero, obtener los IDs de vehículos PLUS
        result = conn.execute(text("""
            SELECT id, title FROM vehicle WHERE is_plus = true
        """))
        
        plus_vehicles = result.fetchall()
        
        if not plus_vehicles:
            print("\n[INFO] No hay vehículos PLUS en la base de datos")
            return
        
        print(f"\n[INFO] Encontrados {len(plus_vehicles)} vehículos PLUS:")
        for vehicle in plus_vehicles:
            print(f"  - ID {vehicle[0]}: {vehicle[1]}")
        
        # Contar vistas a eliminar
        count_result = conn.execute(text("""
            SELECT COUNT(*) FROM vehicle_view 
            WHERE vehicle_id IN (
                SELECT id FROM vehicle WHERE is_plus = true
            )
        """))
        
        views_count = count_result.scalar()
        
        print(f"\n[INFO] Se eliminarán {views_count} registros de vistas")
        print("[INFO] Ejecutando eliminación automática...")
        
        # Eliminar vistas
        result = conn.execute(text("""
            DELETE FROM vehicle_view 
            WHERE vehicle_id IN (
                SELECT id FROM vehicle WHERE is_plus = true
            )
        """))
        
        print(f"\n[OK] ✓ Se eliminaron {result.rowcount} registros de vistas de vehículos PLUS")
    
    print("\n" + "="*60)
    print("OPERACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\n✓ Las vistas de vehículos PLUS han sido reseteadas.")
    print("✓ El sistema anti-fraude ahora usa un cooldown de 3 horas.")


if __name__ == '__main__':
    reset_plus_vehicle_views_auto()
