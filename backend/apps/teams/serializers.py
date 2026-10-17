"""Serializers for Team, TeamRun, TeamMember."""
from rest_framework import serializers
from .models import Team, TeamRun, TeamMember


class TeamRunSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    initiated_by_name = serializers.CharField(
        source='initiated_by.get_full_name', read_only=True
    )
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = TeamRun
        fields = [
            'id', 'project', 'project_name', 'status', 'error_message',
            'initiated_by', 'initiated_by_name',
            'created_at', 'started_at', 'finished_at', 'duration_seconds',
        ]

    def get_duration_seconds(self, obj):
        if obj.started_at and obj.finished_at:
            return (obj.finished_at - obj.started_at).seconds
        return None


class TeamMemberSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='employee.user.email', read_only=True)
    department = serializers.CharField(source='employee.department.name', read_only=True)
    avatar = serializers.ImageField(source='employee.user.avatar', read_only=True)
    skills_summary = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = [
            'id', 'employee', 'employee_name', 'employee_email', 'department',
            'avatar', 'role_in_team', 'contribution_score', 'reason', 'skills_summary',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        emp = instance.employee
        if emp:
            data['employee'] = {
                'id': emp.id,
                'user': {
                    'id': emp.user.id if emp.user else None,
                    'first_name': emp.user.first_name if emp.user else '',
                    'last_name': emp.user.last_name if emp.user else '',
                    'email': emp.user.email if emp.user else '',
                },
                'department': {
                    'id': emp.department.id if emp.department else None,
                    'name': emp.department.name if emp.department else '',
                },
                'chronotype': emp.chronotype,
                'work_format': emp.work_format,
                'weekly_hours': emp.weekly_hours,
            }
        return data

    def get_skills_summary(self, obj):
        skills = obj.employee.skills.filter(is_primary=True).select_related('skill')[:4]
        return [{'name': es.skill.name, 'level': es.level} for es in skills]


class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name', read_only=True
    )
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'project', 'project_name', 'run', 'variant_name',
            'total_score', 'skill_score', 'availability_score',
            'workload_score', 'time_score', 'compatibility_score',
            'skill_coverage_pct', 'explanation',
            'approval_status', 'approved_by', 'approved_by_name', 'approved_at',
            'members', 'member_count', 'created_at',
        ]

    def get_member_count(self, obj):
        return obj.members.count()


class TeamDetailSerializer(TeamSerializer):
    pass
