from datetime import datetime
import xlsxwriter
from django.db.models import Prefetch
import pandas as pd
from io import BytesIO
from django.http import FileResponse
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import (
    ParserSitesSerializer, 
    ParserTasksSerializer, 
    InputFileSerializer, 
    ParserTaskSitesSerializer, 
    ParserStartTaskSerializer, 
    ParserTaskMarkerSerializer,
    ParserOutputTaskSerializer,
    ParserTasksFromArraySerializer,
    InputDataArraySerializer,
    ParserTasksFromArrayListSerializer
)
import time
from rest_framework.response import Response
from rest_framework import status

from .emex import tasks as emex_tasks
from .emex import tasks_v2 as emex_tasks_v2
from .autopiter import tasks as autopiter_tasks
from .autopiter import tasks_v2 as autopiter_tasks_v2
from .wildberries import tasks as wildberries_tasks
from .wildberries import tasks_v2 as wildberries_tasks_v2
from .autodoc import tasks as autodoc_tasks
from .autodoc import tasks_v1 as autodoc_tasks_v2

from .models import (
    ParserInputFile, 
    ParserSite, 
    ParserTask, 
    ParserOutputTask, 
    ParserFindItem, 
    ParserTaskFromArray, 
    InputDataArray
)

from .tasks import export_to_file

class InputFilesView(generics.ListCreateAPIView):
    serializer_class = InputFileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        files = ParserInputFile.objects.all()
        return files
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)     
        data = pd.read_excel(serializer.data['file'])
        input_file=ParserInputFile.objects.get(id=serializer.data['id'])
        rows_count = len(data)
        task = ParserTask.objects.create(rows_count=rows_count, input_file=input_file)
        task.save() 
        task_serializer = ParserStartTaskSerializer(task)

        return Response({ 'task': task_serializer.data }, status=status.HTTP_201_CREATED)

class InputDataView(APIView):
    
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, *args, **kwargs):

        data = self.request.data

        if 'data' not in data: 
            return Response({'error': 'data is required'}, status=status.HTTP_400_BAD_REQUEST)
        if 'sites' not in data: 
            return Response({'error': 'sites is required'}, status=status.HTTP_400_BAD_REQUEST)
        if 'marker' not in data: 
            return Response({'error': 'marker is required'}, status=status.HTTP_400_BAD_REQUEST)

        input_data = data['data']
        sites = data['sites']
        marker = data['marker']

        sites_query = ParserSite.objects.filter(name__in=sites, status=True)

        task_data = {
            'marker': marker,
            'rows_count': len(input_data),
        }
        new_task_serializer = ParserTasksFromArraySerializer(data=task_data)


        if(new_task_serializer.is_valid(False)):
            new_task = new_task_serializer.save()
            for item in input_data:
                item['task_id'] = new_task.id
                item['task_marker'] = f'{new_task.id}-{marker}'

            input_data_serialize = InputDataArraySerializer(data=input_data, many=True)

            if(input_data_serialize.is_valid(False)):
                
                input_data = input_data_serialize.save()

                new_task.input_data.set(input_data)
                new_task.sites.set(sites_query)
                new_task.save()
                return Response({'create': 'Task create is success', 'task': new_task_serializer.data}, status=status.HTTP_201_CREATED)


        return Response({'error': 'Data is not valid'}, status=status.HTTP_400_BAD_REQUEST)
            

class ParserTaskFromArrayView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ParserTasksFromArraySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tasks = ParserTaskFromArray.objects.all()
        return tasks

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.data

        if 'status' in request.data and request.data['status'] == 'run':
            for site in instance['sites']:
                if site['name'] == 'autopiter' and site['status'] == True:
                    autopiter_tasks_v2.create_parser_task_from_array.delay(instance['input_data'], instance['id'], instance['marker'])
                elif site['name'] == 'emex' and site['status'] == True:
                    emex_tasks_v2.create_parser_task_from_array.delay(instance['input_data'], instance['id'], instance['marker'])
                elif site['name'] == 'wildberries' and site['status'] == True:
                    wildberries_tasks_v2.create_parser_task_from_array.delay(instance['input_data'], instance['id'], instance['marker'])
                elif site['name'] == 'autodoc' and site['status'] == True:
                    autodoc_tasks_v2.create_parser_task_from_array.delay(instance['input_data'], instance['id'], instance['marker'])

        return super().update(request)



class ParserSiteView(generics.ListAPIView):
    serializer_class = ParserSitesSerializer

    def get_queryset(self):
        query = ParserSite.objects.filter(status=True)
        return query


class ChangeTaskSitesView(generics.UpdateAPIView):
    serializer_class = ParserTaskSitesSerializer
    queryset = ParserTask.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

class ChangeTaskMarkerView(generics.UpdateAPIView):
    serializer_class = ParserTaskMarkerSerializer
    queryset = ParserTask.objects.all()
    permission_classes = (permissions.IsAuthenticated,)



class ParserTaskView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ParserStartTaskSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tasks = ParserTask.objects.all()
        return tasks

     #Запуск таски селери 
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.data
        file_name = instance['input_file']['file']
        for site in instance['sites']:
            if site['name'] == 'autopiter':
                autopiter_tasks.create_parser_task.apply_async(args=(file_name, instance['id'], instance['marker']), queue='parsing_queue')
            elif site['name'] == 'emex':
                emex_tasks.create_parser_task.apply_async(args=(file_name, instance['id'], instance['marker']), queue='parsing_queue')
            elif site['name'] == 'wildberries':
                wildberries_tasks.create_parser_task.apply_async(args=(file_name, instance['id'], instance['marker']), queue='parsing_queue')
            elif site['name'] == 'autodoc':
                autodoc_tasks.create_parser_task.apply_async(args=(file_name, instance['id'], instance['marker']), queue='parsing_queue')

        return super().update(request)


class ParserTasksListView(generics.ListAPIView):
    serializer_class = ParserTasksSerializer
    lookup_field = 'pk'
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tasks = ParserTask.objects.all().order_by('pk')
        return tasks
    
class ParserTasksFromArrayListView(generics.ListAPIView):
    serializer_class = ParserTasksFromArrayListSerializer
    lookup_field = 'pk'
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tasks = ParserTaskFromArray.objects.all().order_by('pk')
        return tasks


class ParserResultDownLoad(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    
    def get(self, request, *args, **kwargs):

        t_date = datetime.now()

        start = time.time()

        input_file_query = ParserTask.objects.filter(pk=kwargs['pk']).select_related('input_file').first()
        input_file = input_file_query.input_file.file

        excel_data = pd.read_excel(input_file)
        articles = excel_data['КодПроизводителя'].to_list()


            #Получаем все значения артиклей из заданий
        output_tasks = ParserOutputTask.objects.filter(article__in=articles).prefetch_related(Prefetch('finds_list', queryset=ParserFindItem.objects.order_by('price'))).order_by('article', '-pk')


        max_offers = 254


         # create a response
        output = BytesIO()

        wb =  xlsxwriter.Workbook(output)
        worksheet = wb.get_worksheet_by_name("Sheet1")

        headers = ['ID', 'Город', "Склад", 'Артикул', 'Наименование', 'Брэнд', "Свободный остаток", "Цена прихода", "Остаток холдинга", "Расход холдинга", "Можно реализовать"]
        merged_headers = ['Самое дешевое предложение']
        for i in range(1, max_offers + 1):
            merged_headers.append(f'№{i}')
        properties = ['Рейтинг', 'Наличие', 'Срок, дней', 'Цена, руб.']
        align_center_format = wb.add_format({
            'align': 'center',
            'valign': 'vcenter',
        })


        worksheet = wb.add_worksheet()
        # Отрисовка обычных ячеек заголовков
        for col, head in enumerate(headers):
            worksheet.merge_range(0, col, 1, col, head, align_center_format)

        iteration = 0
        # Отрисовка объедененных ячеек предложений
        for col in range(11, len(merged_headers) * 4 + 1, 4):
            worksheet.merge_range(0, col, 0, col + 3, merged_headers[iteration], align_center_format)
            iteration += 1
            # Отрисовка ячеек с полями предложений
            for col2, prop in enumerate(properties):
                worksheet.write(1, col2 + col, prop, align_center_format)

        print(f'Инициализация закончена за: { time.time() - start }')

        #Отрисовка выходных данных          
 
        prev_article = None
        result = list(output_tasks)

        start = time.time()
        row = 0
        for item in result:
            if prev_article:
                if item.article == prev_article:
                    continue
            prev_article = item.article
            worksheet.write(row + 2, 0, row, align_center_format)
            worksheet.write(row + 2, 1, item.city, align_center_format)
            worksheet.write(row + 2, 2, item.stock, align_center_format)
            worksheet.write(row + 2, 3, item.article, align_center_format)
            worksheet.write(row + 2, 4, item.name, align_center_format)
            worksheet.write(row + 2, 5, item.brand, align_center_format)
            worksheet.write(row + 2, 6, item.free_balance, align_center_format)
            worksheet.write(row + 2, 7, item.arrival_price, align_center_format)
            worksheet.write(row + 2, 8, item.holding_balance, align_center_format)
            worksheet.write(row + 2, 9, item.holding_expense, align_center_format)
            worksheet.write(row + 2, 10, item.implemented, align_center_format)
            if(item.finds_list.all()):
                # Самое дешевое предложение
                worksheet.write(row + 2, 11, item.finds_list.all()[0].rating, align_center_format)
                worksheet.write(row + 2, 12, item.finds_list.all()[0].quantity, align_center_format)
                worksheet.write(row + 2, 13, item.finds_list.all()[0].delivery, align_center_format)
                worksheet.write(row + 2, 14, item.finds_list.all()[0].price, align_center_format)
                for i in range(len(item.finds_list.all())):
                        worksheet.write(row + 2, 15+4*i, item.finds_list.all()[i].rating, align_center_format)
                        worksheet.write(row + 2, 16+4*i, item.finds_list.all()[i].quantity, align_center_format)
                        worksheet.write(row + 2, 17+4*i, item.finds_list.all()[i].delivery, align_center_format)
                        worksheet.write(row + 2, 18+4*i, item.finds_list.all()[i].price, align_center_format)
            row += 1
        wb.close()

        output.seek(0)

        print(f'Запись в файл закончена за: { time.time() - start }')

        # return the response
        return FileResponse(output, as_attachment=True, filename=f'output_{t_date}.xlsx')


class GetParserResultView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    

    def get(self, request, *args, **kwargs):

        params = dict(request.query_params)
        
        if '_limit' in params:
            if int(params.get('_limit')[0]) < 500:
                limit = int(params.get('_limit')[0])
            else:
                return Response({'status': 'error', 'message': "Too mutch _limit param" }, status=status.HTTP_400_BAD_REQUEST)
        else:
            limit = 500


        try:
            task = ParserTask.objects.get(pk=kwargs['pk'])
        except ParserTask.DoesNotExist: 
            return Response({'status': 'error', 'message': "This task doesn't exists" }, status=status.HTTP_400_BAD_REQUEST)
            
        
        if task.status == 'done':
            output_tasks = (
                ParserOutputTask.objects
                .filter(task_id=kwargs['pk'])
                .prefetch_related(Prefetch('finds_list', queryset=ParserFindItem.objects.order_by('price')))
                .order_by('article', '-pk')
            )

            serializer = ParserOutputTaskSerializer(output_tasks, many=True)


            if '_start' in params:
                start = int(params.get('_start')[0])
            else:
                state = False
                return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


            if start and start > len(serializer.data):
                return Response({'status': 'error', 'message': "_start param more then size array" }, status=status.HTTP_400_BAD_REQUEST)
            elif limit > len(serializer.data):
                result = serializer.data[start:]
            else:
                result = serializer.data[start:start+limit]
                
            return Response({'status': 'success', 'data': result}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'pending', 'message': 'Parser process is not already done' }, status=status.HTTP_423_LOCKED)




class GetParserResulFromArraytView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    

    def get(self, request, *args, **kwargs):

        params = dict(request.query_params)
        
        if '_limit' in params:
            if int(params.get('_limit')[0]) < 500:
                limit = int(params.get('_limit')[0])
            else:
                return Response({'status': 'error', 'message': "Too mutch _limit param" }, status=status.HTTP_400_BAD_REQUEST)
        else:
            limit = 500


        try:
            task = ParserTaskFromArray.objects.get(pk=kwargs['pk'])
        except ParserTaskFromArray.DoesNotExist: 
            return Response({'status': 'error', 'message': "This task doesn't exists" }, status=status.HTTP_400_BAD_REQUEST)
            
        
        if task.status == 'done':
            output_tasks = (
                InputDataArray.objects
                .filter(task_id=kwargs['pk'])
                .prefetch_related(Prefetch('finds_list', queryset=ParserFindItem.objects.order_by('price')))
                .order_by('article', '-pk')
            )

            serializer = ParserOutputTaskSerializer(output_tasks, many=True)


            if '_start' in params:
                start = int(params.get('_start')[0])
            else:
                state = False
                return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


            if start and start > len(serializer.data):
                return Response({'status': 'error', 'message': "_start param more then size array" }, status=status.HTTP_400_BAD_REQUEST)
            elif limit > len(serializer.data):
                result = serializer.data[start:]
            else:
                result = serializer.data[start:start+limit]
                
            return Response({'status': 'success', 'data': result}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'pending', 'message': 'Parser process is not already done' }, status=status.HTTP_423_LOCKED)