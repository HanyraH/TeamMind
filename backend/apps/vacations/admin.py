from django.contrib import admin
from .models import Vacation


@admin.register(Vacation)
class VacationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'vacation_type', 'start_date', 'end_date', 'status', 'reviewed_by')
    list_filter = ('status', 'vacation_type', 'start_date', 'end_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'reason')
