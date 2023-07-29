from config.celery import app
from datetime import datetime, timedelta

@app.task
def reset_proxies():

    from .models import Proxy 

    # Вычисляем временную метку, представляющую текущее время минус 1 минуты
    two_minutes_ago = datetime.now() - timedelta(minutes=1)

    # Выполняем запрос на получение прокси, которые были изменены не менее 1 минут назад
    proxies = Proxy.objects.filter(request_time__lte=two_minutes_ago, isUsed=True, status=True)

    for proxy in proxies:
        proxy.isUsed = False
        proxy.save()

    print(f'{len(proxies)} проксей сброшено')
