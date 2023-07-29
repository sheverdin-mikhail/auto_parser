up_api:
	cd auto_parser-back_2 && ./myenv/bin/activate && python3 manage.py runserver

up_celery:
	cd auto_parser-back_2 && ./myenv/bin/activate && celery -A config worker -l info

up_front:
	cd auto-parser-front && npm start