"""Views for Employee, Department, and Skill management."""
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.users.permissions import IsAdminRole, IsProjectManagerOrAdmin, IsOwnerOrAdmin
from .models import Department, Position, Skill, Employee, EmployeeSkill, WorkPreference
from .serializers import (
    DepartmentSerializer, PositionSerializer, SkillSerializer,
    EmployeeListSerializer, EmployeeDetailSerializer, EmployeeCreateUpdateSerializer,
    EmployeeSkillSerializer, WorkPreferenceSerializer,
)
from .filters import EmployeeFilter


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRole()]
        return [IsAuthenticated()]


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.select_related('department').all()
    serializer_class = PositionSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRole()]
        return [IsAuthenticated()]


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    search_fields = ['name', 'category']
    pagination_class = None

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRole()]
        return [IsAuthenticated()]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related(
        'user', 'department', 'position'
    ).prefetch_related('skills__skill').all()
    filterset_class = EmployeeFilter
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['user__last_name', 'department__name', 'status']
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        return EmployeeDetailSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsOwnerOrAdmin()]
        if self.action == 'destroy':
            return [IsAdminRole()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get', 'post'], url_path='skills')
    def manage_skills(self, request, pk=None):
        employee = self.get_object()

        if request.method == 'GET':
            skills = employee.skills.select_related('skill').all()
            serializer = EmployeeSkillSerializer(skills, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            # Only admin or employee themselves
            if not (request.user.role == 'admin' or request.user.is_superuser or
                    (hasattr(request.user, 'employee_profile') and
                     request.user.employee_profile == employee)):
                return Response({'detail': 'Нет прав.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = EmployeeSkillSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(employee=employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['get', 'put', 'patch'], url_path='work-preferences')
    def work_preferences(self, request, pk=None):
        employee = self.get_object()
        pref, _ = WorkPreference.objects.get_or_create(employee=employee)

        if request.method == 'GET':
            return Response(WorkPreferenceSerializer(pref).data)

        # Only admin or the employee themselves can modify work preferences
        if not (request.user.role == 'admin' or request.user.is_superuser or
                (hasattr(request.user, 'employee_profile') and
                 request.user.employee_profile == employee)):
            return Response({'detail': 'Нет прав для изменения настроек данного сотрудника.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = WorkPreferenceSerializer(
            pref, data=request.data, partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='workload')
    def workload(self, request, pk=None):
        """Get current employee workload summary."""
        from apps.projects.models import TaskAssignment
        from django.db.models import Sum
        employee = self.get_object()
        assignments = TaskAssignment.objects.filter(
            employee=employee, task__project__status='active'
        ).select_related('task', 'task__project')

        data = []
        total_hours = 0
        for a in assignments:
            total_hours += a.allocated_hours or 0
            data.append({
                'project': a.task.project.name,
                'task': a.task.name,
                'allocated_hours': a.allocated_hours,
            })

        return Response({
            'employee_id': employee.id,
            'weekly_capacity': employee.weekly_hours,
            'allocated_hours': total_hours,
            'utilization_pct': round(total_hours / employee.weekly_hours * 100, 1) if employee.weekly_hours else 0,
            'assignments': data,
        })
