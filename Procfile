web: python manage.py migrate && python manage.py seed_fact_data && python manage.py collectstatic --noinput && gunicorn laboratory_management.wsgi:application
