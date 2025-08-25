from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import JobViewSet


router = DefaultRouter()
router.register(r'jobs',JobViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]