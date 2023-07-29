import datetime

import pandas as pd
from django.core.mail import send_mail
import aiohttp
import asyncio

from src.my_parser.models import ParserOutputTask, ParserFindItem



def get_data_from_file(file_name):
    excel_data = pd.read_excel(file_name, engine='openpyxl')

    result = []
    if(len(excel_data.columns)>3):
        for item in excel_data.values:
            if str(item[2]) != 'nan' and str(item[4]) != 'nan':
                if item[4] == 'Китай':
                    result.append({item[2]: 'unknownbrand'})
                else:
                    result.append({item[2]: item[4]})
            elif str(item[2]) == 'nan':
                result.append({'none_code': item[4]})
            elif str(item[4]) == 'nan':
                result.append({item[2]: 'none_make'})
    else:
        for item in excel_data.values:
            if str(item[0]) != 'nan' and str(item[2]) != 'nan':
                if item[2] == 'Китай':
                    result.append({item[0]: 'unknownbrand'})
                else:
                    result.append({item[0]: item[2]})
            elif str(item[0]) == 'nan':
                result.append({'none_code': item[2]})
            elif str(item[2]) == 'nan':
                result.append({item[0]: 'none_make'})
    return result


def get_data_from_task(task, columns):
    excel_data = task
    result = []
    if(columns>3):
        for item in excel_data:
            if str(item[2]) != 'nan' and str(item[4]) != 'nan':
                if item[4] == 'Китай':
                    result.append({item[2]: 'unknownbrand'})
                else:
                    result.append({item[2]: item[4]})
            elif str(item[2]) == 'nan':
                result.append({'none_code': item[4]})
            elif str(item[4]) == 'nan':
                result.append({item[2]: 'none_make'})
    else:
        for item in excel_data:
            if str(item[0]) != 'nan' and str(item[2]) != 'nan':
                if item[2] == 'Китай':
                    result.append({item[0]: 'unknownbrand'})
                else:
                    result.append({item[0]: item[2]})
            elif str(item[0]) == 'nan':
                result.append({'none_code': item[2]})
            elif str(item[2]) == 'nan':
                result.append({item[0]: 'none_make'})
    return result

async def get_page_data(session, code, make):

    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0', }
    url = f"https://emex.ru/api/search/search?make={str(make).lower().replace('-', '--').replace(' ', '-')}&detailNum={str(code)}&locationId=31980&longitude=37.6318&latitude=55.7583"

    if code == 'none_code':
        return {'none_code': 'Не указан код', 'make': make}
    elif make == 'none_make':
        return {'non_make': 'Не казан производитель', 'code': code}
    else:
        max_retries = 5
        attempt = 0
        while True:
            try:
                login = 'VpxTGE'
                password = 'q0fSf5'
                proxy = f'http://{login}:{password}@45.81.78.54:8000'
                async with session.get(url=url,
                                    headers=headers,
                                    timeout=10,
                                    ssl=False,
                                    proxy=proxy 
                                    ) as response:
                    response_json = await response.json()

                    if 'originals' in response_json['searchResult']:
                        print(f'{code}: {make}')
                        return response_json['searchResult']['originals'][0]
                    else:
                        print(f'{code}: {make}')
                        return {'not_find': response_json['searchResult']['num'],
                                'make': response_json['searchResult']['make']}
            except (
                aiohttp.ClientOSError,  
                aiohttp.ServerDisconnectedError,
                asyncio.exceptions.TimeoutError,
            ):
                if attempt < max_retries:
                    attempt += 1
                else:
                    attempt =0
                    await asyncio.sleep(10)

async def gather_data(task, columns):
    input_data = get_data_from_task(task, columns)

    async with aiohttp.ClientSession() as session:
        # retry = Retry(connect=3, backoff_factor=0.5)
        # adapter = HTTPAdapter(max_retries=retry)
        # session.mount('http://', adapter)
        # session.mount('https://', adapter)

        tasks = []

        for item in input_data:
            for key in item:
                task = asyncio.create_task(get_page_data(session, key, item[key]))
                tasks.append(task)

        return await asyncio.gather(*tasks)

def create_output_from_data(data, start_date, excel_data, columns, id, index_from, last_index):
    max_offers = 0
    for i in range(len(data)):
        if 'offers' in data[i]:
            if max_offers < data[i]['count']:
                max_offers = data[i]['count']
                
    for index, item in enumerate(data):
        #Создание задания в бд
        output_task = ParserOutputTask.objects.create()
        output_task.site = 'emex.ru'
        output_task.start_date = datetime.datetime.now()



        if(columns>3):
            output_task.article = excel_data[index][2]
            output_task.brand = excel_data[index][4]
        else:
            output_task.article = excel_data[index][0]
            output_task.brand = excel_data[index][2]

        if(columns>3):
            output_task.city = excel_data[index][0]
            output_task.stock = excel_data[index][1]
            output_task.free_balance = excel_data[index][5]
            output_task.arrival_price = excel_data[index][6]
        if(columns>8):
            output_task.holding_balance = excel_data[index][7]
            output_task.holding_expense = excel_data[index][8]
            output_task.implemented = excel_data[index][9]
            
        output_task.save()

        #Создание строки для сохранения в excel
        if 'not_find' in item:
            output_task.name = 'Данный товар с данным производителем и артикулом не найден'
            output_task.save()

            
        elif 'non_code' in item:
            output_task.name = 'Данный товар с данным производителем и артикулом не найден'
            output_task.save()

            
        elif 'non_make' in item:
            output_task.name = 'Данный товар с данным производителем и артикулом не найден'
            output_task.save()

        else:
            output_task.name = item['name']            
            for i in range(item['count']):
                #Добавление данных о товаре в таблицу товара
                try:
                    offer = ParserFindItem.objects.get(offer_key=item['offers'][i]['offerKey'])
                    offer.rating = item['offers'][i]['rating2']['rating']
                    offer.quantity = item['offers'][i]['quantity']
                    offer.delivery = item['offers'][i]['delivery']['value']
                    offer.price = item['offers'][i]['displayPrice']['value']
                    offer.save()
                except ParserFindItem.DoesNotExist:
                    offer = ParserFindItem.objects.create(offer_key=item['offers'][i]['offerKey'])
                    offer.rating = item['offers'][i]['rating2']['rating']
                    offer.quantity = item['offers'][i]['quantity']
                    offer.delivery = item['offers'][i]['delivery']['value']
                    offer.price = item['offers'][i]['displayPrice']['value']
                    offer.save()
                #Добавление полученного товара в список товаров задания
                output_task.finds_list.add(ParserFindItem.objects.get(offer_key=offer.offer_key))
            output_task.save()
        if index_from == last_index:
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