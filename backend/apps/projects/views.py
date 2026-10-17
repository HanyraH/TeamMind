"""Views for Project and Task management."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsProjectManagerOrAdmin, IsAdminRole
from .models import Project, Task, TaskAssignment, ProjectSkillRequirement
from .serializers import (
    ProjectListSerializer, ProjectDetailSerializer,
    TaskSerializer, TaskAssignmentSerializer,
    ProjectSkillRequirementSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('manager').prefetch_related(
        'skill_requirements__skill'
    ).all()
    filterset_fields = ['status', 'priority', 'manager']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'end_date', 'priority', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsProjectManagerOrAdmin()]
        if self.action == 'destroy':
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    @action(detail=True, methods=['get', 'post'], url_path='skill-requirements')
    def skill_requirements(self, request, pk=None):
        project = self.get_object()
        if request.method == 'GET':
            reqs = project.skill_requirements.select_related('skill').all()
            return Response(ProjectSkillRequirementSerializer(reqs, many=True).data)
        if request.method == 'POST':
            if not (request.user.role in ['admin', 'project_manager'] or request.user.is_superuser):
                return Response({'detail': 'Нет прав для добавления требований.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = ProjectSkillRequirementSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('project').prefetch_related('required_skills').all()
    serializer_class = TaskSerializer
    filterset_fields = ['project', 'status']
    permission_classes = [IsAuthenticated]


class TaskAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TaskAssignment.objects.select_related(
        'task__project', 'employee__user'
    ).all()
    serializer_class = TaskAssignmentSerializer
    filterset_fields = ['task', 'employee', 'task__project']
    permission_classes = [IsAuthenticated]
