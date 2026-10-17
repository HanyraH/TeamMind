"""Strawberry GraphQL Schema for TeamMind."""
import strawberry
from strawberry.types import Info
from typing import Optional
import datetime


@strawberry.type
class EmployeeType:
    id: int
    full_name: str
    department: str
    status: str
    chronotype: str
    weekly_hours: int


@strawberry.type
class ProjectType:
    id: int
    name: str
    status: str
    priority: str
    start_date: datetime.date
    end_date: datetime.date
    planned_hours: int


@strawberry.type
class TeamVariantType:
    id: int
    variant_name: str
    total_score: float
    skill_coverage_pct: float
    approval_status: str


@strawberry.type
class DashboardMetrics:
    total_employees: int
    active_employees: int
    total_projects: int
    active_projects: int
    pending_vacations: int
    avg_workload_pct: float


@strawberry.type
class DepartmentWorkload:
    department: str
    employee_count: int
    avg_utilization_pct: float


@strawberry.type
class Query:
    @strawberry.field
    def dashboard_metrics(self, info: Info) -> DashboardMetrics:
        from apps.employees.models import Employee
        from apps.projects.models import Project
        from apps.vacations.models import Vacation
        from apps.projects.models import TaskAssignment
        from django.db.models import Sum, Avg

        total_emp = Employee.objects.count()
        active_emp = Employee.objects.filter(status='active').count()
        total_proj = Project.objects.count()
        active_proj = Project.objects.filter(status='active').count()
        pending_vac = Vacation.objects.filter(status='pending').count()

        # Avg workload
        alloc = TaskAssignment.objects.filter(
            task__project__status='active'
        ).values('employee').annotate(total=Sum('allocated_hours'))
        if alloc and active_emp > 0:
            total_alloc = sum(a['total'] for a in alloc if a['total'])
            from apps.employees.models import Employee as Emp
            employees = Emp.objects.filter(status='active').values_list('weekly_hours', flat=True)
            total_cap = sum(employees)
            avg_wl = (total_alloc / total_cap * 100) if total_cap else 0
        else:
            avg_wl = 0.0

        return DashboardMetrics(
            total_employees=total_emp,
            active_employees=active_emp,
            total_projects=total_proj,
            active_projects=active_proj,
            pending_vacations=pending_vac,
            avg_workload_pct=round(avg_wl, 1),
        )

    @strawberry.field
    def department_workloads(self, info: Info) -> list[DepartmentWorkload]:
        from apps.employees.models import Department, Employee
        from apps.projects.models import TaskAssignment
        from django.db.models import Sum

        results = []
        for dept in Department.objects.all():
            employees = Employee.objects.filter(department=dept, status='active')
            count = employees.count()
            if count == 0:
                continue
            total_cap = sum(e.weekly_hours for e in employees)
            emp_ids = list(employees.values_list('id', flat=True))
            alloc = TaskAssignment.objects.filter(
                employee_id__in=emp_ids,
                task__project__status='active'
            ).aggregate(total=Sum('allocated_hours'))
            total_alloc = alloc['total'] or 0
            util_pct = (total_alloc / total_cap * 100) if total_cap else 0
            results.append(DepartmentWorkload(
                department=dept.name,
                employee_count=count,
                avg_utilization_pct=round(util_pct, 1),
            ))
        return results

    @strawberry.field
    def project_teams(
        self, info: Info, project_id: int
    ) -> list[TeamVariantType]:
        from apps.teams.models import Team
        teams = Team.objects.filter(project_id=project_id)
        return [
            TeamVariantType(
                id=t.id,
                variant_name=t.variant_name,
                total_score=float(t.total_score),
                skill_coverage_pct=float(t.skill_coverage_pct),
                approval_status=t.approval_status,
            )
            for t in teams
        ]

    @strawberry.field
    def employees(
        self, info: Info, limit: int = 50, offset: int = 0
    ) -> list[EmployeeType]:
        from apps.employees.models import Employee
        qs = Employee.objects.select_related('user', 'department')[offset:offset + limit]
        return [
            EmployeeType(
                id=e.id,
                full_name=e.user.get_full_name() or e.user.email,
                department=e.department.name if e.department else '',
                status=e.status,
                chronotype=e.chronotype,
                weekly_hours=e.weekly_hours,
            )
            for e in qs
        ]

    @strawberry.field
    def projects(
        self, info: Info, limit: int = 50, offset: int = 0
    ) -> list[ProjectType]:
        from apps.projects.models import Project
        qs = Project.objects.all()[offset:offset + limit]
        return [
            ProjectType(
                id=p.id,
                name=p.name,
                status=p.status,
                priority=p.priority,
                start_date=p.start_date,
                end_date=p.end_date,
                planned_hours=p.planned_hours,
            )
            for p in qs
        ]


@strawberry.type
class GenerateTeamResult:
    run_id: int
    status: str


@strawberry.type
class ApproveTeamResult:
    team_id: int
    approval_status: str
    approved_by: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def generate_team(
        self, info: Info, project_id: int, team_size: Optional[int] = 6
    ) -> GenerateTeamResult:
        from apps.teams.services import start_team_generation
        user = info.context.request.user
        if not user or not user.is_authenticated:
            raise Exception("Требуется авторизация для запуска генерации команды.")
        if getattr(user, 'role', '') not in ['admin', 'project_manager'] and not getattr(user, 'is_superuser', False):
            raise Exception("Недостаточно прав. Требуется роль Руководителя проекта или Администратора.")

        from apps.projects.models import Project
        if not Project.objects.filter(pk=project_id).exists():
            raise Exception(f"Проект с ID {project_id} не найден.")

        effective_size = team_size if (team_size and team_size > 0) else 6
        run_id = start_team_generation(
            project_id=project_id,
            initiated_by_id=user.id,
            team_size=effective_size,
        )
        return GenerateTeamResult(run_id=run_id, status='queued')

    @strawberry.mutation
    def approve_team(self, info: Info, team_id: int) -> ApproveTeamResult:
        from apps.teams.models import Team
        from django.utils import timezone
        user = info.context.request.user
        if not user or not user.is_authenticated:
            raise Exception("Требуется авторизация для утверждения команды.")
        if getattr(user, 'role', '') not in ['admin', 'project_manager'] and not getattr(user, 'is_superuser', False):
            raise Exception("Недостаточно прав. Требуется роль Руководителя проекта или Администратора.")

        try:
            team = Team.objects.get(pk=team_id)
        except Team.DoesNotExist:
            raise Exception(f"Команда с ID {team_id} не найдена.")
        team.approval_status = Team.ApprovalStatus.APPROVED
        team.approved_by = user
        team.approved_at = timezone.now()
        team.save(update_fields=['approval_status', 'approved_by', 'approved_at'])
        return ApproveTeamResult(
            team_id=team.id,
            approval_status=team.approval_status,
            approved_by=user.get_full_name() or getattr(user, 'username', 'User'),
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
