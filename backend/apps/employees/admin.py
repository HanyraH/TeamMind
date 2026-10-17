from django.contrib import admin
from .models import Department, Position, Skill, Employee, EmployeeSkill, WorkPreference


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    search_fields = ['name']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']


class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'department', 'position', 'status', 'chronotype', 'weekly_hours']
    list_filter = ['department', 'status', 'chronotype', 'work_format']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    inlines = [EmployeeSkillInline]
    raw_id_fields = ['user', 'department', 'position']
