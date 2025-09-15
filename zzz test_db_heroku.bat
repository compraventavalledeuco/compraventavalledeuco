@echo off
echo ========================================
echo Probando Conectividad de Base de Datos
echo ========================================

echo.
echo Ejecutando test de conectividad...
heroku run python test_db_connection.py --app compraventavalledeuco

echo.
echo ========================================
echo Si el test falla, considera usar PostgreSQL de Heroku:
echo heroku addons:create heroku-postgresql:mini --app compraventavalledeuco
echo ========================================
pause
