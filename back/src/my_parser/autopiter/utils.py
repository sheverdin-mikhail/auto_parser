from datetime import datetime
from pandas import DataFrame
import requests
from django.core.mail import send_mail
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.my_parser.models import ParserOutputTask, ParserFindItem
from src.panel.utils import getProxy


def get_data(code, make):

    if code == 'none_code':
        return []
    elif make == 'none_make':
        return []
    else:
        url = f"https://autopiter.ru/api/api/searchdetails?detailNumber={code}"
    
        headers = { 
            'Accept':	'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding':	'gzip, deflate, br',
            'Accept-Language':	'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection':	'keep-alive',
            'Host':	'autopiter.ru',
            'Sec-Fetch-Dest':	'document',
            'Sec-Fetch-Mode':	'navigate',
            'Sec-Fetch-Site':	'none',
            'Sec-Fetch-User':	'?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent':	'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'
        }

        proxies = getProxy()
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers = headers   
        response = session.get(
            url=url,
            headers=headers,
            verify=True,
            timeout=20,
            proxies=proxies
        )
        response_json = response.json()
        for item in response_json['data']['catalogs']:
            if item['catalogUrl'] == make.lower().replace(' ', '-'):
                data = get_data_for_id(item['id'], item['catalogUrl'])
                return data

def get_data_for_id(id, make):

    
    headers = { 'Accept':	'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Encoding':	'gzip, deflate, br',
                'Accept-Language':	'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection':	'keep-alive',
                'Host':	'autopiter.ru',
                'Sec-Fetch-Dest':	'document',
                'Sec-Fetch-Mode':	'navigate',
                'Sec-Fetch-Site':	'none',
                'Sec-Fetch-User':	'?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent':	'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'
            }
    

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers = headers  
    url = f"https://autopiter.ru/api/api/appraise?id={id}&searchType=1"

    
    proxies = getProxy()


    response = session.get(
                url=url,
                headers=headers,
                verify=True,
                timeout=20,
                proxies=proxies
            )
    print(response)
    response_json = response.json()
    data = []
    for item in response_json['data']:
        if item['catalogUrl'] == make:
            data.append(item)
    return data


def save_data(data: list, row: DataFrame, id, marker, last_item: bool=False ):
    #Создание задания в бд
    output_task = ParserOutputTask.objects.create()
    output_task.site = 'autopiter.ru'
    output_task.start_date = datetime.now()
    output_task.task_id = id
    output_task.task_marker = f'{id}-{marker}'
    
    keys = ['non_code', 'not_find', 'non_make'] 
    if not data:
        output_task.name = 'Данный товар с данным производителем и артикулом не найден'
    else:
        output_task.name = data[0]['name']
        for item in data:
            #Добавление данных о товаре в таблицу товара
            try:
                offer = ParserFindItem.objects.get(offer_key=item['detailUid'])
                offer.rating = item['rank']/2
                offer.quantity = item['quantity']
                offer.delivery = item['deliveryDays']
                offer.price = item['price']
                offer.save()
            except ParserFindItem.DoesNotExist:
                offer = ParserFindItem.objects.create(offer_key=item['detailUid'])
                offer.rating = item['rank']/2
                offer.quantity = item['quantity']
                offer.delivery = item['deliveryDays']
                offer.price = item['price']
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

