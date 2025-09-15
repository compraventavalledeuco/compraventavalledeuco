@echo off
echo ========================================
echo PRUEBA DE CONEXION A HEROKU POSTGRESQL
echo ========================================
echo.
echo PASO 1: Verificar que tienes Heroku CLI instalado
heroku --version
if %errorlevel% neq 0 (
    echo ERROR: Heroku CLI no esta instalado
    echo Descarga desde: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

echo.
echo PASO 2: Login a Heroku (si no estas logueado)
heroku auth:whoami
if %errorlevel% neq 0 (
    echo Necesitas hacer login...
    heroku login
)

echo.
echo PASO 3: Listar tus apps de Heroku
echo Tus apps disponibles:
heroku apps

echo.
echo ========================================
echo INSTRUCCIONES PARA CONFIGURAR POSTGRESQL:
echo ========================================
echo.
echo 1. Identifica el nombre de tu app de la lista anterior
echo 2. Ejecuta: heroku addons:create heroku-postgresql:essential-0 --app TU-APP-NAME
echo 3. Verifica: heroku config --app TU-APP-NAME
echo 4. Heroku automaticamente creara la variable DATABASE_URL
echo.
echo EJEMPLO:
echo   heroku addons:create heroku-postgresql:essential-0 --app mi-marketplace
echo   heroku config --app mi-marketplace
echo.
echo ========================================
pause
