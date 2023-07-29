from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)

urlpatterns = [
    path('api/admin-panel-for-parser/', admin.site.urls),
    path('api/api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/token/verify/', TokenVerifyView.as_view()),
    path('api/v1/', include('src.panel.urls')),
    path('api/v1/', include('src.my_parser.urls')),
    path('api/v2/', include('src.my_parser.urls_v2')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)