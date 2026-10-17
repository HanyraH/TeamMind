"""
Async team generation service.
Runs the algorithm in a background thread, updates TeamRun status.
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from decimal import Decimal

logger = logging.getLogger(__name__)


def _load_candidates(project_id: int):
    """Load all active employees as CandidateProfile objects."""
    from apps.employees.models import Employee
    from apps.projects.models import TaskAssignment
    from apps.vacations.models import Vacation
    from django.db.models import Sum
    from .algorithm import CandidateProfile

    employees = Employee.objects.filter(status='active').select_related(
        'user', 'department'
    ).prefetch_related(
        'skills__skill',
        'vacations',
        'compatibility_preferences',
    )

    # Pre-compute allocated hours per employee
    alloc_qs = TaskAssignment.objects.filter(
        task__project__status='active'
    ).values('employee_id').annotate(total=Sum('allocated_hours'))
    alloc_map = {row['employee_id']: row['total'] or 0 for row in alloc_qs}

    # Approved vacations
    vac_qs = Vacation.objects.filter(status='approved')
    vac_map: dict[int, list] = {}
    for v in vac_qs:
        vac_map.setdefault(v.employee_id, []).append((v.start_date, v.end_date))

    profiles = []
    for emp in employees:
        compat = {
            cp.other_employee_id: cp.score
            for cp in emp.compatibility_preferences.all()
        }
        profiles.append(CandidateProfile(
            employee_id=emp.id,
            full_name=emp.full_name,
            department=emp.department.name if emp.department else '',
            weekly_hours=emp.weekly_hours,
            current_allocated_hours=alloc_map.get(emp.id, 0),
            chronotype=emp.chronotype,
            work_start=emp.preferred_work_start.strftime('%H:%M'),
            work_end=emp.preferred_work_end.strftime('%H:%M'),
            skills={es.skill_id: es.level for es in emp.skills.all()},
            vacation_periods=vac_map.get(emp.id, []),
            compatibility_scores=compat,
        ))
    return profiles


def _load_requirements(project_id: int):
    """Load skill requirements for the project."""
    from apps.projects.models import ProjectSkillRequirement
    from .algorithm import SkillRequirement

    reqs = ProjectSkillRequirement.objects.filter(project_id=project_id).select_related('skill')
    return [
        SkillRequirement(
            skill_id=req.skill_id,
            skill_name=req.skill.name,
            min_level=req.min_level,
            is_mandatory=req.is_mandatory,
            required_count=req.required_count,
        )
        for req in reqs
    ]


def _save_variants(run_id: int, project_id: int, variants: list[dict]):
    """Persist generated team variants to the database."""
    from .models import Team, TeamMember
    from apps.employees.models import Employee

    for variant_data in variants:
        team = Team.objects.create(
            run_id=run_id,
            project_id=project_id,
            variant_name=variant_data['variant_name'],
            total_score=Decimal(str(variant_data['total_score'])),
            skill_score=Decimal(str(variant_data['skill_score'])),
            availability_score=Decimal(str(variant_data['availability_score'])),
            workload_score=Decimal(str(variant_data['workload_score'])),
            time_score=Decimal(str(variant_data['time_score'])),
            compatibility_score=Decimal(str(variant_data['compatibility_score'])),
            skill_coverage_pct=Decimal(str(variant_data['skill_coverage_pct'])),
            explanation=variant_data['explanation'],
        )
        for member_score in variant_data['members']:
            TeamMember.objects.create(
                team=team,
                employee_id=member_score.employee_id,
                contribution_score=member_score.total_score,
                reason=member_score.contribution_reason,
            )


def _run_generation_task(run_id: int, project_id: int, team_size: int):
    """Background thread: execute the full generation pipeline."""
    import django
    from .models import TeamRun
    from .algorithm import generate_team_variants
    from apps.projects.models import Project

    try:
        run = TeamRun.objects.get(pk=run_id)
        run.status = TeamRun.RunStatus.RUNNING
        run.started_at = datetime.now(timezone.utc)
        run.save(update_fields=['status', 'started_at'])

        project = Project.objects.get(pk=project_id)
        requirements = _load_requirements(project_id)
        candidates = _load_candidates(project_id)

        logger.info(
            'Generating teams for project %s: %d requirements, %d candidates',
            project.name, len(requirements), len(candidates)
        )

        variants = generate_team_variants(
            requirements=requirements,
            candidates=candidates,
            project_start=project.start_date,
            project_end=project.end_date,
            team_size=team_size,
        )

        _save_variants(run_id, project_id, variants)

        run.status = TeamRun.RunStatus.SUCCEEDED
        run.finished_at = datetime.now(timezone.utc)
        run.save(update_fields=['status', 'finished_at'])

        logger.info('Team generation run #%d succeeded with %d variants', run_id, len(variants))

    except Exception as exc:
        logger.exception('Team generation run #%d failed: %s', run_id, exc)
        try:
            from .models import TeamRun
            run = TeamRun.objects.get(pk=run_id)
            run.status = TeamRun.RunStatus.FAILED
            run.error_message = str(exc)
            run.finished_at = datetime.now(timezone.utc)
            run.save(update_fields=['status', 'error_message', 'finished_at'])
        except Exception:
            pass


def start_team_generation(project_id: int, initiated_by_id: int, team_size: int = 6) -> int:
    """
    Create a TeamRun record and start the background generation thread.
    Returns the run_id for status polling.
    """
    from .models import TeamRun

    run = TeamRun.objects.create(
        project_id=project_id,
        initiated_by_id=initiated_by_id,
        status=TeamRun.RunStatus.QUEUED,
    )

    thread = threading.Thread(
        target=_run_generation_task,
        args=(run.pk, project_id, team_size),
        daemon=True,
        name=f'team-gen-{run.pk}',
    )
    thread.start()
    return run.pk
