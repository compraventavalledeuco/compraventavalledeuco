#!/usr/bin/env python3
"""
Script para depurar el problema de selección de imagen principal en Heroku
"""

import os
import sys
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_main_image_heroku():
    """Depurar el estado de la selección de imagen principal en Heroku"""
    try:
        from app import app, db
        from models import Vehicle, ClientRequest
        
        with app.app_context():
            logger.info("=== DEPURACIÓN DE SELECCIÓN DE IMAGEN PRINCIPAL ===")
            
            # Verificar vehículos existentes
            vehicles = Vehicle.query.limit(5).all()
            logger.info(f"📊 Total de vehículos encontrados: {len(vehicles)}")
            
            for i, vehicle in enumerate(vehicles, 1):
                logger.info(f"🚗 Vehículo {i} (ID: {vehicle.id})")
                logger.info(f"   Marca: {vehicle.brand}, Modelo: {vehicle.model}")
                logger.info(f"   main_image_index: {vehicle.main_image_index}")
                
                # Verificar imágenes
                images = vehicle.get_images_list()
                logger.info(f"   Total imágenes: {len(images)}")
                
                if images:
                    for idx, img in enumerate(images[:3]):  # Solo mostrar primeras 3
                        is_main = "⭐ PRINCIPAL" if idx == vehicle.main_image_index else ""
                        logger.info(f"     [{idx}] {img[:50]}... {is_main}")
                    
                    # Verificar imagen principal
                    main_image = vehicle.get_main_image()
                    logger.info(f"   Imagen principal actual: {main_image[:50]}...")
                else:
                    logger.info("   ❌ Sin imágenes")
            
            # Verificar solicitudes de cliente pendientes
            logger.info("=== SOLICITUDES DE CLIENTE ===")
            client_requests = ClientRequest.query.filter_by(status='pending').limit(3).all()
            logger.info(f"📋 Solicitudes pendientes: {len(client_requests)}")
            
            for i, req in enumerate(client_requests, 1):
                logger.info(f"📝 Solicitud {i} (ID: {req.id})")
                logger.info(f"   Marca: {req.brand}, Modelo: {req.model}")
                logger.info(f"   main_image_index: {req.main_image_index}")
                
                images = req.get_images_list()
                logger.info(f"   Total imágenes: {len(images)}")
                
                if images:
                    for idx, img in enumerate(images[:2]):  # Solo mostrar primeras 2
                        is_main = "⭐ PRINCIPAL" if idx == req.main_image_index else ""
                        logger.info(f"     [{idx}] {img[:50]}... {is_main}")
            
            logger.info("✅ Depuración completada exitosamente")
            
    except Exception as e:
        logger.error(f"❌ Error durante la depuración: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_main_image_heroku()
