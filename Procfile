web: gunicorn --pythonpath="$PWD/mfinstop" wsgi:application
celery: celery worker --app=celery_tasks.app
