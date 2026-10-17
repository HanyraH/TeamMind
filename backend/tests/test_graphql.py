"""
Integration tests for Strawberry GraphQL schema endpoints.
Tests dashboardMetrics and schema compilation.
"""
import pytest
from apps.graphql.schema import schema


def test_graphql_schema_compiles():
    assert schema is not None
    query_type = schema.get_type_by_name('Query')
    assert query_type is not None


@pytest.mark.django_db
def test_graphql_dashboard_metrics_execution():
    query = """
    query {
        dashboardMetrics {
            totalEmployees
            activeProjects
        }
    }
    """
    result = schema.execute_sync(query)
    assert result.errors is None
    assert result.data is not None
    assert result.data['dashboardMetrics']['totalEmployees'] >= 0


@pytest.mark.django_db
def test_graphql_employees_and_projects_execution():
    query = """
    query {
        employees(limit: 5) {
            id
            fullName
            status
            weeklyHours
        }
        projects(limit: 5) {
            id
            name
            status
        }
    }
    """
    result = schema.execute_sync(query)
    assert result.errors is None
    assert result.data is not None
    assert 'employees' in result.data
    assert 'projects' in result.data

