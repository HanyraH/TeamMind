"""
Team generation models: TeamRun (async job tracking) and Team (result).
"""
from django.db import models


class TeamRun(models.Model):
    """Tracks the lifecycle of a team generation job."""

    class RunStatus(models.TextChoices):
        QUEUED = 'queued', 'В очереди'
        RUNNING = 'running', 'Выполняется'
        SUCCEEDED = 'succeeded', 'Успешно'
        FAILED = 'failed', 'Ошибка'

    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='team_runs'
    )
    initiated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True
    )
    status = models.CharField(
        max_length=20, choices=RunStatus.choices, default=RunStatus.QUEUED
    )
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Запуск генерации команды'
        verbose_name_plural = 'Запуски генерации команд'
        ordering = ['-created_at']

    def __str__(self):
        return f'Run #{self.pk} for {self.project.name} [{self.status}]'


class Team(models.Model):
    """A generated team variant for a project."""

    class ApprovalStatus(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        APPROVED = 'approved', 'Утверждён'
        REJECTED = 'rejected', 'Отклонён'

    run = models.ForeignKey(TeamRun, on_delete=models.CASCADE, related_name='teams')
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='teams'
    )
    variant_name = models.CharField(max_length=100, help_text='Например: "Максимальный уровень"')
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    skill_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    availability_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    workload_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    time_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    compatibility_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    skill_coverage_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    explanation = models.JSONField(
        default=dict,
        help_text='Structured explanation: strengths, risks, missing skills'
    )
    approval_status = models.CharField(
        max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT
    )
    approved_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_teams'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'
        ordering = ['-total_score']

    def __str__(self):
        return f'{self.variant_name} (score={self.total_score})'


class TeamMember(models.Model):
    """A member of a specific team variant."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    role_in_team = models.CharField(max_length=100, blank=True)
    contribution_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reason = models.TextField(blank=True, help_text='Почему выбран этот сотрудник')

    class Meta:
        verbose_name = 'Участник команды'
        verbose_name_plural = 'Участники команды'
        unique_together = ['team', 'employee']

    def __str__(self):
        return f'{self.employee} → {self.team}'
