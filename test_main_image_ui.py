#!/usr/bin/env python3
"""
Script para probar la funcionalidad de selección de imagen principal desde la UI
"""

import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_main_image_ui():
    """Probar la funcionalidad completa de selección de imagen principal"""
    try:
        from app import app, db
        from models import Vehicle, ClientRequest
        
        with app.app_context():
            logger.info("=== PRUEBA DE FUNCIONALIDAD DE IMAGEN PRINCIPAL ===")
            
            # Buscar un vehículo con múltiples imágenes
            vehicle = Vehicle.query.filter(Vehicle.images.isnot(None)).first()
            
            if not vehicle:
                logger.error("❌ No se encontraron vehículos con imágenes para probar")
                return
            
            logger.info(f"🚗 Probando con vehículo ID: {vehicle.id}")
            logger.info(f"   Marca: {vehicle.brand}, Modelo: {vehicle.model}")
            
            images = vehicle.get_images_list()
            logger.info(f"   Total imágenes: {len(images)}")
            logger.info(f"   main_image_index actual: {vehicle.main_image_index}")
            
            # Mostrar todas las imágenes
            for idx, img in enumerate(images):
                is_main = "⭐ PRINCIPAL" if idx == vehicle.main_image_index else ""
                logger.info(f"     [{idx}] {img[:60]}... {is_main}")
            
            # Probar get_main_image()
            main_image = vehicle.get_main_image()
            logger.info(f"   get_main_image() retorna: {main_image[:60]}...")
            
            # Verificar que la imagen principal corresponde al índice correcto
            if vehicle.main_image_index < len(images):
                expected_main = images[vehicle.main_image_index]
                if main_image == expected_main:
                    logger.info("✅ La imagen principal coincide con el índice seleccionado")
                else:
                    logger.error("❌ La imagen principal NO coincide con el índice seleccionado")
                    logger.error(f"   Esperado: {expected_main[:60]}...")
                    logger.error(f"   Obtenido: {main_image[:60]}...")
            
            # Simular cambio de imagen principal
            logger.info("\n=== SIMULANDO CAMBIO DE IMAGEN PRINCIPAL ===")
            original_index = vehicle.main_image_index
            
            # Cambiar a la primera imagen
            vehicle.main_image_index = 0
            new_main = vehicle.get_main_image()
            logger.info(f"   Cambiado a índice 0: {new_main[:60]}...")
            
            # Cambiar a la última imagen
            vehicle.main_image_index = len(images) - 1
            new_main = vehicle.get_main_image()
            logger.info(f"   Cambiado a índice {len(images) - 1}: {new_main[:60]}...")
            
            # Restaurar índice original
            vehicle.main_image_index = original_index
            logger.info(f"   Restaurado a índice original: {original_index}")
            
            logger.info("✅ Prueba de funcionalidad completada exitosamente")
            
    except Exception as e:
        logger.error(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_main_image_ui()
