@echo off
echo ========================================
echo SUBIENDO MARKETPLACE VALLE DE UCO A GITHUB
echo ========================================

echo.
echo Configurando repositorio remoto...
git remote set-url origin https://github.com/compraventavalledeuco/compraventavalledeuco.git

echo.
echo Agregando archivos principales de la aplicacion...
git add app.py
git add requirements.txt
git add models.py
git add routes.py

echo.
echo Agregando archivos de configuracion para despliegue...
git add Procfile
git add runtime.txt
git add .gitignore

echo.
echo Agregando templates y archivos estaticos...
git add templates/
git add static/

echo.
echo Agregando documentacion y guias...
git add README.md
git add HEROKU_SETUP.md
git add HEROKU_BACKUP_SETUP.md
git add DEPLOYMENT_GUIDE.md
git add DEPLOY_GITHUB_HEROKU.md
git add CONFIGURACION_HEROKU_SUPABASE.md
git add INSTALL_HEROKU_CLI.md
git add verificar_logs_heroku.md
git add railway.json
git add render.yaml
git add pyproject.toml

echo.
echo Agregando archivos de configuracion adicionales...
git add main.py
git add config_local.py
git add run_local.py
git add test_db_connection.py

echo.
echo Agregando scripts de configuracion...
git add configurar_heroku_supabase.bat
git add init_db_heroku.bat
git add setup_heroku_postgres.bat
git add test_db_heroku.bat
git add subir_github.bat

echo.
echo Agregando sistema de backup...
git add backup_system/

echo.
echo Agregando scripts de inicializacion de produccion...
git add init_production_db.py
git add setup_production.bat
git add add_sample_data.py
git add add_seller_keyword_to_client_request.py
git add migrate_local_images_to_cloudinary.py


echo.
echo Agregando scripts de inicializacion de produccion...
git add init_production_db.py
git add setup_production.bat
git add add_sample_data.py

echo.
echo Verificando archivos agregados...
git status

echo.
echo Haciendo commit...
git commit -m "Seller Profile + ClientRequest.seller_keyword + scripts de migracion a Cloudinary"

echo.
echo Subiendo a GitHub...
git push origin main

echo.
echo ========================================
echo REPOSITORIO ACTUALIZADO EN GITHUB!
echo URL: https://github.com/compraventavalledeuco/compraventavalledeuco
echo ========================================

pause
