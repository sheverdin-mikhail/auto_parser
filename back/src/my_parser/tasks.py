from config.celery import app

from django.db.models import Prefetch
import pandas as pd
import time
from src.my_parser.models import ParserTask, ParserOutputTask, ParserFindItem
from src.my_parser.serializers import ParserOutputTaskSerializer

@app.task
def export_to_file(pk):
    
    start_time = time.time()

    input_file_query = ParserTask.objects.filter(pk=pk).select_related('input_file').first()
    input_file = input_file_query.input_file.file

    excel_data = pd.read_excel(input_file)
    articles = excel_data['КодПроизводителя'].to_list()

    print(f'Файл прочитан за {time.time() - start_time}')

    start_time = time.time()
        #Получаем все значения артиклей из заданий
    output_tasks = ParserOutputTask.objects.filter(article__in=articles).prefetch_related(Prefetch('finds_list', queryset=ParserFindItem.objects.order_by('price'))).order_by('article', 'pk')
    serializer = ParserOutputTaskSerializer(output_tasks, many=True)

    print(f'Данный получены за {time.time() - start_time}')


    return serializer.data