from config.celery import app
import pandas as pd


from .utils import get_data, save_data

@app.task
def parse_data(code, make, name, row, id, marker, last_item=False):
    data = get_data(code, make, name)
    print(f'{code} {make} {name}')
    save_data(data, row, id, marker, last_item)



@app.task
def create_parser_task(file_name, id, marker):
    data = pd.read_excel(file_name)
    input_data = []
    for index, item in enumerate(data.values):
        if(len(data.columns)>3):
            row = {
                'code': item[2] if str(item[2]) != 'nan' else None,
                'name': item[3] if str(item[3]) != 'nan' else None,
                'make': item[4] if str(item[4]) != 'nan' else None,
            }

        else:
            row = {
                'code': item[0] if str(item[0]) != 'nan' else None,
                'name': item[1] if str(item[1]) != 'nan' else None,
                'make': item[2] if str(item[2]) != 'nan' else None,
            }
        if(index==len(data.values)-1):
            last_item = True
        else:
            last_item = False

        input_data.append({
            'code': row['code'],
            'make': row['make'],
            'name': row['name'],
            'item': item.tolist(),
            'id': id,
            'marker':marker,
            'last_item': last_item,
        })
        # parse_data.apply_async((code, make, item.tolist(), id, last_item))
    parse_data.chunks(
        ((item['code'], item['make'], item['name'], item['item'], item['id'], item['marker'], item['last_item']) for item in input_data), 
        n=100
    ).apply_async()