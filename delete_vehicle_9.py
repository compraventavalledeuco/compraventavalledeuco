#!/usr/bin/env python3
"""
Script para eliminar el vehículo ID 9 de la base de datos
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Vehicle, VehicleView, Click

def delete_vehicle_9():
    """Elimina el vehículo ID 9 y todos sus registros relacionados"""
    with app.app_context():
        try:
            # Buscar el vehículo
            vehicle = Vehicle.query.get(9)
            
            if not vehicle:
                print("❌ Vehículo ID 9 no encontrado en la base de datos")
                return False
            
            print(f"🔍 Encontrado vehículo ID 9:")
            print(f"   Título: {vehicle.title}")
            print(f"   Marca: {vehicle.brand}")
            print(f"   Modelo: {vehicle.model}")
            print(f"   Precio: {vehicle.price}")
            print(f"   Activo: {vehicle.is_active}")
            
            # Eliminar registros relacionados primero
            print("\n🗑️ Eliminando registros relacionados...")
            
            # Eliminar vistas del vehículo
            views_deleted = VehicleView.query.filter_by(vehicle_id=9).delete()
            print(f"   ✅ {views_deleted} registros de VehicleView eliminados")
            
            # Eliminar clicks del vehículo
            clicks_deleted = Click.query.filter_by(vehicle_id=9).delete()
            print(f"   ✅ {clicks_deleted} registros de Click eliminados")
            
            # Eliminar imágenes del sistema de archivos (si existen)
            if vehicle.images:
                print(f"   🖼️ Eliminando {len(vehicle.images)} imágenes...")
                upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
                for image_path in vehicle.images:
                    full_path = os.path.join(upload_folder, image_path)
                    if os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                            print(f"      ✅ Imagen eliminada: {image_path}")
                        except OSError as e:
                            print(f"      ⚠️ Error eliminando imagen {image_path}: {e}")
                    else:
                        print(f"      ⚠️ Imagen no encontrada: {image_path}")
            
            # Eliminar el vehículo
            print("\n🗑️ Eliminando vehículo...")
            db.session.delete(vehicle)
            db.session.commit()
            
            print("✅ Vehículo ID 9 eliminado exitosamente de la base de datos")
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando vehículo ID 9: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Iniciando eliminación del vehículo ID 9...")
    success = delete_vehicle_9()
    
    if success:
        print("\n🎉 Proceso completado exitosamente")
    else:
        print("\n💥 Proceso falló")
        sys.exit(1)
