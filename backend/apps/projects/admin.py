from django.contrib import admin
from .models import Project, ProjectSkillRequirement, Task, TaskAssignment


class ProjectSkillRequirementInline(admin.TabularInline):
    model = ProjectSkillRequirement
    extra = 1


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'priority', 'manager', 'start_date', 'end_date', 'planned_hours')
    list_filter = ('status', 'priority', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    inlines = [ProjectSkillRequirementInline, TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'estimated_hours')
    list_filter = ('status', 'project')
    search_fields = ('name', 'description')
    filter_horizontal = ('required_skills',)


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'employee', 'allocated_hours', 'assigned_at')
    list_filter = ('task__project', 'employee')
