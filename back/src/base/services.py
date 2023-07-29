import datetime


import pandas as pd
import requests
from django.conf import settings
import xlsxwriter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_path_upload_file(instance, file):
    '''Построение пути к файлу, format: (media)/input_files/file.xlsx'''

    date = datetime.datetime.now()
    date_str = date.strftime('%d%m%Y%s%M%h')
    return f'input_files/{date_str}_inputdata.xlsx'


def get_path_output_file():
    pass