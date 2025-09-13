@echo off
echo ========================================
echo VERIFICANDO ESTADO DE POSTGRESQL HEROKU
echo ========================================
echo.

:check_loop
echo Verificando estado de PostgreSQL...
heroku addons:info postgresql-polished-67208 --app compraventavalledeuco | findstr "State:"

heroku addons:info postgresql-polished-67208 --app compraventavalledeuco | findstr "State: provisioned" >nul
if %errorlevel% equ 0 (
    echo.
    echo ✅ PostgreSQL esta listo!
    echo.
    echo Verificando nueva DATABASE_URL...
    heroku config:get DATABASE_URL --app compraventavalledeuco
    echo.
    echo ========================================
    echo PROXIMOS PASOS:
    echo 1. Ejecutar: .\init_db_heroku.bat
    echo 2. Tu app ya usara PostgreSQL automaticamente
    echo ========================================
    goto end
) else (
    echo ⏳ PostgreSQL aun se esta creando... esperando 10 segundos
    timeout /t 10 /nobreak >nul
    goto check_loop
)

:end
pause
