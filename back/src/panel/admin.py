from django.contrib import admin

from .models import Proxy, SiteUser

admin.site.register(Proxy)
admin.site.register(SiteUser)
