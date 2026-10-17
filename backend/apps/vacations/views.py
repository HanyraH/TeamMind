"""Views for Vacation management."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.users.permissions import IsProjectManagerOrAdmin
from .models import Vacation
from .serializers import VacationSerializer


class VacationViewSet(viewsets.ModelViewSet):
    serializer_class = VacationSerializer
    filterset_fields = ['employee', 'status', 'vacation_type']

    def get_queryset(self):
        user = self.request.user
        qs = Vacation.objects.select_related('employee__user', 'reviewed_by').all()
        # Employees can only see their own vacations
        if user.role == 'employee':
            if hasattr(user, 'employee_profile'):
                return qs.filter(employee=user.employee_profile)
            return qs.none()
        return qs

    def get_permissions(self):
        if self.action in ['approve_vacation', 'reject_vacation']:
            return [IsProjectManagerOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        # Auto-assign employee if role is employee
        if user.role == 'employee' and hasattr(user, 'employee_profile'):
            serializer.save(employee=user.employee_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_vacation(self, request, pk=None):
        vacation = self.get_object()
        vacation.status = Vacation.VacationStatus.APPROVED
        vacation.reviewed_by = request.user
        vacation.reviewed_at = timezone.now()
        vacation.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
        return Response(VacationSerializer(vacation).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_vacation(self, request, pk=None):
        vacation = self.get_object()
        vacation.status = Vacation.VacationStatus.REJECTED
        vacation.reviewed_by = request.user
        vacation.reviewed_at = timezone.now()
        vacation.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
        return Response(VacationSerializer(vacation).data)
