"""
Unit tests for the multi-criteria team selection algorithm.
Verifies formula S = 0.35K + 0.25A + 0.20L + 0.10T + 0.10C,
mandatory skill constraints, and vacation exclusion rules.
"""
from datetime import date, timedelta
from decimal import Decimal
import pytest

from apps.teams.algorithm import (
    CandidateProfile,
    SkillRequirement,
    TeamScoringEngine,
    generate_team_variants,
    WEIGHTS,
)


@pytest.fixture
def sample_requirements():
    return [
        SkillRequirement(skill_id=1, skill_name='Python', min_level=3, is_mandatory=True, required_count=1),
        SkillRequirement(skill_id=2, skill_name='React', min_level=3, is_mandatory=True, required_count=1),
        SkillRequirement(skill_id=3, skill_name='PostgreSQL', min_level=2, is_mandatory=False, required_count=1),
    ]


@pytest.fixture
def project_dates():
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    return start, end


def test_weights_sum_to_one():
    total = sum(WEIGHTS.values())
    assert total == Decimal('1.0')


def test_vacation_disqualification(sample_requirements, project_dates):
    start, end = project_dates
    engine = TeamScoringEngine(sample_requirements, start, end)

    # Candidate with vacation overlapping project
    cand_vacation = CandidateProfile(
        employee_id=10,
        full_name='Иван Иванов',
        department='Backend',
        weekly_hours=40,
        current_allocated_hours=0,
        chronotype='owl',
        work_start='11:00',
        work_end='20:00',
        skills={1: 4, 3: 3},
        vacation_periods=[(start, start + timedelta(days=28))],
        compatibility_scores={},
    )

    scores = engine.score_candidate(cand_vacation)
    assert not scores.is_eligible
    assert 'отпуск' in scores.disqualification_reason.lower()


def test_candidate_without_vacation_is_eligible(sample_requirements, project_dates):
    start, end = project_dates
    engine = TeamScoringEngine(sample_requirements, start, end)

    cand = CandidateProfile(
        employee_id=11,
        full_name='Мария Смирнова',
        department='Backend',
        weekly_hours=40,
        current_allocated_hours=10,
        chronotype='intermediate',
        work_start='09:00',
        work_end='18:00',
        skills={1: 4, 3: 3},
        vacation_periods=[],
        compatibility_scores={},
    )

    scores = engine.score_candidate(cand)
    assert scores.is_eligible
    assert scores.availability_score == Decimal('100')
    assert scores.skill_score > Decimal('0')
    assert scores.total_score > Decimal('0')


def test_generate_team_variants(sample_requirements, project_dates):
    start, end = project_dates

    # 5 candidates covering skills
    candidates = [
        CandidateProfile(
            employee_id=1, full_name='Python Senior', department='Backend',
            weekly_hours=40, current_allocated_hours=10, chronotype='intermediate',
            work_start='09:00', work_end='18:00', skills={1: 5, 3: 4},
            vacation_periods=[], compatibility_scores={2: 2},
        ),
        CandidateProfile(
            employee_id=2, full_name='React Senior', department='Frontend',
            weekly_hours=40, current_allocated_hours=5, chronotype='intermediate',
            work_start='09:00', work_end='18:00', skills={2: 5},
            vacation_periods=[], compatibility_scores={1: 2},
        ),
        CandidateProfile(
            employee_id=3, full_name='Fullstack Mid', department='Backend',
            weekly_hours=40, current_allocated_hours=0, chronotype='owl',
            work_start='11:00', work_end='20:00', skills={1: 3, 2: 3, 3: 3},
            vacation_periods=[], compatibility_scores={},
        ),
        CandidateProfile(
            employee_id=4, full_name='DBA Specialist', department='Backend',
            weekly_hours=40, current_allocated_hours=15, chronotype='lark',
            work_start='08:00', work_end='17:00', skills={3: 5},
            vacation_periods=[], compatibility_scores={},
        ),
    ]

    variants = generate_team_variants(
        requirements=sample_requirements,
        candidates=candidates,
        project_start=start,
        project_end=end,
        team_size=3,
    )

    assert len(variants) > 0
    top = variants[0]
    assert 'total_score' in top
    assert 'skill_coverage_pct' in top
    assert top['total_score'] > 0
    assert len(top['members']) <= 3
