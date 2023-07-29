from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Proxy, SiteUser
from rest_framework import generics, permissions
from .serializers import ProxyListSerializer, SiteUserListSerializer


class ProxyListView(generics.ListCreateAPIView):
    serializer_class = ProxyListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        query = Proxy.objects.all()
        return query


class ProxyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProxyListSerializer
    lookup_field = 'id'
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        query = Proxy.objects.all()
        return query


class SiteUserView(generics.ListCreateAPIView):

    # permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SiteUserListSerializer


    def get_queryset(self):
        query = SiteUser.objects.all()
        return query
