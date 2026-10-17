"""Views for authentication and user management."""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdminRole


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get current authenticated user profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update current user profile."""
    serializer = UserSerializer(
        request.user,
        data=request.data,
        partial=request.method == 'PATCH'
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change current user password."""
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    if not user.check_password(serializer.validated_data['old_password']):
        return Response(
            {'old_password': 'Неверный текущий пароль.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    return Response({'detail': 'Пароль успешно изменён.'})


class UserListCreateView(generics.ListCreateAPIView):
    """Admin-only: list and create users."""
    queryset = User.objects.all().order_by('last_name')
    permission_classes = [IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin-only: retrieve, update, or delete a user."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
