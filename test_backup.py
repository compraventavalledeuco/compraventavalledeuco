#!/usr/bin/env python3
"""
Script de prueba para el sistema de backup mejorado
"""

import sys
import os
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

def test_backup_system():
    """Prueba el sistema de backup"""
    try:
        # Importar el sistema de backup
        from backup_system.backup_system import BackupManager
        
        print("🔧 Inicializando BackupManager...")
        backup_manager = BackupManager()
        
        print("📦 Ejecutando backup manual...")
        result = backup_manager.perform_backup('manual')
        
        if result['success']:
            print("✅ Backup completado exitosamente!")
            print(f"📁 Archivo: {result.get('archive_path', 'N/A')}")
            size_bytes = result.get('total_size', 0)
            size_kb = size_bytes / 1024 if size_bytes > 0 else 0
            print(f"📊 Tamaño: {size_bytes} bytes ({size_kb:.2f} KB)")
            if result.get('errors'):
                print(f"⚠️  Advertencias: {result['errors']}")
        else:
            print("❌ Error en backup:")
            for error in result.get('errors', []):
                print(f"   - {error}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backup_with_app_context():
    """Prueba el backup con contexto de aplicación"""
    try:
        # Importar la aplicación Flask
        from app import app
        from backup_system.backup_system import BackupManager
        
        print("🔧 Inicializando con contexto de aplicación...")
        
        with app.app_context():
            backup_manager = BackupManager()
            print("📦 Ejecutando backup con datos de aplicación...")
            result = backup_manager.perform_backup('manual')
            
            if result['success']:
                print("✅ Backup con aplicación completado exitosamente!")
                print(f"📁 Archivo: {result.get('archive_path', 'N/A')}")
                size_bytes = result.get('total_size', 0)
                size_kb = size_bytes / 1024 if size_bytes > 0 else 0
                print(f"📊 Tamaño: {size_bytes} bytes ({size_kb:.2f} KB)")
                if result.get('errors'):
                    print(f"⚠️  Advertencias: {result['errors']}")
            else:
                print("❌ Error en backup con aplicación:")
                for error in result.get('errors', []):
                    print(f"   - {error}")
            
            return result['success']
        
    except Exception as e:
        print(f"❌ Error ejecutando test con aplicación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backup_list():
    """Lista los backups existentes"""
    try:
        backup_dirs = ['backups', 'backups/daily', 'backups/weekly', 'backups/monthly']
        
        print("\n📋 Backups existentes:")
        total_backups = 0
        
        for backup_dir in backup_dirs:
            backup_path = Path(backup_dir)
            if backup_path.exists():
                backups = list(backup_path.glob('*.zip'))
                if backups:
                    print(f"\n📂 {backup_dir}:")
                    for backup in sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True):
                        size_mb = backup.stat().st_size / (1024 * 1024)
                        print(f"   📦 {backup.name} ({size_mb:.2f} MB)")
                        total_backups += 1
        
        print(f"\n📊 Total de backups: {total_backups}")
        return total_backups
        
    except Exception as e:
        print(f"❌ Error listando backups: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema de backup...")
    
    # Probar creación de backup básico
    print("\n=== Prueba 1: Backup básico ===")
    backup_success_basic = test_backup_system()
    
    # Probar backup con contexto de aplicación
    print("\n=== Prueba 2: Backup con aplicación ===")
    backup_success_app = test_backup_with_app_context()
    
    # Listar backups existentes
    print("\n=== Listado de backups ===")
    backup_count = test_backup_list()
    
    print(f"\n📋 Resumen:")
    print(f"   ✅ Backup básico exitoso: {'Sí' if backup_success_basic else 'No'}")
    print(f"   ✅ Backup con app exitoso: {'Sí' if backup_success_app else 'No'}")
    print(f"   📦 Total backups: {backup_count}")
    
    if backup_success_basic or backup_success_app:
        print("\n🎉 ¡Sistema de backup funcionando correctamente!")
    else:
        print("\n⚠️  Revisar configuración del sistema de backup")
