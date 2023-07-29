from datetime import datetime
from pandas import DataFrame
import requests
import time
from django.core.mail import send_mail
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.my_parser.models import ParserOutputTask, ParserFindItem
from src.panel.utils import getProxy


def get_data(code, make):

    while True:
        proxies, proxy = getProxy()
        if proxies:
            break

    url = f"https://emex.ru/api/search/search?make={str(make).lower().replace('-', '--').replace(' ', '-')}&detailNum={str(code)}&locationId=31980&longitude=37.6318&latitude=55.7583"
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
        'Accept' : 'image/avif,image/webp,*/*'
    }

    if code == 'none_code':
        return {'none_code': 'Не указан код', 'make': make}
    elif make == 'none_make':
        return {'non_make': 'Не казан производитель', 'code': code}
    else:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers = headers        
        while True:
            response = session.get(
                url=url,
                headers=headers,
                verify=True,
                timeout=20,
                proxies=proxies
                )
            time.sleep(60)
            proxy.isUsed = False
            proxy.save()
            if 'originals' in response.json()['searchResult']:
                print('Запрос сделан')
                return response.json()['searchResult']['originals'][0]
            else:
                return {'not_find': response.json()['searchResult']['num'], 'make': response.json()['searchResult']['make']}


def save_data(data: dict, row: DataFrame, id, marker, last_item: bool=False ):
    #Создание задания в бд
    output_task = ParserOutputTask.objects.create()
    output_task.site = 'emex.ru'
    output_task.start_date = datetime.now()
    output_task.task_id = id
    output_task.task_marker = f'{id}-{marker}'

    keys = ['non_code', 'not_find', 'non_make'] 
    if any(key in data for key in keys):
        output_task.name = 'Данный товар с данным производителем и артикулом не найден'
    else:
        output_task.name = data['name']
        for i in range(len(data['offers'])):
            #Добавление данных о товаре в таблицу товара
            try:
                offer = ParserFindItem.objects.get(offer_key=data['offers'][i]['offerKey'])
                offer.rating = data['offers'][i]['rating2']['rating']
                offer.quantity = data['offers'][i]['quantity']
                offer.delivery = data['offers'][i]['delivery']['value']
                offer.price = data['offers'][i]['displayPrice']['value']
                offer.save()
            except ParserFindItem.DoesNotExist:
                offer = ParserFindItem.objects.create(offer_key=data['offers'][i]['offerKey'])
                offer.rating = data['offers'][i]['rating2']['rating']
                offer.quantity = data['offers'][i]['quantity']
                offer.delivery = data['offers'][i]['delivery']['value']
                offer.price = data['offers'][i]['displayPrice']['value']
                offer.save()
            #Добавление полученного товара в список товаров задания
            output_task.finds_list.add(ParserFindItem.objects.get(offer_key=offer.offer_key))
    if(len(row)>3): #Проверка кол-ва колонок во входящей строке данных
        output_task.article = row[2]
        output_task.brand = row[4]
    else:
        output_task.article = row[0]
        output_task.brand = row[2]

    #Добавление данных в таблицу из строки файла
    if(len(row)>3):
        output_task.city = row[0]
        output_task.stock = row[1]
        output_task.free_balance = row[5]
        output_task.arrival_price = row[6]
    if(len(row)>8):
        output_task.holding_balance = row[7]
        output_task.holding_expense = row[8]
        output_task.implemented = row[9]
    output_task.save()

    if last_item:
        from src.my_parser.models import ParserTask
        from django.contrib.auth.models import User
        task = ParserTask.objects.get(id=id)
        task.status = 'done'
        task.save()
        admin = User.objects.all().first()
        sended = send_mail(
                'Информация об окончании работы парсера.', 
                f'Задача номер - {task.pk} выполнена.', 
                'parser@uitdep.ru', 
                [admin.email], 
                fail_silently=False
        )

