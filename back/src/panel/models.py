from django.db import models
from src.my_parser.models import ParserSite

class PanelUser(models.Model):
    """
        Класс для аккаунта пользователей панели
    """
    email = models.EmailField('E-Mail', max_length=255, unique=True)
    join_date = models.DateTimeField('Дата добавления', auto_now_add=True)
    password = models.CharField('Пароль', max_length=255)

    @property
    def is_authenticated(self):
        """
            Всегда возращает True, это способ узнать был ли пользователь аутентифицирован
        """
        return True


class SiteUser(models.Model):
    """
        Класс для пользователей парсера с сайта
    """

    WORK = 'work'
    PAUSED = 'paused'
    BLOCKED = 'blocked'

    STATUS_LIST = [
        (WORK, 'В работе'),
        (BLOCKED, 'В отстойнике'),
        (PAUSED, 'Не используется'),
    ]

    login = models.CharField('Логин', max_length=255)
    password = models.CharField('Пароль', max_length=255)
    create_date = models.DateTimeField('Дата добавления', auto_now_add=True)
    status = models.CharField('Статус', choices=STATUS_LIST, default=PAUSED, max_length=255)
    blocked = models.BooleanField('Заблокирован', null=True, blank=True)
    blocked_date = models.DateTimeField('Дата блокировки', null=True, blank=True)
    block_count = models.PositiveIntegerField('Количество блокировок', default=0, blank=True)
    count_requests = models.PositiveIntegerField('Количество сделаных запросов', default=0, blank=True)
    max_count_requests = models.PositiveIntegerField('Максимальное количество запросов', default=950)
    site = models.ForeignKey(ParserSite, verbose_name=("Сайт аккаунта"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.site.name}: {self.login}@{self.password}'


class Proxy(models.Model):
    """
        Модель прокси
    """
    type = models.CharField('Тип прокси', max_length=20)
    ip = models.CharField('IP прокси', max_length=255)
    port = models.CharField('Порт прокси', max_length=20)
    login = models.CharField('Логин', max_length=255, null=True, blank=True)
    password = models.CharField('Пароль прокси', max_length=255, null=True, blank=True)
    status = models.BooleanField('Статус вкл/выкл', default=False, blank=True)
    isUsed = models.BooleanField('Использовано', default=False, blank=True)
    request_count = models.PositiveIntegerField('Количество запросов с прокси', default=0, blank=True)

    request_time = models.DateTimeField('Время последнего использования прокси', blank=True, auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = 'Прокси'
        verbose_name_plural = 'Прокси'

    def __str__(self):
        return f'{self.ip}:{self.port}'
