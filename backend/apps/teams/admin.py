from django.contrib import admin
from .models import TeamRun, Team, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0


@admin.register(TeamRun)
class TeamRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'status', 'initiated_by', 'created_at')
    list_filter = ('status', 'created_at')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('variant_name', 'project', 'total_score', 'skill_coverage_pct', 'approval_status')
    list_filter = ('approval_status', 'project')
    inlines = [TeamMemberInline]
