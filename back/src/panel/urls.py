
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('proxies/', views.ProxyListView.as_view()),
    path('proxy/<int:id>', views.ProxyView.as_view()),
    path('site_users/', views.SiteUserView.as_view()),
]
