"""Models for Projects, Tasks, Task Requirements and Assignments."""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Project(models.Model):
    """A company project requiring team assembly."""

    class ProjectStatus(models.TextChoices):
        PLANNING = 'planning', 'Планирование'
        ACTIVE = 'active', 'Активный'
        ON_HOLD = 'on_hold', 'Приостановлен'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'

    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'
        CRITICAL = 'critical', 'Критический'

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PLANNING
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    manager = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True,
        related_name='managed_projects'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    planned_hours = models.PositiveIntegerField(default=0, help_text='Плановые часы на проект')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days


class ProjectSkillRequirement(models.Model):
    """Required skill for a project (used in team generation)."""
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='skill_requirements'
    )
    skill = models.ForeignKey('employees.Skill', on_delete=models.CASCADE)
    min_level = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_mandatory = models.BooleanField(default=True)
    required_count = models.PositiveSmallIntegerField(
        default=1, help_text='Сколько специалистов с данным навыком нужно'
    )

    class Meta:
        verbose_name = 'Требование к навыку'
        verbose_name_plural = 'Требования к навыкам'
        unique_together = ['project', 'skill']

    def __str__(self):
        return f'{self.project.name} — {self.skill.name} (мин. {self.min_level})'


class Task(models.Model):
    """Project task with skill requirements."""

    class TaskStatus(models.TextChoices):
        TODO = 'todo', 'К выполнению'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На проверке'
        DONE = 'done', 'Выполнено'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO
    )
    estimated_hours = models.PositiveIntegerField(default=0)
    required_skills = models.ManyToManyField(
        'employees.Skill', blank=True, related_name='tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['project', 'name']

    def __str__(self):
        return f'{self.project.name} / {self.name}'


class TaskAssignment(models.Model):
    """Assignment of an employee to a specific task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='task_assignments'
    )
    allocated_hours = models.PositiveIntegerField(default=0)
    assigned_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Назначение на задачу'
        verbose_name_plural = 'Назначения на задачи'
        unique_together = ['task', 'employee']

    def __str__(self):
        return f'{self.employee} → {self.task}'
