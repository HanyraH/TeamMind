"""Custom User model with role-based access control."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Администратор'
    PROJECT_MANAGER = 'project_manager', 'Менеджер проекта'
    EMPLOYEE = 'employee', 'Сотрудник'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_project_manager(self):
        return self.role == UserRole.PROJECT_MANAGER

    @property
    def is_employee_role(self):
        return self.role == UserRole.EMPLOYEE
