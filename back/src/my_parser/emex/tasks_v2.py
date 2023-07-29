from config.celery import app
import pandas as pd

from .utils_v2 import get_data, save_data

@app.task
def parse_data(code, make, item, id, marker, last_item=False):
    data = get_data(code, make)
    print(f'{code}: {make}')
    save_data(data, item, id, marker, last_item)


@app.task
def create_parser_task_from_array(id, marker):

    from ..serializers import ParserTasksFromArraySerializer
    from ..models import ParserTaskFromArray

    task = ParserTaskFromArray.objects.get(id=id)

    serializer = ParserTasksFromArraySerializer(task)
    data = serializer.data['input_data']

    input_data = []
    for index, item in enumerate(data):
      
        if(index==len(data)-1):
            last_item = True
        else:
            last_item = False

        input_data.append({
            'code': item['article'],
            'make': item['brand'],
            'item': item,
            'id': id,
            'marker': marker,
            'last_item': last_item,
        })
    parse_data.chunks(
        ((item['code'], item['make'], item['item'], item['id'], marker, item['last_item']) for item in input_data), 
        n=100
    ).apply_async(priority=10, queue='parsing_queue')


