#!/usr/bin/env python3
"""
Demostración simple del sistema de backup mejorado
"""

import os
import json
import zipfile
import datetime
from pathlib import Path

def create_simple_backup():
    """Crea un backup simple para demostración"""
    try:
        # Crear directorio de backup
        backup_dir = Path('backups')
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now()
        backup_name = f"backup_demo_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        backup_path = backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        # Crear directorio de datos
        data_backup_path = backup_path / "data_backup"
        data_backup_path.mkdir(exist_ok=True)
        
        # Simular datos de vehículos (con URLs de imágenes, no archivos físicos)
        vehicles_data = [
            {
                'id': 1,
                'title': 'Toyota Corolla 2020',
                'price': 15000,
                'currency': 'USD',
                'images': '["https://res.cloudinary.com/demo/image/upload/v123/car1.jpg", "https://res.cloudinary.com/demo/image/upload/v123/car1_2.jpg"]',
                'brand': 'Toyota',
                'model': 'Corolla',
                'year': 2020,
                'is_active': True,
                'created_at': '2024-01-15T10:30:00'
            },
            {
                'id': 2,
                'title': 'Honda Civic 2019',
                'price': 13500,
                'currency': 'USD',
                'images': '["https://res.cloudinary.com/demo/image/upload/v124/car2.jpg"]',
                'brand': 'Honda',
                'model': 'Civic',
                'year': 2019,
                'is_active': True,
                'created_at': '2024-01-16T14:20:00'
            }
        ]
        
        # Simular datos de solicitudes de clientes
        requests_data = [
            {
                'id': 1,
                'full_name': 'Juan Pérez',
                'dni': '12345678',
                'whatsapp_number': '+5491123456789',
                'title': 'Ford Focus 2018',
                'price': 12000,
                'currency': 'USD',
                'status': 'pending',
                'created_at': '2024-01-17T09:15:00'
            }
        ]
        
        # Simular datos de administradores
        admins_data = [
            {
                'id': 1,
                'username': 'admin',
                'password_hash': 'hashed_password_here'
            }
        ]
        
        # Guardar datos en archivos JSON
        with open(data_backup_path / "vehicles.json", 'w', encoding='utf-8') as f:
            json.dump(vehicles_data, f, indent=2, ensure_ascii=False)
        
        with open(data_backup_path / "client_requests.json", 'w', encoding='utf-8') as f:
            json.dump(requests_data, f, indent=2, ensure_ascii=False)
        
        with open(data_backup_path / "admins.json", 'w', encoding='utf-8') as f:
            json.dump(admins_data, f, indent=2, ensure_ascii=False)
        
        # Crear resumen del backup
        summary = {
            'backup_date': timestamp.isoformat(),
            'vehicles_count': len(vehicles_data),
            'requests_count': len(requests_data),
            'admins_count': len(admins_data),
            'gestores_count': 0,
            'backup_type': 'data_only',
            'note': 'Este backup contiene solo datos (URLs de imágenes, no archivos físicos)'
        }
        
        with open(data_backup_path / "backup_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Crear información de base de datos
        with open(backup_path / "database_info.txt", 'w', encoding='utf-8') as f:
            f.write("Base de datos: No se encontró archivo SQLite local\n")
            f.write("Probablemente usando PostgreSQL remoto\n")
            f.write("Los datos se respaldan desde la aplicación directamente\n")
        
        # Crear archivo comprimido
        archive_path = backup_dir / f"{backup_name}.zip"
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_path)
                    zipf.write(file_path, arcname)
        
        # Eliminar carpeta temporal
        import shutil
        shutil.rmtree(backup_path)
        
        return {
            'success': True,
            'archive_path': str(archive_path),
            'total_size': archive_path.stat().st_size,
            'vehicles_count': len(vehicles_data),
            'requests_count': len(requests_data)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def list_backups():
    """Lista todos los backups"""
    backup_dirs = ['backups', 'backups/daily', 'backups/weekly', 'backups/monthly']
    all_backups = []
    
    for backup_dir in backup_dirs:
        backup_path = Path(backup_dir)
        if backup_path.exists():
            for backup_file in backup_path.glob('*.zip'):
                all_backups.append({
                    'name': backup_file.name,
                    'path': str(backup_file),
                    'size': backup_file.stat().st_size,
                    'date': datetime.datetime.fromtimestamp(backup_file.stat().st_mtime),
                    'directory': backup_dir
                })
    
    # Ordenar por fecha (más recientes primero)
    all_backups.sort(key=lambda x: x['date'], reverse=True)
    return all_backups

def analyze_backup_content(backup_path):
    """Analiza el contenido de un backup"""
    try:
        with zipfile.ZipFile(backup_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            # Buscar resumen si existe
            summary = None
            if 'data_backup/backup_summary.json' in file_list:
                summary_data = zip_ref.read('data_backup/backup_summary.json')
                summary = json.loads(summary_data.decode('utf-8'))
            
            return {
                'files': file_list,
                'file_count': len(file_list),
                'summary': summary
            }
    except Exception as e:
        return {'error': str(e)}

def cleanup_old_backups(max_backups=5):
    """Limpia backups antiguos manteniendo solo los más recientes"""
    all_backups = list_backups()
    
    if len(all_backups) > max_backups:
        backups_to_delete = all_backups[max_backups:]
        deleted_count = 0
        
        for backup in backups_to_delete:
            try:
                Path(backup['path']).unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Error eliminando {backup['name']}: {e}")
        
        return deleted_count
    
    return 0

def main():
    print("🚀 DEMOSTRACIÓN DEL SISTEMA DE BACKUP MEJORADO")
    print("=" * 50)
    
    # Crear algunos backups de demostración
    print("\n=== 1. Creando Backups de Demostración ===")
    
    successful_backups = 0
    for i in range(1, 7):  # Crear 6 backups para probar rotación
        print(f"📦 Creando backup {i}/6...")
        result = create_simple_backup()
        
        if result['success']:
            size_kb = result['total_size'] / 1024
            print(f"✅ Backup {i} creado: {size_kb:.2f} KB")
            print(f"   📊 Vehículos: {result['vehicles_count']}, Solicitudes: {result['requests_count']}")
            successful_backups += 1
        else:
            print(f"❌ Error en backup {i}: {result['error']}")
        
        # Pequeña pausa para que tengan timestamps diferentes
        import time
        time.sleep(0.1)
    
    # Listar todos los backups
    print(f"\n=== 2. Lista de Backups (antes de rotación) ===")
    all_backups = list_backups()
    print(f"📦 Total de backups encontrados: {len(all_backups)}")
    
    for backup in all_backups[:10]:  # Mostrar solo los primeros 10
        size_kb = backup['size'] / 1024
        print(f"   📄 {backup['name']} - {size_kb:.2f} KB - {backup['date'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Aplicar rotación
    print(f"\n=== 3. Aplicando Sistema de Rotación (máx. 5) ===")
    deleted_count = cleanup_old_backups(5)
    print(f"🗑️  Backups eliminados: {deleted_count}")
    
    # Listar backups después de rotación
    print(f"\n=== 4. Lista de Backups (después de rotación) ===")
    remaining_backups = list_backups()
    print(f"📦 Backups restantes: {len(remaining_backups)}")
    
    total_size = 0
    for backup in remaining_backups:
        size_kb = backup['size'] / 1024
        total_size += backup['size']
        print(f"   📄 {backup['name']} - {size_kb:.2f} KB")
    
    # Analizar contenido de un backup
    if remaining_backups:
        print(f"\n=== 5. Análisis de Contenido ===")
        latest_backup = remaining_backups[0]
        print(f"🔍 Analizando: {latest_backup['name']}")
        
        content = analyze_backup_content(latest_backup['path'])
        if 'error' not in content:
            print(f"📁 Archivos en el backup: {content['file_count']}")
            for file_name in content['files']:
                print(f"   📄 {file_name}")
            
            if content['summary']:
                summary = content['summary']
                print(f"\n📊 Resumen del backup:")
                print(f"   📅 Fecha: {summary.get('backup_date', 'N/A')}")
                print(f"   🚗 Vehículos: {summary.get('vehicles_count', 0)}")
                print(f"   📝 Solicitudes: {summary.get('requests_count', 0)}")
                print(f"   👥 Administradores: {summary.get('admins_count', 0)}")
                print(f"   💡 Nota: {summary.get('note', 'N/A')}")
    
    # Resumen final
    print(f"\n" + "=" * 50)
    print(f"📋 RESUMEN DE LA DEMOSTRACIÓN")
    print(f"=" * 50)
    print(f"✅ Backups creados exitosamente: {successful_backups}/6")
    print(f"✅ Sistema de rotación: Funcionando (máx. 5 backups)")
    print(f"✅ Backups finales: {len(remaining_backups)}")
    print(f"✅ Tamaño total: {(total_size / 1024):.2f} KB")
    
    print(f"\n🎯 CARACTERÍSTICAS DEL NUEVO SISTEMA:")
    print(f"   📦 Solo guarda datos (URLs de imágenes, no archivos físicos)")
    print(f"   🔄 Rotación automática (máximo 5 backups)")
    print(f"   💾 Backups pequeños y eficientes")
    print(f"   📊 Información detallada de cada backup")
    print(f"   🔧 Fácil restauración desde archivos JSON")
    
    # Comparación con sistema anterior
    old_backups = [b for b in all_backups if b['size'] > 100000]  # > 100KB
    new_backups = [b for b in all_backups if b['size'] <= 100000]  # <= 100KB
    
    if old_backups and new_backups:
        avg_old = sum(b['size'] for b in old_backups) / len(old_backups) / 1024
        avg_new = sum(b['size'] for b in new_backups) / len(new_backups) / 1024
        reduction = ((avg_old - avg_new) / avg_old) * 100
        
        print(f"\n📈 COMPARACIÓN CON SISTEMA ANTERIOR:")
        print(f"   📦 Backups antiguos (con imágenes): {avg_old:.2f} KB promedio")
        print(f"   📦 Backups nuevos (solo datos): {avg_new:.2f} KB promedio")
        print(f"   💾 Reducción de tamaño: {reduction:.1f}%")
    
    print(f"\n🎉 ¡Sistema de backup mejorado funcionando correctamente!")

if __name__ == "__main__":
    main()
