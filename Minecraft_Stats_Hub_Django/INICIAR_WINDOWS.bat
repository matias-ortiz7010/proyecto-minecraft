@echo off
setlocal
cd /d "%~dp0"

if not exist .venv (
    echo Creando entorno virtual...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Instalando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Preparando base de datos...
python manage.py makemigrations stats
if errorlevel 1 goto :error
python manage.py migrate
if errorlevel 1 goto :error

echo.
echo Si es la primera vez y queres datos de prueba, ejecuta en otra consola:
echo python manage.py seed_demo
echo.
echo Abriendo servidor en http://127.0.0.1:8000/
python manage.py runserver
goto :eof

:error
echo.
echo Hubo un error. Revisa que Python este instalado y disponible como "python".
pause
