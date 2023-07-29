from rest_framework import serializers
import pandas as pd

from .models import ParserInputFile, ParserSite, ParserTask, ParserOutputTask, ParserFindItem, ParserTaskFromArray, InputDataArray
from src.my_parser.emex.tasks import parse_data


class InputFileSerializer(serializers.ModelSerializer):
    """Файл с входящими данными парсера"""

    class Meta:
        model = ParserInputFile
        fields = "__all__"




class ParserSitesSerializer(serializers.ModelSerializer):
    """ Сайты для парсинга """

    class Meta:
        model = ParserSite
        fields = "__all__"


class ParserTasksSerializer(serializers.ModelSerializer):
    """ Задания для парсера """

    input_file = InputFileSerializer(read_only=True, many=False)
    

    class Meta:
        model = ParserTask
        fields = "__all__"

        
class ParserStartTaskSerializer(serializers.ModelSerializer):
    """ Задания для парсера """

    input_file = InputFileSerializer(read_only=True, many=False)
    sites = ParserSitesSerializer(read_only=True, many=True)

    class Meta:
        model = ParserTask
        fields = "__all__"
        # exclude = ['sites']

class ParserTaskSitesSerializer(serializers.ModelSerializer):
    """ Сайты для парсера """

    class Meta:
        model = ParserTask
        fields = ('sites',)

class ParserTaskMarkerSerializer(serializers.ModelSerializer):
    """ Сайты для парсера """

    class Meta:
        model = ParserTask
        fields = ('marker',)


# class ParserFindItemSerializer(serializers.ModelSerializer):

#     class Meta: 
#         model = ParserFindItem
#         fields = "__all__"

# class ParserOutputTaskSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = ParserOutputTask
#         fields = "__all__"
#         # exclude = ('finds_list', )
#     finds_list = ParserFindItemSerializer(read_only=True, many=True)




class ParserFindItemSerializer(serializers.Serializer):

    rating = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    delivery = serializers.IntegerField(read_only=True)
    price = serializers.IntegerField(read_only=True)


class ParserOutputTaskSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    city = serializers.CharField(read_only=True)
    stock = serializers.CharField(read_only=True)
    site = serializers.CharField(read_only=True)
    article = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    brand = serializers.CharField(read_only=True)
    free_balance = serializers.CharField(read_only=True)
    arrival_price = serializers.CharField(read_only=True)
    holding_balance = serializers.CharField(read_only=True)
    holding_expense = serializers.CharField(read_only=True)
    implemented = serializers.CharField(read_only=True)
    finds_list = ParserFindItemSerializer(read_only=True, many=True)


class InputDataArraySerializer(serializers.ModelSerializer):
    """ Входные данные в виде массива """

    class Meta:
        model = InputDataArray
        fields = "__all__"


class ParserTasksFromArraySerializer(serializers.ModelSerializer):
    """ Задания для парсера из массива данных """

    input_data = InputDataArraySerializer(many=True, read_only=True)
    sites = ParserSitesSerializer(read_only=True, many=True)

    class Meta:
        model = ParserTaskFromArray
        fields = "__all__"


class ParserTasksFromArrayListSerializer(serializers.ModelSerializer):
    """ Задания для парсера из массива данных """

    sites = ParserSitesSerializer(read_only=True, many=True)

    class Meta:
        model = ParserTaskFromArray
        exclude = ('input_data', )
