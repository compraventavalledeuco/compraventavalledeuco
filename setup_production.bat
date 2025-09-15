@echo off
echo ========================================
echo CONFIGURACION DE PRODUCCION - VALLE DE UCO
echo ========================================

echo.
echo Este script te ayudara a inicializar la base de datos en produccion.
echo.

echo PASO 1: Conectate a tu servidor (Heroku/Railway/Render)
echo.
echo Para HEROKU:
echo   heroku run python init_production_db.py --app tu-app-name
echo.
echo Para RAILWAY:
echo   railway run python init_production_db.py
echo.
echo Para RENDER:
echo   Ejecuta en la consola web: python init_production_db.py
echo.

echo PASO 2: Alternativamente, usa el endpoint web:
echo   Visita: https://tu-dominio.com/admin/init-db
echo   (Requiere estar logueado como admin)
echo.

echo PASO 3: Verifica que funcione:
echo   Visita tu sitio web y deberia mostrar los vehiculos
echo.

echo ========================================
echo COMANDOS UTILES ADICIONALES:
echo ========================================
echo.
echo Ver logs en Heroku:
echo   heroku logs --tail --app tu-app-name
echo.
echo Reiniciar aplicacion en Heroku:
echo   heroku restart --app tu-app-name
echo.
echo Abrir consola en Heroku:
echo   heroku run bash --app tu-app-name
echo.

pause
