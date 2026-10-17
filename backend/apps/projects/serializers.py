"""Serializers for Project, Task, and TaskAssignment."""
from rest_framework import serializers
from .models import Project, ProjectSkillRequirement, Task, TaskAssignment


class ProjectSkillRequirementSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = ProjectSkillRequirement
        fields = ['id', 'skill', 'skill_name', 'min_level', 'is_mandatory', 'required_count']


class ProjectListSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    team_count = serializers.SerializerMethodField()
    has_approved_team = serializers.SerializerMethodField()
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'status', 'priority', 'start_date', 'end_date',
            'planned_hours', 'duration_days', 'manager_name',
            'team_count', 'has_approved_team', 'created_at',
        ]

    def get_team_count(self, obj):
        return obj.teams.count()

    def get_has_approved_team(self, obj):
        return obj.teams.filter(approval_status='approved').exists()


class ProjectDetailSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    skill_requirements = ProjectSkillRequirementSerializer(many=True, read_only=True)
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'priority',
            'start_date', 'end_date', 'planned_hours', 'duration_days',
            'manager', 'manager_name', 'skill_requirements',
            'created_at', 'updated_at',
        ]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'project', 'name', 'description', 'status',
            'estimated_hours', 'required_skills', 'created_at',
        ]


class TaskAssignmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    task_name = serializers.CharField(source='task.name', read_only=True)

    class Meta:
        model = TaskAssignment
        fields = ['id', 'task', 'task_name', 'employee', 'employee_name',
                  'allocated_hours', 'assigned_at', 'note']
