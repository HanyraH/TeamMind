"""Vacation request models."""
from django.db import models


class Vacation(models.Model):
    """Employee vacation/absence period."""

    class VacationStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        APPROVED = 'approved', 'Одобрен'
        REJECTED = 'rejected', 'Отклонён'

    class VacationType(models.TextChoices):
        ANNUAL = 'annual', 'Ежегодный отпуск'
        SICK = 'sick', 'Больничный'
        UNPAID = 'unpaid', 'За свой счёт'
        REMOTE = 'remote_work', 'Удалённая работа'
        OTHER = 'other', 'Иное'

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='vacations'
    )
    vacation_type = models.CharField(
        max_length=20, choices=VacationType.choices, default=VacationType.ANNUAL
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=VacationStatus.choices, default=VacationStatus.PENDING
    )
    reason = models.TextField(blank=True, help_text='Причина или комментарий')
    reviewed_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_vacations'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Отпуск'
        verbose_name_plural = 'Отпуска'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.employee} ({self.start_date} — {self.end_date}): {self.get_status_display()}'

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1

    def overlaps_with(self, start_date, end_date) -> bool:
        """Check if this vacation overlaps with the given date range."""
        return self.start_date <= end_date and self.end_date >= start_date
