"""
Employee management models: departments, positions, skills, employees,
work preferences, and compatibility preferences.
"""
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Department(models.Model):
    """Company department (e.g. Backend, Frontend, QA)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(models.Model):
    """Job position within the company."""
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='positions'
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        unique_together = ['name', 'department']
        ordering = ['department', 'name']

    def __str__(self):
        return f'{self.name} ({self.department.name})'


class Skill(models.Model):
    """Skill catalog entry (technology, tool, methodology)."""

    class SkillCategory(models.TextChoices):
        TECHNICAL = 'technical', 'Техническая'
        SOFT = 'soft', 'Мягкая'
        MANAGEMENT = 'management', 'Управленческая'
        DOMAIN = 'domain', 'Предметная область'

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=SkillCategory.choices,
        default=SkillCategory.TECHNICAL
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.name} ({self.get_category_display()})'


class Employee(models.Model):
    """Employee profile with work preferences and chronotype."""

    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'active', 'Активен'
        ON_VACATION = 'on_vacation', 'В отпуске'
        INACTIVE = 'inactive', 'Неактивен'

    class Chronotype(models.TextChoices):
        LARK = 'lark', 'Жаворонок'
        OWL = 'owl', 'Сова'
        INTERMEDIATE = 'intermediate', 'Промежуточный'

    class WorkFormat(models.TextChoices):
        REMOTE = 'remote', 'Удалённо'
        OFFICE = 'office', 'Офис'
        HYBRID = 'hybrid', 'Гибрид'

    user = models.OneToOneField(
        'users.User', on_delete=models.CASCADE, related_name='employee_profile'
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, related_name='employees'
    )
    position = models.ForeignKey(
        Position, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees'
    )
    phone = models.CharField(max_length=20, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE
    )

    # Work capacity
    weekly_hours = models.PositiveSmallIntegerField(
        default=40,
        validators=[MinValueValidator(1), MaxValueValidator(80)],
        help_text='Плановая ставка часов в неделю'
    )

    # Chronotype & schedule preferences
    chronotype = models.CharField(
        max_length=20,
        choices=Chronotype.choices,
        default=Chronotype.INTERMEDIATE
    )
    preferred_work_start = models.TimeField(
        default='09:00',
        help_text='Предпочтительное начало рабочего дня'
    )
    preferred_work_end = models.TimeField(
        default='18:00',
        help_text='Предпочтительный конец рабочего дня'
    )
    preferred_meeting_start = models.TimeField(
        default='10:00',
        help_text='Предпочтительное начало встреч'
    )
    preferred_meeting_end = models.TimeField(
        default='17:00',
        help_text='Предпочтительный конец встреч'
    )

    # Work format
    work_format = models.CharField(
        max_length=20,
        choices=WorkFormat.choices,
        default=WorkFormat.HYBRID
    )

    # Bio
    bio = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return self.user.get_full_name()

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email


class EmployeeSkill(models.Model):
    """Skill proficiency level for a specific employee."""
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='skills'
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name='employee_skills'
    )
    level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Уровень владения: 1=Начинающий, 5=Эксперт'
    )
    years_experience = models.DecimalField(
        max_digits=4, decimal_places=1, default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    is_primary = models.BooleanField(default=False, help_text='Основной навык')

    class Meta:
        verbose_name = 'Навык сотрудника'
        verbose_name_plural = 'Навыки сотрудников'
        unique_together = ['employee', 'skill']
        ordering = ['-level', '-is_primary']

    def __str__(self):
        return f'{self.employee} — {self.skill.name} (уровень {self.level})'


class WorkPreference(models.Model):
    """Communication and collaboration preferences."""

    class CommunicationStyle(models.TextChoices):
        ASYNC = 'async', 'Асинхронная коммуникация'
        SYNC = 'sync', 'Синхронная коммуникация'
        MIXED = 'mixed', 'Смешанная'

    class CollaborationStyle(models.TextChoices):
        INDEPENDENT = 'independent', 'Самостоятельная работа'
        COLLABORATIVE = 'collaborative', 'Командная работа'
        FLEXIBLE = 'flexible', 'Гибкий стиль'

    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name='work_preferences'
    )
    communication_style = models.CharField(
        max_length=20,
        choices=CommunicationStyle.choices,
        default=CommunicationStyle.MIXED
    )
    collaboration_style = models.CharField(
        max_length=20,
        choices=CollaborationStyle.choices,
        default=CollaborationStyle.FLEXIBLE
    )
    preferred_team_size_min = models.PositiveSmallIntegerField(default=2)
    preferred_team_size_max = models.PositiveSmallIntegerField(default=8)
    prefers_stable_teams = models.BooleanField(
        default=True, help_text='Предпочитает стабильные составы команды'
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Рабочие предпочтения'
        verbose_name_plural = 'Рабочие предпочтения'

    def __str__(self):
        return f'Предпочтения: {self.employee}'


class CompatibilityPreference(models.Model):
    """Bilateral collaboration preference between two employees."""

    class CompatibilityScore(models.IntegerChoices):
        STRONGLY_PREFER = 2, 'Очень предпочитаю'
        PREFER = 1, 'Предпочитаю'
        NEUTRAL = 0, 'Нейтрально'
        PREFER_NOT = -1, 'Предпочитаю не работать'
        AVOID = -2, 'Избегаю'

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='compatibility_preferences'
    )
    other_employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='compatibility_ratings_received'
    )
    score = models.SmallIntegerField(
        choices=CompatibilityScore.choices,
        default=CompatibilityScore.NEUTRAL
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Предпочтение совместимости'
        verbose_name_plural = 'Предпочтения совместимости'
        unique_together = ['employee', 'other_employee']

    def __str__(self):
        return f'{self.employee} → {self.other_employee}: {self.score}'
