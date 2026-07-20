web: python manage.py migrate && python manage.py seed_bulk_data --count 40 && python manage.py collectstatic --noinput && gunicorn laboratory_management.wsgi:application
