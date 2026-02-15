web: python manage.py migrate && python manage.py createcachetable && gunicorn 
handbook_project.wsgi --bind 0.0.0.0:$PORT