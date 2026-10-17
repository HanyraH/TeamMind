"""Serializers for Employee, Department, Skill models."""
from rest_framework import serializers
from .models import Department, Position, Skill, Employee, EmployeeSkill, WorkPreference


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'employee_count', 'created_at']

    def get_employee_count(self, obj):
        return obj.employees.filter(status='active').count()


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Position
        fields = ['id', 'name', 'department', 'department_name', 'description']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description']


class DepartmentSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class PositionSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']


class SkillSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']


class EmployeeUserSerializer(serializers.ModelSerializer):
    class Meta:
        from apps.users.models import User
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'avatar']


class EmployeeSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category', read_only=True)
    name = serializers.CharField(source='skill.name', read_only=True)
    skill = SkillSimpleSerializer(read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = ['id', 'skill', 'name', 'skill_name', 'skill_category',
                  'level', 'years_experience', 'is_primary']


class WorkPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkPreference
        fields = ['communication_style', 'collaboration_style',
                  'preferred_team_size_min', 'preferred_team_size_max',
                  'prefers_stable_teams', 'notes']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Full-featured serializer for lists and cards."""
    user = EmployeeUserSerializer(read_only=True)
    department = DepartmentSimpleSerializer(read_only=True)
    position = PositionSimpleSerializer(read_only=True)
    skills = EmployeeSkillSerializer(many=True, read_only=True)
    work_preferences = WorkPreferenceSerializer(read_only=True)

    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    primary_skills = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'department', 'position', 'skills', 'work_preferences',
            'full_name', 'email', 'avatar', 'department_name', 'position_name',
            'status', 'chronotype', 'work_format', 'weekly_hours', 'primary_skills',
            'preferred_work_start', 'preferred_work_end',
            'preferred_meeting_start', 'preferred_meeting_end', 'bio',
        ]

    def get_primary_skills(self, obj):
        skills = obj.skills.filter(is_primary=True).select_related('skill')[:3]
        return [{'name': es.skill.name, 'level': es.level} for es in skills]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for a single employee."""
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    skills = EmployeeSkillSerializer(many=True, read_only=True)
    work_preferences = WorkPreferenceSerializer(read_only=True)
    current_workload_hours = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'email', 'avatar', 'phone',
            'department', 'department_name', 'position', 'position_name',
            'hire_date', 'status', 'weekly_hours', 'chronotype',
            'preferred_work_start', 'preferred_work_end',
            'preferred_meeting_start', 'preferred_meeting_end',
            'work_format', 'bio', 'skills', 'work_preferences',
            'current_workload_hours', 'created_at', 'updated_at',
        ]

    def get_current_workload_hours(self, obj):
        """Sum hours from active task assignments."""
        from apps.projects.models import TaskAssignment
        from django.db.models import Sum
        result = TaskAssignment.objects.filter(
            employee=obj,
            task__project__status='active'
        ).aggregate(total=Sum('allocated_hours'))
        return result['total'] or 0


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'department', 'position', 'phone', 'hire_date',
            'weekly_hours', 'chronotype', 'preferred_work_start', 'preferred_work_end',
            'preferred_meeting_start', 'preferred_meeting_end', 'work_format', 'bio',
        ]
