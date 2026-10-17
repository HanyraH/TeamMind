from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('runs', views.TeamRunViewSet, basename='teamrun')
router.register('', views.TeamViewSet, basename='team')

urlpatterns = [
    path('', include(router.urls)),
]
