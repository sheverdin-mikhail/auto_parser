
from django.urls import path

from . import views_v2

urlpatterns = [
    path('parser_task/<int:pk>/', views_v2.ParserTaskFromArrayView.as_view()),
    path('start_task/<int:pk>/', views_v2.StartTask.as_view()),
    path('input_data/', views_v2.InputDataView.as_view()),
    path('get_result/<int:pk>/', views_v2.GetParserResulFromArraytView.as_view()),
    path('parser_task_list/', views_v2.ParserTasksFromArrayListView.as_view()),

]
