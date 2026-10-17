"""Filters for Employee search and filtering."""
import django_filters
from .models import Employee, Skill


class EmployeeFilter(django_filters.FilterSet):
    department = django_filters.NumberFilter(field_name='department__id')
    status = django_filters.CharFilter(field_name='status')
    chronotype = django_filters.CharFilter(field_name='chronotype')
    work_format = django_filters.CharFilter(field_name='work_format')
    skill = django_filters.NumberFilter(
        field_name='skills__skill__id',
        label='Фильтр по навыку (ID)'
    )
    skill_level_min = django_filters.NumberFilter(
        field_name='skills__level', lookup_expr='gte',
        label='Минимальный уровень навыка'
    )
    search = django_filters.CharFilter(method='filter_search', label='Поиск')

    class Meta:
        model = Employee
        fields = ['department', 'status', 'chronotype', 'work_format', 'skill']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            user__first_name__icontains=value
        ) | queryset.filter(
            user__last_name__icontains=value
        ) | queryset.filter(
            user__email__icontains=value
        )
