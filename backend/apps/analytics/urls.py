from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_stats, name='analytics_dashboard'),
    path('projects-without-team/', views.projects_without_team, name='analytics_no_team'),
]
