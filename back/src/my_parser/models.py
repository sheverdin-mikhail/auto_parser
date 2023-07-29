from email.policy import default
from re import T
from statistics import mode
from tabnanny import verbose
from unicodedata import name
from django.db import models
from django.core.validators import FileExtensionValidator
from django.forms import CharField

from src.base.services import get_path_upload_file
from .utils import firstParserSite


class ParserSite(models.Model):
    name = models.CharField(("Название сайта"), max_length=50)
    status = models.BooleanField('Сайт вкл/выкл', default=True)

    class Meta: 
        verbose_name = 'Сайт для парсинга'
        verbose_name_plural = 'Сайты для парсинга'
    
    def __str__(self) -> str:
        return self.name


class ParserInputFile(models.Model):
    file = models.FileField(
        'Входящие данные парсера',
        upload_to=get_path_upload_file,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['xlsx'])]
    )

    class Meta:
        verbose_name = 'Файл входных данных'
        verbose_name_plural = 'Файлы входных данных'

    def __str__(self):
        return self.file.name


class ParserTask(models.Model):
    READY = 'ready'
    RUN = 'run'
    DONE = 'done'

    STATUS_CHOISES = [
        (READY, 'Готов к выполнению'),
        (RUN, 'Выполняется'),
        (DONE, 'Выполнен'),
    ]

    ANALYTICS = '1'
    AVAILABILITY = '2'
    API = '3'
    TECH = '4'

    MARKER_CHOISES = [
        (ANALYTICS, 'Аналитика'),
        (AVAILABILITY, 'Наличие'),
        (API, 'API'),
        (TECH, 'Техническое'),
    ]

    sites = models.ManyToManyField("my_parser.ParserSite", verbose_name=("Сайты для парсинга"), default=firstParserSite, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    input_file = models.OneToOneField(ParserInputFile, verbose_name='Входные данные', on_delete=models.CASCADE, related_name="input_file")
    marker=models.CharField(('Маркер'), max_length=2, choices=MARKER_CHOISES, default=ANALYTICS)
    rows_count = models.IntegerField('Количество заданий', default=0, blank=True)
    status = models.CharField('Статус работы парсера', max_length=255, choices=STATUS_CHOISES, default=READY)


    class Meta:
        verbose_name = 'Задача парсер'
        verbose_name_plural = 'Задачи парсер'

    def __str__(self):
        return f'id: {self.pk} file:{self.input_file.file.name} create_date: {self.create_date}'




class ParserFindItem(models.Model):
    
    offer_key = models.CharField(('Индивидуальный ключ товара'), max_length=1024, primary_key=True, unique=True)
    rating = models.CharField(('Рейтинг'), max_length=1024, null=True, blank=True)
    quantity = models.IntegerField(('Наличие'), null=True, blank=True)
    delivery = models.IntegerField(('Срок доставки'), null=True, blank=True)
    price = models.IntegerField(('Цена'), blank=True, null=True)

    class Meta:
        verbose_name = 'Оффер задачи'
        verbose_name_plural = 'Оффер задачи'

    def __str__(self):
        return f'Рейтинг: {self.rating} Наличие, шт: {self.quantity} Срок, дн.: {self.delivery} Цена руб.: {self.price}'




class ParserOutputTask(models.Model):
    
    
    task_id = models.IntegerField(('ID исходной задачи'), blank=True, null=True)
    task_marker = models.CharField(('Поле для выборки'), max_length=255, blank=True, null=True)
    start_date = models.DateTimeField(("Дата начала работы парсера"), null=True, blank=True)
    city = models.CharField(("Город"), max_length=255, null=True, blank=True)
    stock = models.CharField(("Склад"), max_length=255, null=True, blank=True)
    site = models.CharField(('Сайт'), max_length=255, null=True, blank=True)
    article = models.CharField(('Артикул'), max_length=255, null=True, blank=True)
    name = models.CharField(('Наименование'), max_length=255, null=True, blank=True)
    brand = models.CharField(('Брэнд'), max_length=255, null=True, blank=True)
    free_balance = models.CharField(("Свободный остаток"), max_length=255, null=True, blank=True)
    arrival_price = models.CharField(('Цена прихода'), max_length=255, null=True, blank=True)
    holding_balance = models.CharField(('Остаток Холдинга (свободный)'), max_length=255, null=True, blank=True)
    holding_expense = models.CharField(('Расход Холдинга'), max_length=255, null=True, blank=True)
    implemented = models.CharField(('Можно реализовать в ИМ'), max_length=255, null=True, blank=True)
    finds_list = models.ManyToManyField(ParserFindItem, verbose_name=("Список найденных предложений"), null=True, blank=True)

    class Meta:
        verbose_name = 'Выходные данные задачи'
        verbose_name_plural = 'Выходные данные задачи'

    def __str__(self):
        return f'Дата: {self.start_date} | Артикул: {self.article} | Наименование: {self.name} | Брэнд: {self.brand}'



class InputDataArray(ParserOutputTask):

    class Meta:
        verbose_name = "Массив входных данных"
        verbose_name_plural = "Массив входных данных"

    def __str__(self):
        return self.name

    


class ParserTaskFromArray(models.Model):
    READY = 'ready'
    RUN = 'run'
    DONE = 'done'

    STATUS_CHOISES = [
        (READY, 'Готов к выполнению'),
        (RUN, 'Выполняется'),
        (DONE, 'Выполнен'),
    ]

    ANALYTICS = '1'
    AVAILABILITY = '2'
    TECH = '3'

    MARKER_CHOISES = [
        (ANALYTICS, 'Аналитика'),
        (AVAILABILITY, 'Наличие'),
        (TECH, 'Техническое'),
    ]

    sites = models.ManyToManyField("my_parser.ParserSite", verbose_name=("Сайты для парсинга"), default=firstParserSite, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    input_data = models.ManyToManyField("my_parser.InputDataArray", verbose_name=("Массив входных данных"))
    marker=models.CharField(('Маркер'), max_length=2, choices=MARKER_CHOISES, default=ANALYTICS)
    rows_count = models.IntegerField('Количество заданий', default=0, blank=True)
    status = models.CharField('Статус работы парсера', max_length=255, choices=STATUS_CHOISES, default=READY)


    class Meta:
        verbose_name = 'Задача парсер из массива'
        verbose_name_plural = 'Задачи парсер из массива'

    def __str__(self):
        return f'id: {self.pk} create_date: {self.create_date}'

