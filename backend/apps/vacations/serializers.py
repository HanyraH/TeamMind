"""Serializers for Vacation models."""
from rest_framework import serializers
from django.utils import timezone
from .models import Vacation


class VacationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.get_full_name', read_only=True
    )
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Vacation
        fields = [
            'id', 'employee', 'employee_name', 'vacation_type',
            'start_date', 'end_date', 'duration_days',
            'status', 'reason', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'created_at',
        ]
        read_only_fields = ['status', 'reviewed_by', 'reviewed_at']
        extra_kwargs = {'employee': {'required': False}}

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
            }
        return data

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            raise serializers.ValidationError('Дата окончания не может быть раньше начала.')
        request = self.context.get('request')
        if not data.get('employee') and not self.instance:
            if not (request and getattr(request.user, 'role', None) == 'employee' and hasattr(request.user, 'employee_profile')):
                raise serializers.ValidationError({'employee': 'Необходимо указать сотрудника.'})
        return data
