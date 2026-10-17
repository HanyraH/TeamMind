"""
Integration tests for Django REST Framework API endpoints.
Tests authentication, permissions, employees catalog, projects and teams.
"""
import pytest
from rest_framework.test import APIClient
from apps.users.models import User, UserRole
from apps.projects.models import Project


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    user, _ = User.objects.get_or_create(
        email='admin_test@teammind.ru',
        defaults={
            'username': 'admin_test',
            'role': UserRole.ADMIN,
            'is_staff': True,
        }
    )
    user.set_password('AdminTest123!')
    user.save()
    return user


@pytest.fixture
def pm_user(db):
    user, _ = User.objects.get_or_create(
        email='pm_test@teammind.ru',
        defaults={
            'username': 'pm_test',
            'role': UserRole.PROJECT_MANAGER,
        }
    )
    user.set_password('PmTest123!')
    user.save()
    return user


@pytest.mark.django_db
def test_login_success(api_client, admin_user):
    res = api_client.post('/api/auth/login/', {
        'email': 'admin_test@teammind.ru',
        'password': 'AdminTest123!',
    })
    assert res.status_code == 200
    assert 'access' in res.data
    assert 'refresh' in res.data


@pytest.mark.django_db
def test_login_invalid_credentials(api_client, admin_user):
    res = api_client.post('/api/auth/login/', {
        'email': 'admin_test@teammind.ru',
        'password': 'WrongPassword!',
    })
    assert res.status_code == 401


@pytest.mark.django_db
def test_employees_list_requires_auth(api_client):
    res = api_client.get('/api/employees/')
    assert res.status_code == 401


@pytest.mark.django_db
def test_employees_list_authenticated(api_client, pm_user):
    api_client.force_authenticate(user=pm_user)
    res = api_client.get('/api/employees/')
    assert res.status_code == 200


@pytest.mark.django_db
def test_analytics_dashboard_authenticated(api_client, pm_user):
    api_client.force_authenticate(user=pm_user)
    res = api_client.get('/api/analytics/dashboard/')
    assert res.status_code == 200
    assert 'employees' in res.data
    assert 'projects' in res.data
