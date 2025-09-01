from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthCheckView, api_root

router = DefaultRouter()

urlpatterns = [
    path('', api_root, name='api-root'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('v1/', include(router.urls)),
]