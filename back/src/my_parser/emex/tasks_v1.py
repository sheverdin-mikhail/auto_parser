from datetime import datetime
import json
from config.celery import app
import pandas as pd
import asyncio


from src.base.parser import create_output_from_data, gather_data


@app.task
def parse_data(input_data):
    # instance, start_date, task, from_index

    columns = input_data['columns']
    id = input_data['id']
    start_date = input_data['start_date']
    task = input_data['task_data']
    from_index = input_data['task_index']
    last_index = input_data['last_index']
    data = asyncio.run(gather_data(task, columns))
    create_output_from_data(data, start_date, task, columns, id,from_index,last_index)


@app.task
def create_parser_task(file_name, id):
    data = pd.read_excel(file_name)
    start_date = datetime.now()
    tasks = {}
    if(len(data.values)>100):
        i=0
        n=1 #номер массива
        last_index = 0
        while(True):
            try:
                if i%100 == 0:
                    task = data.values[i:i+100]
                    tasks[i] = task
                    last_index = i
                    i += 1
                    n+1
                else:
                    i += 1
                data.values[i]
            except IndexError:
                task = data.values[last_index+1:]
                tasks[last_index+1] = task
                break
        for el in tasks:
            input_data = {
                'id': id,
                'columns': len(data.columns),
                'start_date': start_date.strftime('%d%m%Y%s%M%h'),
                'task_data': tasks[el].tolist(),
                'task_index': el,
                'last_index': list(tasks.keys())[-1]
                }
            parse_data.delay(input_data)
    else:
        tasks[0] = data.values
        input_data = {'id': id, 'columns': len(data.columns), 'start_date': start_date.strftime('%d%m%Y%s%M%h'), 'task_data': tasks[0].tolist(), 'task_index': 0, 'last_index': 0}
        parse_data.delay(input_data)