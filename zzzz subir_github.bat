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
git add main.py

echo.
echo Agregando archivos de configuracion para despliegue...
git add Procfile
git add runtime.txt
git add .gitignore
git add pyproject.toml
git add railway.json
git add render.yaml

echo.
echo Agregando templates y archivos estaticos...
git add templates/
git add static/

echo.
echo Agregando documentacion y guias...
git add README.md
git add HEROKU_SETUP.md
git add HEROKU_BACKUP_SETUP.md
git add HEROKU_S3_SETUP.md
git add DEPLOYMENT_GUIDE.md
git add DEPLOY_GITHUB_HEROKU.md
git add CONFIGURACION_HEROKU_SUPABASE.md
git add INSTALL_HEROKU_CLI.md
git add verificar_logs_heroku.md
git add CLOUDINARY_SETUP.md

echo.
echo Agregando scripts de configuracion y testing...
git add configurar_heroku_supabase.bat
git add init_db_heroku.bat
git add setup_heroku_postgres.bat
git add test_db_heroku.bat
git add check_postgres_ready.bat
git add test_db_connection.py
git add test_supabase_connection.py
git add check_supabase_settings.py
git add run_local.py

echo.
echo Agregando sistema de backup...
git add backup_system/

echo.
echo Agregando scripts de base de datos y migracion...
git add init_production_db.py
git add setup_production.bat
git add add_sample_data.py
git add add_seller_keyword_column.py
git add add_seller_keyword_to_client_request.py
git add force_add_seller_keyword.py
git add migrate_db_direct.py
git add migrate_local_images_to_cloudinary.py
git add update_supabase_url.py
git add init_supabase_local.py

echo.
echo Agregando scripts de almacenamiento en la nube...
git add cloud_storage.py
git add cloudinary_storage.py
git add clear_broken_images.py

echo.
echo Agregando scripts de testing y debug...
git add test_seller_keyword.py
git add debug_seller_keyword.py
git add final_test.py

echo.
echo Agregando archivos de configuracion adicionales...
git add backup_state.json
git add incremental_backup_config.json

echo.
echo Agregando scripts de configuracion legacy...
git add "zzz setup_heroku_postgres.bat"
git add "zzz test_db_heroku.bat"
git add "zzzz subir_github.bat"

echo.
echo Verificando archivos agregados...
git status

echo.
echo Haciendo commit con timestamp...
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
git commit -m "Actualizacion completa del marketplace - %timestamp%"

echo.
echo Subiendo a GitHub...
git push origin main

echo.
echo ========================================
echo REPOSITORIO ACTUALIZADO EN GITHUB!
echo URL: https://github.com/compraventavalledeuco/compraventavalledeuco
echo ========================================

pause
