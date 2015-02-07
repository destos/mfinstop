web: gunicorn --pythonpath="$PWD/mfinstop" wsgi:application
worker: celery worker --app=celery_tasks.app
