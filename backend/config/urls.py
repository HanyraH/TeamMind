"""TeamMind URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.graphql.views import AuthenticatedGraphQLView
from apps.graphql.schema import schema


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'name': 'TeamMind AI Backend API',
        'status': 'online',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'employees': '/api/employees/',
            'projects': '/api/projects/',
            'teams': '/api/teams/',
            'vacations': '/api/vacations/',
            'analytics': '/api/analytics/',
            'graphql': '/graphql/',
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/employees/', include('apps.employees.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/teams/', include('apps.teams.urls')),
    path('api/vacations/', include('apps.vacations.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('graphql/', AuthenticatedGraphQLView.as_view(schema=schema)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
