from config.celery import app
import pandas as pd


from .utils import get_data, save_data

@app.task
def parse_data(code, make, row, id, last_item=False):
    data = get_data(code, make)
    print(f'{code}: {make}')
    save_data(data, row, id, last_item)



@app.task
def create_parser_task(file_name, id):
    data = pd.read_excel(file_name)
    input_data = []
    for index, item in enumerate(data.values):
        if(len(data.columns)>3):
            if str(item[2]) != 'nan' and str(item[4]) != 'nan':
                if item[4] == 'Китай':
                    code = item[2]
                    make = 'unknownbrand'
                else:
                    code = item[2]
                    make = item[4]

            elif str(item[2]) == 'nan':
                code = 'none_code'
                make = item[4]

            elif str(item[4]) == 'nan':
                code = item[2]
                make = 'none_make'

        else:
            if str(item[0]) != 'nan' and str(item[2]) != 'nan':
                if item[2] == 'Китай':
                    code = item[0]
                    make = 'unknownbrand'
                else:
                    code = item[0]
                    make = item[2]

            elif str(item[2]) == 'nan':
                code = 'none_code'
                make = item[2]

            elif str(item[4]) == 'nan':
                code = item[0]
                make = 'none_make'
        if(index==len(data.values)-1):
            last_item = True
        else:
            last_item = False

        input_data.append({
            'code': code,
            'make': make,
            'item': item.tolist(),
            'id': id,
            'last_item': last_item,
        })
        # parse_data.apply_async((code, make, item.tolist(), id, last_item))
    parse_data.chunks(
        ((item['code'], item['make'], item['item'], item['id'], item['last_item']) for item in input_data), 
        n=100
    ).apply_async()