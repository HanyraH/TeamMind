from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('tasks', views.TaskViewSet, basename='task')
router.register('assignments', views.TaskAssignmentViewSet, basename='assignment')
router.register('', views.ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
]
