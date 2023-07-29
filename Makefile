
#Создать пользователя для админки
create_super_user:
	cd back && docker exec -it back_web_1 python3 manage.py createsuperuser

#Сделать миграции в бд
back_migrate:
	cd back && docker exec -it back_web_1 python3 manage.py migrate

#Включить контейнеры приложения
up_app:
	cd back && docker-compose -f docker-compose.dev.yml up --build

#Отключить контейнеры приложения 
down_app:
	cd back && docker-compose -f docker-compose.dev.yml down