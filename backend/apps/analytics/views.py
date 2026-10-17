"""Analytics views — aggregated statistics for dashboard."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Aggregated metrics for the main dashboard."""
    from apps.employees.models import Employee, Department
    from apps.projects.models import Project, TaskAssignment
    from apps.vacations.models import Vacation

    total_emp = Employee.objects.count()
    active_emp = Employee.objects.filter(status='active').count()
    total_proj = Project.objects.count()
    active_proj = Project.objects.filter(status='active').count()
    pending_vac = Vacation.objects.filter(status='pending').count()

    # Workload by department
    dept_workloads = []
    for dept in Department.objects.all():
        emps = Employee.objects.filter(department=dept, status='active')
        count = emps.count()
        if count == 0:
            continue
        emp_ids = list(emps.values_list('id', flat=True))
        total_cap = sum(e.weekly_hours for e in emps)
        alloc = TaskAssignment.objects.filter(
            employee_id__in=emp_ids,
            task__project__status='active'
        ).aggregate(total=Sum('allocated_hours'))
        total_alloc = alloc['total'] or 0
        dept_workloads.append({
            'department': dept.name,
            'employee_count': count,
            'utilization_pct': round(total_alloc / total_cap * 100, 1) if total_cap else 0,
        })

    # Chronotype distribution
    from django.db.models import Value
    chronotype_dist = (
        Employee.objects.filter(status='active')
        .values('chronotype')
        .annotate(count=Count('id'))
        .order_by('chronotype')
    )

    # Overloaded employees (>85%)
    all_employees = Employee.objects.filter(status='active')
    emp_ids = list(all_employees.values_list('id', flat=True))
    alloc_map = {
        row['employee_id']: row['total'] or 0
        for row in TaskAssignment.objects.filter(
            employee_id__in=emp_ids,
            task__project__status='active'
        ).values('employee_id').annotate(total=Sum('allocated_hours'))
    }
    overloaded = [
        {'name': e.full_name, 'utilization_pct': round(alloc_map.get(e.id, 0) / e.weekly_hours * 100, 1)}
        for e in all_employees
        if e.weekly_hours > 0 and alloc_map.get(e.id, 0) / e.weekly_hours > 0.85
    ]

    avg_utilization = (
        round(sum(d['utilization_pct'] for d in dept_workloads) / len(dept_workloads), 1)
        if dept_workloads else 0.0
    )

    return Response({
        'employees': {
            'total': total_emp,
            'active': active_emp,
        },
        'projects': {
            'total': total_proj,
            'active': active_proj,
        },
        'vacations': {
            'pending': pending_vac,
        },
        'avg_utilization_pct': avg_utilization,
        'department_workloads': dept_workloads,
        'chronotype_distribution': list(chronotype_dist),
        'overloaded_employees': overloaded[:10],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def projects_without_team(request):
    """Projects in planning/active status with no approved team."""
    from apps.projects.models import Project
    from apps.teams.models import Team

    approved_project_ids = Team.objects.filter(
        approval_status='approved'
    ).values_list('project_id', flat=True)

    projects = Project.objects.filter(
        status__in=['planning', 'active']
    ).exclude(id__in=approved_project_ids).values('id', 'name', 'status', 'priority', 'start_date')

    return Response({'projects': list(projects)})
