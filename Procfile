web: python manage.py migrate && python manage.py correct_patient_genders && python manage.py collectstatic --noinput && gunicorn laboratory_management.wsgi:application
