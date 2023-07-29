from rest_framework import serializers

from .models import Proxy, SiteUser


class ProxyListSerializer(serializers.ModelSerializer):
    """Список прокси"""

    class Meta:
        model = Proxy
        fields = "__all__"






class SiteUserListSerializer(serializers.ModelSerializer):
    """Список пользователей для парсинга"""

    class Meta:
        model = SiteUser
        fields = "__all__"

