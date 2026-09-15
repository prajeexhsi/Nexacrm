@echo off
if not exist venv\Scripts\python.exe (
  py -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
echo.
echo Start the CRM with: python manage.py runserver
echo Then open: http://127.0.0.1:8000/
pause
