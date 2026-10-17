from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('departments', views.DepartmentViewSet, basename='department')
router.register('positions', views.PositionViewSet, basename='position')
router.register('skills', views.SkillViewSet, basename='skill')
router.register('', views.EmployeeViewSet, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
]
