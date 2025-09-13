@echo off
echo ========================================
echo Inicializando Base de Datos en Heroku
echo ========================================

echo.
echo Ejecutando inicializacion de base de datos...
heroku run python app.py init-db --app compraventavalledeuco

echo.
echo Verificando logs de la aplicacion...
heroku logs --tail --app compraventavalledeuco

echo.
echo ========================================
echo Proceso completado
echo ========================================
pause
