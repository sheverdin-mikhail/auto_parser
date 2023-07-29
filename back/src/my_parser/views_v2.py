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
    ParserOutputTaskSerializer,
    ParserTasksFromArraySerializer,
    InputDataArraySerializer,
    ParserTasksFromArrayListSerializer
)
import time
from rest_framework.response import Response
from rest_framework import status

from .emex import tasks_v2 as emex_tasks_v2
from .autopiter import tasks_v2 as autopiter_tasks_v2
from .wildberries import tasks_v2 as wildberries_tasks_v2
from .autodoc import tasks_v2 as autodoc_tasks_v2

from .models import (
    ParserSite, 
    ParserTask, 
    ParserFindItem, 
    ParserTaskFromArray, 
    InputDataArray
)


class InputDataView(APIView):
    
    permission_classes = (permissions.IsAuthenticated,)
    
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
        # new_task_serializer = ParserTasksFromArraySerializer(data=task_data)
        new_task_serializer = ParserTasksFromArrayListSerializer(data=task_data)


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
            

class ParserTaskFromArrayView(generics.RetrieveDestroyAPIView):

    # serializer_class = ParserTasksFromArraySerializer
    serializer_class = ParserTasksFromArrayListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tasks = ParserTaskFromArray.objects.all()
        return tasks

    
class StartTask(generics.RetrieveUpdateAPIView):

    # serializer_class = ParserTasksFromArraySerializer
    serializer_class = ParserTasksFromArrayListSerializer
    # permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tasks = ParserTaskFromArray.objects.all()
        return tasks

    def patch(self, request, *args, **kwargs):
        
        task = ParserTaskFromArray.objects.get(id=kwargs['pk'])
        if "sites" in request.data:
            sites = ParserSite.objects.filter(id__in = request.data['sites'])
            task.sites.set(sites)
            task.save()

        if "marker" in request.data:
            sites = ParserSite.objects.filter(id__in = request.data['sites'])
            task.marker = request.data['marker']
            task.save()


        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if 'status' in request.data and request.data['status'] == 'run':
            for site in instance.sites.all():
                if site.name == 'autopiter' and site.status == True:
                    autopiter_tasks_v2.create_parser_task_from_array.apply_async(args=(instance.id, instance.marker), queue='parsing_queue')
                elif site.name == 'emex' and site.status == True:
                    emex_tasks_v2.create_parser_task_from_array.apply_async(args=(instance.id, instance.marker), queue='parsing_queue')
                elif site.name == 'wildberries' and site.status == True:
                    wildberries_tasks_v2.create_parser_task_from_array.apply_async(args=(instance.id, instance.marker), queue='parsing_queue')
                elif site.name == 'autodoc' and site.status == True:
                    autodoc_tasks_v2.create_parser_task_from_array.apply_async(args=(instance.id, instance.marker), queue='parsing_queue')

        return super().patch(request, *args, **kwargs)


class ParserTasksFromArrayListView(generics.ListAPIView):
    serializer_class = ParserTasksFromArrayListSerializer
    lookup_field = 'pk'
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tasks = ParserTaskFromArray.objects.all().order_by('pk')
        return tasks


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
            task = ParserTaskFromArray.objects.values('id', 'status', 'rows_count').get(pk=kwargs['pk'])
        except ParserTaskFromArray.DoesNotExist: 
            return Response({'status': 'error', 'message': "This task doesn't exists" }, status=status.HTTP_400_BAD_REQUEST)

        if '_start' in params:
            start = int(params.get('_start')[0])
        else:
            start = 0
            
        
        if task.get('status') == 'done':
            output_tasks = (
                InputDataArray.objects
                .filter(task_id=kwargs['pk'])
                .prefetch_related(Prefetch('finds_list', queryset=ParserFindItem.objects.order_by('price')))
                .order_by('article', '-pk')
                [start:start+limit]
            )

            serializer = ParserOutputTaskSerializer(output_tasks, many=True)
                            
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'pending', 'message': 'Parser process is not already done' }, status=status.HTTP_423_LOCKED)