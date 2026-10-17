"""REST API views for team generation and management."""
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.users.permissions import IsProjectManagerOrAdmin, IsAdminRole
from .models import Team, TeamRun, TeamMember
from .services import start_team_generation
from .serializers import TeamRunSerializer, TeamSerializer, TeamDetailSerializer


class TeamRunViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only view of team generation run statuses."""
    queryset = TeamRun.objects.select_related('project', 'initiated_by').all()
    serializer_class = TeamRunSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['project', 'status']

    @action(detail=False, methods=['post'], url_path='generate',
            permission_classes=[IsProjectManagerOrAdmin])
    def generate(self, request):
        """Start a new team generation run for a project."""
        project_id = request.data.get('project_id')
        try:
            team_size = int(request.data.get('team_size', 6))
            if team_size <= 0:
                team_size = 6
        except (ValueError, TypeError):
            team_size = 6

        if not project_id:
            return Response(
                {'project_id': 'Это поле обязательно.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        run_id = start_team_generation(
            project_id=project_id,
            initiated_by_id=request.user.id,
            team_size=team_size,
        )
        return Response(
            {'run_id': run_id, 'status': 'queued'},
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=True, methods=['get'], url_path='status')
    def run_status(self, request, pk=None):
        """Poll the status of a specific run."""
        run = self.get_object()
        serializer = TeamRunSerializer(run)
        return Response(serializer.data)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.select_related('project', 'run').prefetch_related(
        'members__employee__user'
    ).all()
    filterset_fields = ['project', 'approval_status', 'run']

    def get_serializer_class(self):
        if self.action == 'list':
            return TeamSerializer
        return TeamDetailSerializer

    def get_permissions(self):
        if self.action in ['approve', 'reject', 'add_member', 'remove_member']:
            return [IsProjectManagerOrAdmin()]
        if self.action == 'destroy':
            return [IsAdminRole()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a team variant as the official team."""
        team = self.get_object()
        team.approval_status = Team.ApprovalStatus.APPROVED
        team.approved_by = request.user
        team.approved_at = timezone.now()
        team.save(update_fields=['approval_status', 'approved_by', 'approved_at'])
        return Response(TeamDetailSerializer(team).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a team variant."""
        team = self.get_object()
        team.approval_status = Team.ApprovalStatus.REJECTED
        team.save(update_fields=['approval_status'])
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'], url_path='members/add')
    def add_member(self, request, pk=None):
        """Manually add a member to a team."""
        team = self.get_object()
        employee_id = request.data.get('employee_id')
        role = request.data.get('role_in_team', '')
        if not employee_id:
            return Response(
                {'employee_id': 'Обязательное поле.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        member, created = TeamMember.objects.get_or_create(
            team=team,
            employee_id=employee_id,
            defaults={'role_in_team': role}
        )
        if not created:
            return Response(
                {'detail': 'Сотрудник уже в команде.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'status': 'added', 'member_id': member.id})

    @action(detail=True, methods=['delete'], url_path='members/(?P<member_id>[^/.]+)/remove')
    def remove_member(self, request, pk=None, member_id=None):
        """Remove a member from a team."""
        team = self.get_object()
        member = get_object_or_404(TeamMember, team=team, pk=member_id)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
