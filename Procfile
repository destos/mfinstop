web: gunicorn --pythonpath="$PWD/mfinstop" wsgi:application
celery: ./manage.py celery worker --app=celery_tasks.app
