
from django.urls import path

from . import views

urlpatterns = [
    path('parser_task/<int:pk>/', views.ParserTaskView.as_view()),
    path('change_sites/<int:pk>/', views.ChangeTaskSitesView.as_view()),
    path('change_marker/<int:pk>/', views.ChangeTaskMarkerView.as_view()),
    path('parser_task_list/', views.ParserTasksListView.as_view()),
    path('parser_sites_list/', views.ParserSiteView.as_view()),
    path('input_files/', views.InputFilesView.as_view()),
    path('download/<int:pk>/', views.ParserResultDownLoad.as_view()),
    path('get_result/<int:pk>/', views.GetParserResultView.as_view()),
]
