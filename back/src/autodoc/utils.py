from datetime import datetime
from pandas import DataFrame
import requests
from django.core.mail import send_mail
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.my_parser.models import ParserOutputTask, ParserFindItem
from src.panel.utils import getProxy, getUser


def refresh_token(refresh_token):


    url = 'https://auth.autodoc.ru/token'
    headers = { 
        'Accept':	'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding':	'gzip, deflate, br',
        'Accept-Language':	'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection':	'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'null',
        'Content-Length': '1666',
        'Host':	'auth.autodoc.ru',
        'Sec-Fetch-Dest':	'document',
        'Sec-Fetch-Mode':	'navigate',
        'Sec-Fetch-Site':	'none',
        'Sec-Fetch-User':	'?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent':	'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'
    }

    data={
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }



    return requests.post(url=url, data=data, headers=headers).json()       





def get_token():
    user = getUser('autodoc')
    grant_type="password"

    url = 'https://auth.autodoc.ru/token'
    headers = { 
        'Accept':	'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding':	'gzip, deflate, br',
        'Accept-Language':	'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection':	'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'null',
        'Content-Length': '1666',
        'Host':	'auth.autodoc.ru',
        'Sec-Fetch-Dest':	'document',
        'Sec-Fetch-Mode':	'navigate',
        'Sec-Fetch-Site':	'none',
        'Sec-Fetch-User':	'?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent':	'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'
    }

    data={
        'username': user['login'],
        'password': user['password'],
        'grant_type': grant_type,
    }
      

    return requests.post(url=url, data=data, headers=headers).json()        
    

def get_data(code, make, token_data):

    if code == 'none_code':
        return []
    elif make == 'none_make':
        return []
    else:
        url = f"https://webapi.autodoc.ru/api/manufacturers/{code}?showAll=false"
        headers = { 
            'Accept':	'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding':	'gzip, deflate, br',
            'Accept-Language':	'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection':	'keep-alive',
            'Host':	'webapi.autodoc.ru',
            'Origin': 'https://www.autodoc.ru',
            'Referer': 'https://www.autodoc.ru/',
            'Sec-Fetch-Dest':	'document',
            'Sec-Fetch-Mode':	'navigate',
            'Sec-Fetch-Site':	'none',
            'Sec-Fetch-User':	'?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent':	'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
            'source_': 'Site2',
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
        for item in response_json:
            if item['manufacturerName'].lower() == make.lower().replace(' ', '-'):
                data =  get_data_for_id(item['id'], code, token_data)
                return data

def get_data_for_id(id, code, token_data):

    access_token = token_data['access_token']
    headers = { 
        'Accept':	'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding':	'gzip, deflate, br',
        'Accept-Language':	'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection':	'keep-alive',
        'Host':	'webapi.autodoc.ru',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.autodoc.ru',
        'Referer': 'https://www.autodoc.ru/',
        'Sec-Fetch-Dest':	'document',
        'Sec-Fetch-Mode':	'navigate',
        'Sec-Fetch-Site':	'none',
        'Sec-Fetch-User':	'?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent':	'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
        'source_': 'Site2',
        'Authorization': access_token
    }
    

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers = headers  
    url = f"https://webapi.autodoc.ru/api/spareparts/{id}/{code}/2"


    
    proxies = getProxy()


    response = session.get(
        url=url,
        headers=headers,
        verify=True,
        timeout=20,
        proxies=proxies
    )

    try_counter=0
    while True:
        if (len(response.json()['inventoryItems']) == 0):
            refresh_data = refresh_token(token_data['refresh_token'])
            access_token = f"{refresh_data['token_type']} {refresh_data['access_token']}"
            headers['Authorization'] = access_token
            response = session.get(
                url=url,
                headers=headers,
                verify=True,
                timeout=20,
                proxies=proxies
            )
            if try_counter == 10 :
                return None
            try_counter += 1
            
        else:
            response_json = response.json()
            return response_json

def save_data(data: list, row: DataFrame, id, marker, last_item: bool=False ):
    #Создание задания в бд
    output_task = ParserOutputTask.objects.create()
    output_task.site = 'autodoc.ru'
    output_task.start_date = datetime.now()
    output_task.task_id = id
    output_task.task_marker = f'{id}-{marker}'
    
    keys = ['non_code', 'not_find', 'non_make'] 
    if data==None:
        output_task.name = 'Данный товар с данным производителем и артикулом не найден'
    else:
        for item in data['inventoryItems']:
            #Добавление данных о товаре в таблицу товара
            try:
                offer = ParserFindItem.objects.get(offer_key=f"autodoc_{item['id']}")
                offer.rating = 'empty'
                offer.quantity = item['quantity']
                offer.delivery = item['deliveryDays']
                offer.price = item['price']
                offer.save()
            except ParserFindItem.DoesNotExist:
                offer = ParserFindItem.objects.create(offer_key=f"autodoc_{item['id']}")
                offer.rating = 'empty'
                offer.quantity = item['quantity']
                offer.delivery = item['deliveryDays']
                offer.price = item['price']
                offer.save()
            #Добавление полученного товара в список товаров задания
            output_task.finds_list.add(ParserFindItem.objects.get(offer_key=offer.offer_key))
    if(len(row)>3): #Проверка кол-ва колонок во входящей строке данных
        output_task.article = row[2]
        output_task.name = row[3]
        output_task.brand = row[4]

    else:
        output_task.article = row[0]
        output_task.name = row[1]
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

