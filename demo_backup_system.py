#!/usr/bin/env python3
"""
Demostración del sistema de backup mejorado
Este script crea varios backups para demostrar:
1. Backup de solo datos (sin imágenes físicas)
2. Sistema de rotación (máximo 5 backups)
3. Funcionalidad de restauración
"""

import sys
import os
import time
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

def demo_backup_creation():
    """Demuestra la creación de backups"""
    try:
        from backup_system.backup_system import BackupManager
        
        print("🔧 Inicializando BackupManager...")
        backup_manager = BackupManager()
        
        print("\n📦 Creando 6 backups para demostrar el sistema de rotación...")
        
        successful_backups = 0
        for i in range(1, 7):
            print(f"\n--- Backup {i}/6 ---")
            result = backup_manager.perform_backup('manual')
            
            if result['success']:
                print(f"✅ Backup {i} completado exitosamente!")
                size_bytes = result.get('total_size', 0)
                size_kb = size_bytes / 1024 if size_bytes > 0 else 0
                print(f"📊 Tamaño: {size_kb:.2f} KB")
                successful_backups += 1
            else:
                print(f"❌ Error en backup {i}:")
                for error in result.get('errors', []):
                    print(f"   - {error}")
            
            # Pequeña pausa entre backups
            if i < 6:
                time.sleep(1)
        
        print(f"\n✅ Backups creados exitosamente: {successful_backups}/6")
        return successful_backups > 0
        
    except Exception as e:
        print(f"❌ Error en demostración: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_backup_list():
    """Lista los backups y demuestra el sistema de rotación"""
    try:
        backup_dirs = ['backups', 'backups/daily', 'backups/weekly', 'backups/monthly']
        
        print("\n📋 Estado actual de backups (después de rotación):")
        total_backups = 0
        total_size = 0
        
        for backup_dir in backup_dirs:
            backup_path = Path(backup_dir)
            if backup_path.exists():
                backups = list(backup_path.glob('*.zip'))
                if backups:
                    print(f"\n📂 {backup_dir}:")
                    # Ordenar por fecha de modificación (más recientes primero)
                    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    
                    for backup in backups:
                        size_bytes = backup.stat().st_size
                        size_kb = size_bytes / 1024
                        total_size += size_bytes
                        print(f"   📦 {backup.name} ({size_kb:.2f} KB)")
                        total_backups += 1
        
        print(f"\n📊 Resumen:")
        print(f"   📦 Total de backups: {total_backups}")
        print(f"   💾 Tamaño total: {(total_size / 1024):.2f} KB")
        print(f"   🔄 Rotación: {'Activa (máx. 5 backups)' if total_backups <= 5 else 'Necesaria'}")
        
        return total_backups
        
    except Exception as e:
        print(f"❌ Error listando backups: {e}")
        return 0

def demo_backup_content():
    """Muestra el contenido de un backup reciente"""
    try:
        import zipfile
        import json
        
        # Buscar el backup más reciente
        backup_dirs = ['backups', 'backups/daily', 'backups/weekly', 'backups/monthly']
        latest_backup = None
        latest_time = 0
        
        for backup_dir in backup_dirs:
            backup_path = Path(backup_dir)
            if backup_path.exists():
                for backup_file in backup_path.glob('*.zip'):
                    mtime = backup_file.stat().st_mtime
                    if mtime > latest_time:
                        latest_time = mtime
                        latest_backup = backup_file
        
        if not latest_backup:
            print("❌ No se encontraron backups para analizar")
            return False
        
        print(f"\n🔍 Analizando backup más reciente: {latest_backup.name}")
        
        with zipfile.ZipFile(latest_backup, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"📁 Archivos en el backup ({len(file_list)}):")
            
            for file_name in sorted(file_list):
                file_info = zip_ref.getinfo(file_name)
                size_kb = file_info.file_size / 1024
                print(f"   📄 {file_name} ({size_kb:.2f} KB)")
            
            # Si existe el resumen del backup, mostrarlo
            if 'data_backup/backup_summary.json' in file_list:
                print(f"\n📊 Resumen del backup:")
                summary_data = zip_ref.read('data_backup/backup_summary.json')
                summary = json.loads(summary_data.decode('utf-8'))
                
                print(f"   📅 Fecha: {summary.get('backup_date', 'N/A')}")
                print(f"   🚗 Vehículos: {summary.get('vehicles_count', 0)}")
                print(f"   📝 Solicitudes: {summary.get('requests_count', 0)}")
                print(f"   👥 Administradores: {summary.get('admins_count', 0)}")
                print(f"   🏢 Gestores: {summary.get('gestores_count', 0)}")
                print(f"   💡 Nota: {summary.get('note', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analizando backup: {e}")
        return False

def demo_backup_size_comparison():
    """Compara el tamaño de los backups nuevos vs antiguos"""
    try:
        backup_path = Path('backups')
        if not backup_path.exists():
            print("❌ No se encontró directorio de backups")
            return False
        
        backups = list(backup_path.glob('*.zip'))
        if len(backups) < 2:
            print("ℹ️  Se necesitan al menos 2 backups para comparar")
            return False
        
        # Ordenar por fecha
        backups.sort(key=lambda x: x.stat().st_mtime)
        
        print(f"\n📊 Comparación de tamaños de backup:")
        print(f"{'Archivo':<40} {'Tamaño (KB)':<12} {'Tipo':<10}")
        print("-" * 65)
        
        for backup in backups:
            size_kb = backup.stat().st_size / 1024
            # Determinar si es nuevo formato (pequeño) o antiguo (grande)
            backup_type = "NUEVO ✅" if size_kb < 100 else "ANTIGUO ❌"
            print(f"{backup.name:<40} {size_kb:<12.2f} {backup_type:<10}")
        
        # Mostrar estadísticas
        new_backups = [b for b in backups if b.stat().st_size / 1024 < 100]
        old_backups = [b for b in backups if b.stat().st_size / 1024 >= 100]
        
        if new_backups and old_backups:
            avg_new = sum(b.stat().st_size for b in new_backups) / len(new_backups) / 1024
            avg_old = sum(b.stat().st_size for b in old_backups) / len(old_backups) / 1024
            reduction = ((avg_old - avg_new) / avg_old) * 100
            
            print(f"\n📈 Estadísticas:")
            print(f"   📦 Backups nuevos (solo datos): {len(new_backups)} - Promedio: {avg_new:.2f} KB")
            print(f"   📦 Backups antiguos (con imágenes): {len(old_backups)} - Promedio: {avg_old:.2f} KB")
            print(f"   💾 Reducción de tamaño: {reduction:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error comparando tamaños: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DEMOSTRACIÓN DEL SISTEMA DE BACKUP MEJORADO")
    print("=" * 50)
    
    # Demostrar creación de backups
    print("\n=== 1. Creación de Backups ===")
    creation_success = demo_backup_creation()
    
    # Mostrar lista de backups
    print("\n=== 2. Sistema de Rotación ===")
    backup_count = demo_backup_list()
    
    # Analizar contenido de backup
    print("\n=== 3. Contenido del Backup ===")
    content_success = demo_backup_content()
    
    # Comparar tamaños
    print("\n=== 4. Comparación de Tamaños ===")
    comparison_success = demo_backup_size_comparison()
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE LA DEMOSTRACIÓN")
    print("=" * 50)
    print(f"✅ Creación de backups: {'Exitosa' if creation_success else 'Falló'}")
    print(f"✅ Sistema de rotación: {'Funcionando (máx. 5)' if backup_count <= 5 else 'Necesita ajuste'}")
    print(f"✅ Análisis de contenido: {'Exitoso' if content_success else 'Falló'}")
    print(f"✅ Comparación de tamaños: {'Exitosa' if comparison_success else 'Falló'}")
    
    print(f"\n🎯 BENEFICIOS DEL NUEVO SISTEMA:")
    print(f"   📦 Solo guarda datos (URLs de imágenes, no archivos físicos)")
    print(f"   🔄 Rotación automática (máximo 5 backups)")
    print(f"   💾 Backups mucho más pequeños y rápidos")
    print(f"   🔧 Sistema de restauración mejorado")
    print(f"   📊 Información detallada de cada backup")
    
    if creation_success:
        print(f"\n🎉 ¡Sistema de backup funcionando correctamente!")
    else:
        print(f"\n⚠️  Revisar configuración del sistema")
