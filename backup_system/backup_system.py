#!/usr/bin/env python3
"""
Sistema de Backup Automatizado para Marketplace de Vehículos
Autor: Sistema de Backup Seguro
Fecha: 2025-09-12

Este script realiza backups completos de:
- Base de datos SQLite
- Imágenes de vehículos y gestores
- Archivos de configuración críticos
"""

import os
import sys
import shutil
import sqlite3
import zipfile
import datetime
import logging
import json
import hashlib
from pathlib import Path
import schedule
import time

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class BackupManager:
    def __init__(self, config_file='backup_config.json'):
        """Inicializa el gestor de backups"""
        self.config_file = config_file
        self.load_config()
        self.setup_directories()
        
    def load_config(self):
        """Carga la configuración desde archivo JSON"""
        default_config = {
            "project_path": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "backup_base_dir": "backups",
            "database_file": "vehicle_marketplace.db",
            "uploads_dir": "static/uploads",
            "config_files": [
                "app.py",
                "models.py", 
                "routes.py",
                "requirements.txt",
                "pyproject.toml",
                "config_local.py"
            ],
            "retention_days": 30,
            "compression_level": 6,
            "enable_cloud_backup": False,
            "cloud_provider": "none",
            "backup_schedule": {
                "daily": "02:00",
                "weekly": "sunday",
                "monthly": 1
            }
        }
        
        config_path = Path(__file__).parent / self.config_file
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config = {**default_config, **loaded_config}
            except Exception as e:
                logging.warning(f"Error cargando configuración: {e}. Usando configuración por defecto.")
                self.config = default_config
        else:
            self.config = default_config
        
        self.save_config()
        
    def save_config(self):
        """Guarda la configuración actual"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error guardando configuración: {e}")
    
    def setup_directories(self):
        """Crea las carpetas necesarias para backups"""
        self.backup_dir = Path(self.config['backup_base_dir'])
        self.daily_dir = self.backup_dir / 'daily'
        self.weekly_dir = self.backup_dir / 'weekly'
        self.monthly_dir = self.backup_dir / 'monthly'
        
        for directory in [self.backup_dir, self.daily_dir, self.weekly_dir, self.monthly_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
    def calculate_file_hash(self, file_path):
        """Calcula el hash SHA-256 de un archivo"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logging.error(f"Error calculando hash de {file_path}: {e}")
            return None
    
    def backup_database(self, backup_path):
        """Realiza backup de la base de datos (SQLite si existe)"""
        db_path = Path(self.config['project_path']) / self.config['database_file']
        
        if not db_path.exists():
            logging.info(f"Base de datos SQLite no encontrada: {db_path} - Probablemente usando PostgreSQL")
            # Crear un archivo de información sobre la base de datos
            db_info_path = backup_path / "database_info.txt"
            with open(db_info_path, 'w', encoding='utf-8') as f:
                f.write(f"Base de datos: No se encontró archivo SQLite local\n")
                f.write(f"Ruta buscada: {db_path}\n")
                f.write(f"Probablemente usando PostgreSQL remoto\n")
                f.write(f"Los datos se respaldan desde la aplicación directamente\n")
            return True
            
        try:
            # Crear backup usando SQLite backup API (más seguro que copiar archivo)
            backup_db_path = backup_path / f"database_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Conectar a la base de datos original
            source_conn = sqlite3.connect(str(db_path))
            
            # Crear conexión al archivo de backup
            backup_conn = sqlite3.connect(str(backup_db_path))
            
            # Realizar backup usando la API de SQLite
            source_conn.backup(backup_conn)
            
            # Cerrar conexiones
            backup_conn.close()
            source_conn.close()
            
            # Verificar integridad del backup
            if self.verify_database_integrity(backup_db_path):
                logging.info(f"Backup de base de datos SQLite completado: {backup_db_path}")
                return True
            else:
                logging.error("Error en la verificación de integridad del backup de base de datos")
                return False
                
        except Exception as e:
            logging.error(f"Error en backup de base de datos: {e}")
            return False
    
    def verify_database_integrity(self, db_path):
        """Verifica la integridad de la base de datos"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()
            conn.close()
            return result[0] == "ok"
        except Exception as e:
            logging.error(f"Error verificando integridad de {db_path}: {e}")
            return False
    
    def backup_data_only(self, backup_path):
        """Realiza backup solo de los datos (URLs de imágenes, no archivos físicos)"""
        try:
            data_backup_path = backup_path / "data_backup"
            data_backup_path.mkdir(exist_ok=True)
            
            # Exportar datos de todas las tablas importantes
            from app import app
            from models import Vehicle, ClientRequest, Admin, Click, VehicleView, PageVisit, Gestor
            
            with app.app_context():
                # Backup de vehículos (con URLs de imágenes)
                vehicles_data = []
                vehicles = Vehicle.query.all()
                for vehicle in vehicles:
                    vehicle_data = {
                        'id': vehicle.id,
                        'title': vehicle.title,
                        'description': vehicle.description,
                        'price': vehicle.price,
                        'currency': vehicle.currency,
                        'year': vehicle.year,
                        'brand': vehicle.brand,
                        'model': vehicle.model,
                        'kilometers': vehicle.kilometers,
                        'fuel_type': vehicle.fuel_type,
                        'transmission': vehicle.transmission,
                        'color': vehicle.color,
                        'images': vehicle.images,  # JSON string con URLs
                        'main_image_index': vehicle.main_image_index,
                        'whatsapp_number': vehicle.whatsapp_number,
                        'call_number': vehicle.call_number,
                        'contact_type': vehicle.contact_type,
                        'phone_number': vehicle.phone_number,
                        'is_active': vehicle.is_active,
                        'is_plus': vehicle.is_plus,
                        'premium_duration_months': vehicle.premium_duration_months,
                        'premium_expires_at': vehicle.premium_expires_at.isoformat() if vehicle.premium_expires_at else None,
                        'created_at': vehicle.created_at.isoformat(),
                        'updated_at': vehicle.updated_at.isoformat(),
                        'location': vehicle.location,
                        'tire_condition': vehicle.tire_condition,
                        'seller_keyword': vehicle.seller_keyword,
                        'client_request_id': vehicle.client_request_id,
                        'full_name': getattr(vehicle, 'full_name', None),
                        'dni': getattr(vehicle, 'dni', None),
                        'email': getattr(vehicle, 'email', None),
                        'address': getattr(vehicle, 'address', None),
                        'doors': getattr(vehicle, 'doors', None),
                        'engine': getattr(vehicle, 'engine', None),
                        'condition': getattr(vehicle, 'condition', None),
                        'plan': getattr(vehicle, 'plan', None),
                        'mileage': getattr(vehicle, 'mileage', None)
                    }
                    vehicles_data.append(vehicle_data)
                
                # Backup de solicitudes de clientes
                requests_data = []
                requests = ClientRequest.query.all()
                for request in requests:
                    request_data = {
                        'id': request.id,
                        'full_name': request.full_name,
                        'dni': request.dni,
                        'whatsapp_number': request.whatsapp_number,
                        'call_number': request.call_number,
                        'phone_number': request.phone_number,
                        'location': request.location,
                        'address': request.address,
                        'seller_keyword': request.seller_keyword,
                        'title': request.title,
                        'description': request.description,
                        'price': request.price,
                        'currency': request.currency,
                        'year': request.year,
                        'brand': request.brand,
                        'model': request.model,
                        'kilometers': request.kilometers,
                        'fuel_type': request.fuel_type,
                        'transmission': request.transmission,
                        'color': request.color,
                        'images': request.images,  # JSON string con URLs
                        'main_image_index': request.main_image_index,
                        'publication_type': request.publication_type,
                        'status': request.status,
                        'admin_notes': request.admin_notes,
                        'created_at': request.created_at.isoformat(),
                        'updated_at': request.updated_at.isoformat(),
                        'processed_at': request.processed_at.isoformat() if request.processed_at else None,
                        'processed_by_admin_id': request.processed_by_admin_id
                    }
                    requests_data.append(request_data)
                
                # Backup de administradores
                admins_data = []
                admins = Admin.query.all()
                for admin in admins:
                    admin_data = {
                        'id': admin.id,
                        'username': admin.username,
                        'password_hash': admin.password_hash
                    }
                    admins_data.append(admin_data)
                
                # Backup de gestores
                gestores_data = []
                gestores = Gestor.query.all()
                for gestor in gestores:
                    gestor_data = {
                        'id': gestor.id,
                        'name': gestor.name,
                        'business_name': gestor.business_name,
                        'phone_number': gestor.phone_number,
                        'whatsapp_number': gestor.whatsapp_number,
                        'email': gestor.email,
                        'address': gestor.address,
                        'location': gestor.location,
                        'specializations': gestor.specializations,
                        'years_experience': gestor.years_experience,
                        'description': gestor.description,
                        'image_filename': gestor.image_filename,
                        'is_active': gestor.is_active,
                        'is_featured': gestor.is_featured,
                        'created_at': gestor.created_at.isoformat(),
                        'updated_at': gestor.updated_at.isoformat()
                    }
                    gestores_data.append(gestor_data)
            
            # Guardar todos los datos en archivos JSON
            with open(data_backup_path / "vehicles.json", 'w', encoding='utf-8') as f:
                json.dump(vehicles_data, f, indent=2, ensure_ascii=False)
            
            with open(data_backup_path / "client_requests.json", 'w', encoding='utf-8') as f:
                json.dump(requests_data, f, indent=2, ensure_ascii=False)
            
            with open(data_backup_path / "admins.json", 'w', encoding='utf-8') as f:
                json.dump(admins_data, f, indent=2, ensure_ascii=False)
            
            with open(data_backup_path / "gestores.json", 'w', encoding='utf-8') as f:
                json.dump(gestores_data, f, indent=2, ensure_ascii=False)
            
            # Crear resumen del backup
            summary = {
                'backup_date': datetime.datetime.now().isoformat(),
                'vehicles_count': len(vehicles_data),
                'requests_count': len(requests_data),
                'admins_count': len(admins_data),
                'gestores_count': len(gestores_data),
                'backup_type': 'data_only',
                'note': 'Este backup contiene solo datos (URLs de imágenes, no archivos físicos)'
            }
            
            with open(data_backup_path / "backup_summary.json", 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Backup de datos completado: {data_backup_path}")
            logging.info(f"Vehículos: {len(vehicles_data)}, Solicitudes: {len(requests_data)}, Admins: {len(admins_data)}, Gestores: {len(gestores_data)}")
            return True
            
        except Exception as e:
            logging.error(f"Error en backup de datos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def backup_config_files(self, backup_path):
        """Realiza backup de archivos de configuración críticos"""
        try:
            config_backup_path = backup_path / "config_backup"
            config_backup_path.mkdir(exist_ok=True)
            
            project_path = Path(self.config['project_path'])
            
            for config_file in self.config['config_files']:
                source_file = project_path / config_file
                if source_file.exists():
                    dest_file = config_backup_path / config_file
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    logging.info(f"Archivo de configuración respaldado: {config_file}")
                else:
                    logging.warning(f"Archivo de configuración no encontrado: {config_file}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error en backup de archivos de configuración: {e}")
            return False
    
    def create_backup_archive(self, backup_path, archive_name):
        """Crea un archivo comprimido del backup"""
        try:
            archive_path = backup_path.parent / f"{archive_name}.zip"
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, 
                               compresslevel=self.config['compression_level']) as zipf:
                
                # Check if backup_path has any files
                files_added = 0
                for file_path in backup_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(backup_path)
                        zipf.write(file_path, arcname)
                        files_added += 1
                
                # If no files were added, add a placeholder
                if files_added == 0:
                    zipf.writestr('backup_info.txt', f'Backup created on {datetime.datetime.now()}\nNo database or uploads found to backup.')
            
            # Eliminar carpeta temporal después de comprimir
            shutil.rmtree(backup_path)
            
            logging.info(f"Archivo de backup creado: {archive_path} ({files_added} archivos)")
            return archive_path
            
        except Exception as e:
            logging.error(f"Error creando archivo de backup: {e}")
            return None
    
    def create_backup_manifest(self, backup_info):
        """Crea un manifiesto con información del backup"""
        manifest = {
            'backup_date': backup_info['timestamp'],
            'backup_type': backup_info['type'],
            'files_backed_up': backup_info.get('files_count', 0),
            'total_size': backup_info.get('total_size', 0),
            'database_hash': backup_info.get('database_hash'),
            'success': backup_info.get('success', False),
            'errors': backup_info.get('errors', [])
        }
        
        manifest_file = backup_info['backup_path'].parent / f"{backup_info['archive_name']}_manifest.json"
        
        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            logging.info(f"Manifiesto creado: {manifest_file}")
        except Exception as e:
            logging.error(f"Error creando manifiesto: {e}")
    
    def create_backup(self, backup_type='manual'):
        """Alias para perform_backup para compatibilidad"""
        return self.perform_backup(backup_type)
    
    def perform_backup(self, backup_type='manual'):
        """Realiza un backup completo"""
        timestamp = datetime.datetime.now()
        backup_name = f"backup_{backup_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Determinar directorio según tipo de backup
        if backup_type == 'daily':
            target_dir = self.daily_dir
        elif backup_type == 'weekly':
            target_dir = self.weekly_dir
        elif backup_type == 'monthly':
            target_dir = self.monthly_dir
        else:
            target_dir = self.backup_dir
        
        backup_path = target_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"Iniciando backup {backup_type}: {backup_name}")
        
        backup_info = {
            'timestamp': timestamp.isoformat(),
            'type': backup_type,
            'backup_path': backup_path,
            'archive_name': backup_name,
            'success': True,
            'errors': []
        }
        
        try:
            # Backup de base de datos
            if not self.backup_database(backup_path):
                backup_info['errors'].append("Error en backup de base de datos")
                backup_info['success'] = False
            
            # Backup de datos (solo URLs, no archivos físicos)
            if not self.backup_data_only(backup_path):
                backup_info['errors'].append("Error en backup de datos")
                backup_info['success'] = False
            
            # Backup de archivos de configuración
            if not self.backup_config_files(backup_path):
                backup_info['errors'].append("Error en backup de configuración")
                backup_info['success'] = False
            
            # Crear archivo comprimido
            archive_path = self.create_backup_archive(backup_path, backup_name)
            if archive_path:
                backup_info['total_size'] = archive_path.stat().st_size
                backup_info['archive_path'] = str(archive_path)
            else:
                backup_info['errors'].append("Error creando archivo comprimido")
                backup_info['success'] = False
            
            # Crear manifiesto
            self.create_backup_manifest(backup_info)
            
            # Limpiar backups antiguos después de crear uno nuevo
            if backup_info['success']:
                logging.info(f"Backup {backup_type} completado exitosamente: {backup_name}")
                self.cleanup_old_backups(5)  # Mantener máximo 5 backups
            else:
                logging.error(f"Backup {backup_type} completado con errores: {backup_info['errors']}")
            
            return backup_info
            
        except Exception as e:
            logging.error(f"Error crítico durante backup: {e}")
            backup_info['success'] = False
            backup_info['errors'].append(f"Error crítico: {str(e)}")
            return backup_info
    
    def restore_backup(self, backup_file):
        """Restaura un backup desde archivo (nuevo formato JSON)"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return {
                    'success': False,
                    'error': f'Archivo de backup no encontrado: {backup_file}'
                }
            
            logging.info(f"Iniciando restauración desde: {backup_file}")
            
            # Verificar que es un archivo ZIP válido
            if not zipfile.is_zipfile(backup_path):
                return {
                    'success': False,
                    'error': 'El archivo no es un ZIP válido'
                }
            
            # Crear directorio temporal para extracción
            import tempfile
            temp_dir = Path(tempfile.mkdtemp())
            
            try:
                # Extraer el backup
                with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Buscar el directorio de datos
                data_backup_path = temp_dir / 'data_backup'
                
                if data_backup_path.exists():
                    # Nuevo formato: restaurar desde archivos JSON
                    return self._restore_from_json_data(data_backup_path)
                else:
                    # Formato antiguo: buscar base de datos SQLite
                    return self._restore_from_legacy_format(temp_dir)
                
            finally:
                # Limpiar directorio temporal
                shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            logging.error(f"Error durante la restauración: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _restore_from_json_data(self, data_backup_path):
        """Restaura datos desde archivos JSON"""
        try:
            from app import app
            from models import db, Vehicle, ClientRequest, Admin, Gestor
            
            with app.app_context():
                # Crear backup de seguridad de la base de datos actual
                current_db_path = Path(self.config['project_path']) / self.config['database_file']
                if current_db_path.exists():
                    backup_current = current_db_path.parent / f"{current_db_path.stem}_backup_before_restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy2(current_db_path, backup_current)
                    logging.info(f"Backup de seguridad creado: {backup_current}")
                
                # Leer archivos JSON
                vehicles_file = data_backup_path / 'vehicles.json'
                requests_file = data_backup_path / 'client_requests.json'
                admins_file = data_backup_path / 'admins.json'
                gestores_file = data_backup_path / 'gestores.json'
                summary_file = data_backup_path / 'backup_summary.json'
                
                # Leer resumen del backup
                if summary_file.exists():
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        summary = json.load(f)
                        logging.info(f"Restaurando backup del {summary.get('backup_date', 'fecha desconocida')}")
                        logging.info(f"Tipo: {summary.get('backup_type', 'desconocido')}")
                
                # Limpiar tablas existentes (excepto admins por seguridad)
                logging.info("Limpiando datos existentes...")
                db.session.query(Vehicle).delete()
                db.session.query(ClientRequest).delete()
                db.session.query(Gestor).delete()
                db.session.commit()
                
                restored_counts = {'vehicles': 0, 'requests': 0, 'admins': 0, 'gestores': 0}
                
                # Restaurar vehículos
                if vehicles_file.exists():
                    with open(vehicles_file, 'r', encoding='utf-8') as f:
                        vehicles_data = json.load(f)
                        
                    for vehicle_data in vehicles_data:
                        try:
                            # Convertir fechas de string a datetime
                            if vehicle_data.get('premium_expires_at'):
                                vehicle_data['premium_expires_at'] = datetime.datetime.fromisoformat(vehicle_data['premium_expires_at'])
                            if vehicle_data.get('created_at'):
                                vehicle_data['created_at'] = datetime.datetime.fromisoformat(vehicle_data['created_at'])
                            if vehicle_data.get('updated_at'):
                                vehicle_data['updated_at'] = datetime.datetime.fromisoformat(vehicle_data['updated_at'])
                            
                            # Crear nuevo vehículo
                            vehicle = Vehicle(**vehicle_data)
                            db.session.add(vehicle)
                            restored_counts['vehicles'] += 1
                        except Exception as e:
                            logging.error(f"Error restaurando vehículo {vehicle_data.get('id', 'desconocido')}: {e}")
                
                # Restaurar solicitudes de clientes
                if requests_file.exists():
                    with open(requests_file, 'r', encoding='utf-8') as f:
                        requests_data = json.load(f)
                        
                    for request_data in requests_data:
                        try:
                            # Convertir fechas de string a datetime
                            if request_data.get('created_at'):
                                request_data['created_at'] = datetime.datetime.fromisoformat(request_data['created_at'])
                            if request_data.get('updated_at'):
                                request_data['updated_at'] = datetime.datetime.fromisoformat(request_data['updated_at'])
                            if request_data.get('processed_at'):
                                request_data['processed_at'] = datetime.datetime.fromisoformat(request_data['processed_at'])
                            
                            # Crear nueva solicitud
                            request = ClientRequest(**request_data)
                            db.session.add(request)
                            restored_counts['requests'] += 1
                        except Exception as e:
                            logging.error(f"Error restaurando solicitud {request_data.get('id', 'desconocida')}: {e}")
                
                # Restaurar gestores
                if gestores_file.exists():
                    with open(gestores_file, 'r', encoding='utf-8') as f:
                        gestores_data = json.load(f)
                        
                    for gestor_data in gestores_data:
                        try:
                            # Convertir fechas de string a datetime
                            if gestor_data.get('created_at'):
                                gestor_data['created_at'] = datetime.datetime.fromisoformat(gestor_data['created_at'])
                            if gestor_data.get('updated_at'):
                                gestor_data['updated_at'] = datetime.datetime.fromisoformat(gestor_data['updated_at'])
                            
                            # Crear nuevo gestor
                            gestor = Gestor(**gestor_data)
                            db.session.add(gestor)
                            restored_counts['gestores'] += 1
                        except Exception as e:
                            logging.error(f"Error restaurando gestor {gestor_data.get('id', 'desconocido')}: {e}")
                
                # Restaurar administradores (solo si no existen)
                if admins_file.exists():
                    with open(admins_file, 'r', encoding='utf-8') as f:
                        admins_data = json.load(f)
                        
                    for admin_data in admins_data:
                        try:
                            # Verificar si el admin ya existe
                            existing_admin = Admin.query.filter_by(username=admin_data['username']).first()
                            if not existing_admin:
                                admin = Admin(**admin_data)
                                db.session.add(admin)
                                restored_counts['admins'] += 1
                            else:
                                logging.info(f"Admin {admin_data['username']} ya existe, omitiendo")
                        except Exception as e:
                            logging.error(f"Error restaurando admin {admin_data.get('username', 'desconocido')}: {e}")
                
                # Confirmar cambios
                db.session.commit()
                
                logging.info(f"Restauración completada:")
                logging.info(f"- Vehículos: {restored_counts['vehicles']}")
                logging.info(f"- Solicitudes: {restored_counts['requests']}")
                logging.info(f"- Gestores: {restored_counts['gestores']}")
                logging.info(f"- Administradores: {restored_counts['admins']}")
                
                return {
                    'success': True,
                    'message': f'Backup restaurado exitosamente. Vehículos: {restored_counts["vehicles"]}, Solicitudes: {restored_counts["requests"]}, Gestores: {restored_counts["gestores"]}, Admins: {restored_counts["admins"]}',
                    'restored_counts': restored_counts
                }
                
        except Exception as e:
            logging.error(f"Error restaurando desde JSON: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Error restaurando datos: {str(e)}'
            }
    
    def _restore_from_legacy_format(self, temp_dir):
        """Restaura desde formato antiguo (base de datos SQLite)"""
        try:
            # Buscar el archivo de base de datos en el backup
            db_backup_path = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.db') or file == self.config['database_file']:
                        db_backup_path = Path(root) / file
                        break
                if db_backup_path:
                    break
            
            if not db_backup_path or not db_backup_path.exists():
                return {
                    'success': False,
                    'error': 'No se encontró archivo de base de datos en el backup'
                }
            
            # Ruta de la base de datos actual
            current_db_path = Path(self.config['project_path']) / self.config['database_file']
            
            # Hacer backup de la base de datos actual antes de restaurar
            if current_db_path.exists():
                backup_current = current_db_path.parent / f"{current_db_path.stem}_backup_before_restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(current_db_path, backup_current)
                logging.info(f"Backup de seguridad creado: {backup_current}")
            
            # Restaurar la base de datos
            shutil.copy2(db_backup_path, current_db_path)
            logging.info(f"Base de datos restaurada desde: {db_backup_path}")
            
            return {
                'success': True,
                'message': f'Backup legacy restaurado exitosamente'
            }
            
        except Exception as e:
            logging.error(f"Error restaurando formato legacy: {e}")
            return {
                'success': False,
                'error': f'Error restaurando backup legacy: {str(e)}'
            }

    def cleanup_old_backups(self, max_backups=5):
        """Elimina backups antiguos manteniendo solo los más recientes (máximo 5)"""
        try:
            # Recopilar todos los backups de todos los directorios
            all_backups = []
            
            for backup_dir in [self.daily_dir, self.weekly_dir, self.monthly_dir, self.backup_dir]:
                if backup_dir.exists():
                    for item in backup_dir.iterdir():
                        if item.is_file() and item.suffix == '.zip':
                            try:
                                # Extraer fecha del nombre del archivo
                                date_str = item.stem.split('_')[-2] + '_' + item.stem.split('_')[-1]
                                file_date = datetime.datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                                all_backups.append({
                                    'file': item,
                                    'date': file_date,
                                    'manifest': item.parent / f"{item.stem}_manifest.json"
                                })
                            except (ValueError, IndexError):
                                logging.warning(f"No se pudo parsear fecha del archivo: {item}")
            
            # Ordenar por fecha (más recientes primero)
            all_backups.sort(key=lambda x: x['date'], reverse=True)
            
            # Eliminar backups que excedan el límite
            if len(all_backups) > max_backups:
                backups_to_delete = all_backups[max_backups:]
                
                for backup_info in backups_to_delete:
                    try:
                        # Eliminar archivo de backup
                        backup_info['file'].unlink()
                        logging.info(f"Backup eliminado: {backup_info['file']}")
                        
                        # Eliminar manifiesto asociado si existe
                        if backup_info['manifest'].exists():
                            backup_info['manifest'].unlink()
                            logging.info(f"Manifiesto eliminado: {backup_info['manifest']}")
                            
                    except Exception as e:
                        logging.error(f"Error eliminando backup {backup_info['file']}: {e}")
                
                logging.info(f"Limpieza completada. Mantenidos {max_backups} backups más recientes, eliminados {len(backups_to_delete)}")
            else:
                logging.info(f"No es necesaria limpieza. Backups actuales: {len(all_backups)}, límite: {max_backups}")
                
        except Exception as e:
            logging.error(f"Error durante limpieza de backups: {e}")
    
    def schedule_backups(self):
        """Programa los backups automáticos"""
        # Backup diario
        daily_time = self.config['backup_schedule']['daily']
        schedule.every().day.at(daily_time).do(self.perform_backup, 'daily')
        
        # Backup semanal
        weekly_day = self.config['backup_schedule']['weekly']
        schedule.every().week.at(daily_time).do(self.perform_backup, 'weekly')
        
        # Backup mensual (primer día del mes)
        schedule.every().month.do(self.perform_backup, 'monthly')
        
        # Limpieza de backups antiguos (diaria) - mantener máximo 5
        schedule.every().day.at("03:00").do(self.cleanup_old_backups, 5)
        
        logging.info("Backups programados:")
        logging.info(f"- Diario: {daily_time}")
        logging.info(f"- Semanal: {weekly_day} a las {daily_time}")
        logging.info(f"- Mensual: primer día del mes")
        logging.info("- Limpieza: diaria a las 03:00")
    
    def run_scheduler(self):
        """Ejecuta el programador de backups"""
        self.schedule_backups()
        
        logging.info("Sistema de backup iniciado. Presiona Ctrl+C para detener.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        except KeyboardInterrupt:
            logging.info("Sistema de backup detenido por el usuario.")

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        backup_manager = BackupManager()
        
        if command == 'backup':
            backup_type = sys.argv[2] if len(sys.argv) > 2 else 'manual'
            backup_manager.perform_backup(backup_type)
        elif command == 'schedule':
            backup_manager.run_scheduler()
        elif command == 'cleanup':
            backup_manager.cleanup_old_backups()
        else:
            print("Uso: python backup_system.py [backup|schedule|cleanup] [tipo]")
            print("Tipos de backup: manual, daily, weekly, monthly")
    else:
        # Ejecutar backup manual por defecto
        backup_manager = BackupManager()
        backup_manager.perform_backup('manual')

if __name__ == "__main__":
    main()
