web: gunicorn --pythonpath="$PWD/mfinstop" wsgi:application
celery: python mfinstop/manage.py celery worker --app=celery_tasks.app
