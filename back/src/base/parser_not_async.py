import datetime

import pandas as pd
import requests
from django.conf import settings
import xlsxwriter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.mail import send_mail

from src.my_parser.models import ParserOutputTask, ParserFindItem



def get_data_from_file(file_name):
    print(f'чтение из файла {file_name}')
    excel_data = pd.read_excel(file_name, engine='openpyxl')

    result = []
    print(excel_data)
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

def collect_data(code, make):

    login = 'oRKGCm'
    password = 'QQboJk'
    proxies = {
        'https': f'http://{login}:{password}@176.53.141.185:8000'
    }
    url = f"https://emex.ru/api/search/search?make={str(make).lower().replace('-', '--').replace(' ', '-')}&detailNum={str(code)}&locationId=31980&longitude=37.6318&latitude=55.7583"
    # url = 'https://google.com'
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
        'Accept' : 'image/avif,image/webp,*/*'
    }
    print(f'{code}: {make}')
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
        response = session.get(
            url=url,
            headers=headers,
            verify=True,
            cert=('nginx/fullchain.pem', 'nginx/privkey.pem'),
            timeout=20,
            proxies=proxies
            )

        if 'originals' in response.json()['searchResult']:
            return response.json()['searchResult']['originals'][0]
        else:
            return {'not_find': response.json()['searchResult']['num'], 'make': response.json()['searchResult']['make']}


def create_output_from_data(data, start_date):
    output = []
    max_offers = 0
    for i in range(len(data)):
        if 'offers' in data[i]:
            if max_offers < data[i]['count']:
                max_offers = data[i]['count']
                
    for item in data:

        #Создание задания в бд
        output_task = ParserOutputTask.objects.create()
        output_task.site = 'emex.ru'
        output_task.start_date = datetime.datetime.now()
        #Создание строки для сохранения в excel
        if 'not_find' in item:
            output_task.article = item['not_find']
            output_task.name = 'Данный товар с данным производителем и артикулом не найден'
            output_task.brand = item['make']
            output_task.save()

            df = pd.DataFrame({
                'Сайт': ['emex.ru'],
                'Артикул': [item['not_find']],
                'Наименование': 'Данный товар с данным производителем и артикулом не найден',
                'Бренд': [item['make']],

            })
            for i in range(6):
                df.insert(
                    4 + i,
                    'Самое дешевое предложение' if i == 0 else f'№{i}',
                    [{
                        'Рейтинг': ' ',
                        'Наличие': ' ',
                        'Срок, дней': ' ',
                        'Цена, руб.': ' ',
                    }]
                )
        elif 'non_code' in item:
            output_task.article = item['non_code']
            output_task.name = 'Данный товар с данным производителем и артикулом не найден'
            output_task.brand = item['make']
            output_task.save()

            df = pd.DataFrame({
                'Сайт': ['emex.ru'],
                'Артикул': [item['non_code']],
                'Наименование': 'Данный товар с данным производителем и артикулом не найден',
                'Бренд': [item['make']],

            })
            for i in range(6):
                df.insert(
                    4 + i,
                    'Самое дешевое предложение' if i == 0 else f'№{i}',
                    [{
                        'Рейтинг': ' ',
                        'Наличие': ' ',
                        'Срок, дней': ' ',
                        'Цена, руб.': ' ',
                    }]
                )
        elif 'non_make' in item:
            output_task.article = item['code']
            output_task.name = 'Данный товар с данным производителем и артикулом не найден'
            output_task.brand = item['non_make']
            output_task.save()

            df = pd.DataFrame({
                'Сайт': ['emex.ru'],
                'Артикул': [item['code']],
                'Наименование': 'Данный товар с данным производителем и артикулом не найден',
                'Бренд': [item['non_make']],

            })
            for i in range(6):
                df.insert(
                    4 + i,
                    'Самое дешевое предложение' if i == 0 else f'№{i}',
                    [{
                        'Рейтинг': ' ',
                        'Наличие': ' ',
                        'Срок, дней': ' ',
                        'Цена, руб.': ' ',
                    }]
                )
        else:
            output_task.article = item['detailNum']
            output_task.name = item['name']
            output_task.brand = item['make']
            df = pd.DataFrame({
                'Сайт': ['emex.ru'],
                'Артикул': [item['detailNum']],
                'Наименование': [item['name']],
                'Бренд': [item['make']],

            })
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

                # Создание строк товаров для добавления в excel
                df.insert(
                    4 + i,
                    'Самое дешевое предложение' if i == 0 else f'№{i}',
                    [{
                        'Рейтинг': item['offers'][i]['rating2']['rating'],
                        'Наличие': item['offers'][i]['quantity'],
                        'Срок, дней': f"{item['offers'][i]['delivery']['value']}",
                        'Цена, руб.': f"{item['offers'][i]['displayPrice']['value']}"
                    }]
                )
            output_task.save()
        output.append(df)
    return output, max_offers


def save_to_excel_file(output, max_offers, id):
    t_date = datetime.datetime.now().strftime('%d%m%Y%s%M%h')

    wb = xlsxwriter.Workbook(f'media/output_files/{t_date}_outputfile.xlsx')
    worksheet = wb.add_worksheet()
    headers = ['ID', 'Сайт', 'Артикул', 'Наименование', 'Брэнд']
    merged_headers = ['Самое дешевое предложение']
    for i in range(1, max_offers+1):
        merged_headers.append(f'№{i}')
    properties = ['Рейтинг', 'Наличие', 'Срок, дней', 'Цена, руб.']
    align_center_format = wb.add_format({
        'align': 'center',
        'valign': 'vcenter',
    })
    # Отрисовка обычных ячеек заголовков
    for col, head in enumerate(headers):
        worksheet.merge_range(0, col, 1, col, head, align_center_format)

    iteration = 0
    # Отрисовка объедененных ячеек предложений
    for col in range(5, len(merged_headers) * 4 + 1, 4):
        worksheet.merge_range(0, col, 0, col + 3, merged_headers[iteration], align_center_format)
        iteration += 1
        # Отрисовка ячеек с полями предложений
        for col2, prop in enumerate(properties):
            worksheet.write(1, col2 + col, prop, align_center_format)

    for row, item in enumerate(output):
        worksheet.write(row + 2, 0, row, align_center_format)
        worksheet.write(row + 2, 1, item['Сайт'][0], align_center_format)
        worksheet.write(row + 2, 2, item['Артикул'][0], align_center_format)
        worksheet.write(row + 2, 3, item['Наименование'][0], align_center_format)
        worksheet.write(row + 2, 4, item['Бренд'][0], align_center_format)
        # Самое дешевое предложение
        if 'Самое дешевое предложение' in item:
            worksheet.write(row + 2, 5, item['Самое дешевое предложение'][0]['Рейтинг'], align_center_format)
            worksheet.write(row + 2, 6, item['Самое дешевое предложение'][0]['Наличие'], align_center_format)
            worksheet.write(row + 2, 7, item['Самое дешевое предложение'][0]['Срок, дней'], align_center_format)
            worksheet.write(row + 2, 8, item['Самое дешевое предложение'][0]['Цена, руб.'], align_center_format)
        for i in range(max_offers+1):
            if f'№{i}' in item:
                worksheet.write(row + 2, 5+4*i, item[f'№{i}'][0]['Рейтинг'], align_center_format)
                worksheet.write(row + 2, 6+4*i, item[f'№{i}'][0]['Наличие'], align_center_format)
                worksheet.write(row + 2, 7+4*i, item[f'№{i}'][0]['Срок, дней'], align_center_format)
                worksheet.write(row + 2, 8+4*i, item[f'№{i}'][0]['Цена, руб.'], align_center_format)
            
    wb.close()
    from src.my_parser.models import ParserTask
    from django.contrib.auth.models import User
    task = ParserTask.objects.get(id=id)
    task.output_file = f'output_files/{t_date}_outputfile.xlsx'
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
