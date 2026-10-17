"""URL routes for authentication and user management."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.me, name='user_me'),
    path('me/update/', views.update_profile, name='user_update_profile'),
    path('me/change-password/', views.change_password, name='user_change_password'),
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
