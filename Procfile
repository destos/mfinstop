web: gunicorn --pythonpath="$PWD/mfinstop" wsgi:application
celery: python manage.py celery worker --app=celery_tasks.app
