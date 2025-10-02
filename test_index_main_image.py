#!/usr/bin/env python3
"""
Script para probar específicamente la imagen principal en el index
"""

import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_index_main_image():
    """Probar cómo se muestra la imagen principal en el index"""
    try:
        from app import app, db
        from models import Vehicle
        
        with app.app_context():
            logger.info("=== PRUEBA DE IMAGEN PRINCIPAL EN INDEX ===")
            
            # Buscar el vehículo específico
            vehicle = Vehicle.query.get(23)
            
            if not vehicle:
                logger.error("❌ No se encontró el vehículo ID 23")
                return
            
            logger.info(f"🚗 Vehículo ID: {vehicle.id}")
            logger.info(f"   Título: {vehicle.title}")
            logger.info(f"   main_image_index: {vehicle.main_image_index}")
            
            # Obtener lista de imágenes
            images = vehicle.get_images_list()
            logger.info(f"   Total imágenes: {len(images)}")
            
            # Mostrar todas las imágenes con sus índices
            for idx, img in enumerate(images):
                is_main = "⭐ PRINCIPAL" if idx == vehicle.main_image_index else ""
                logger.info(f"     [{idx}] {img} {is_main}")
            
            # Probar get_main_image()
            main_image = vehicle.get_main_image()
            logger.info(f"\n🎯 get_main_image() retorna:")
            logger.info(f"   {main_image}")
            
            # Verificar si coincide con el índice esperado
            if vehicle.main_image_index < len(images):
                expected_image = images[vehicle.main_image_index]
                logger.info(f"\n🔍 Imagen esperada (índice {vehicle.main_image_index}):")
                logger.info(f"   {expected_image}")
                
                if main_image == expected_image:
                    logger.info("✅ ¡CORRECTO! get_main_image() retorna la imagen del índice correcto")
                else:
                    logger.error("❌ ERROR: get_main_image() NO retorna la imagen del índice correcto")
                    logger.error("   Esto indica un problema en el método get_main_image()")
            
            # Simular lo que hace el template del index
            logger.info(f"\n📄 Simulación del template index.html:")
            if images:
                template_condition = f"vehicle.get_images_list() = {len(images) > 0} (True)"
                logger.info(f"   {template_condition}")
                
                # Simular la lógica del template
                if main_image.startswith('http'):
                    final_url = main_image
                else:
                    final_url = f"/static/{main_image}"
                
                logger.info(f"   URL final que se mostraría: {final_url}")
            else:
                logger.info("   Se mostraría placeholder (sin imágenes)")
            
            logger.info("✅ Prueba completada")
            
    except Exception as e:
        logger.error(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_index_main_image()
