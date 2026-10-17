"""
TeamMind Team Selection Algorithm
==================================
Multi-criteria scoring algorithm for optimal team assembly.

Formula: S = 0.35*K + 0.25*A + 0.20*L + 0.10*T + 0.10*C
  K — Skill score (skill coverage and level match)
  A — Availability score (no vacation conflicts)
  L — Workload balance score (utilization percentage)
  T — Time compatibility score (chronotype + working hours overlap)
  C — Collaboration compatibility score (mutual preferences)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)

# Scoring weights (must sum to 1.0)
WEIGHTS = {
    'skill': Decimal('0.35'),
    'availability': Decimal('0.25'),
    'workload': Decimal('0.20'),
    'time': Decimal('0.10'),
    'compatibility': Decimal('0.10'),
}

# Maximum load threshold — over this, candidate is penalized
MAX_LOAD_PCT = 85


@dataclass
class SkillRequirement:
    skill_id: int
    skill_name: str
    min_level: int
    is_mandatory: bool
    required_count: int


@dataclass
class CandidateProfile:
    employee_id: int
    full_name: str
    department: str
    weekly_hours: int
    current_allocated_hours: int  # hours already committed on active projects
    chronotype: str  # 'lark' | 'owl' | 'intermediate'
    work_start: str  # HH:MM
    work_end: str    # HH:MM
    skills: dict[int, int]          # skill_id -> level
    vacation_periods: list[tuple[date, date]]  # approved vacations
    compatibility_scores: dict[int, int]       # employee_id -> score (-2..2)


@dataclass
class CandidateScores:
    employee_id: int
    full_name: str
    skill_score: Decimal = Decimal('0')
    availability_score: Decimal = Decimal('0')
    workload_score: Decimal = Decimal('0')
    time_score: Decimal = Decimal('0')
    compatibility_score: Decimal = Decimal('0')
    total_score: Decimal = Decimal('0')
    covered_skills: list[int] = field(default_factory=list)
    contribution_reason: str = ''
    is_eligible: bool = True
    disqualification_reason: str = ''

    def compute_total(self):
        self.total_score = (
            WEIGHTS['skill'] * self.skill_score +
            WEIGHTS['availability'] * self.availability_score +
            WEIGHTS['workload'] * self.workload_score +
            WEIGHTS['time'] * self.time_score +
            WEIGHTS['compatibility'] * self.compatibility_score
        )


class TeamScoringEngine:
    """Computes scores for each candidate against project requirements."""

    def __init__(
        self,
        requirements: list[SkillRequirement],
        project_start: date,
        project_end: date,
    ):
        self.requirements = requirements
        self.project_start = project_start
        self.project_end = project_end

    # ── K: Skill Score ──────────────────────────────────────────────────────

    def _skill_score(self, candidate: CandidateProfile) -> tuple[Decimal, list[int]]:
        """
        Score how well candidate covers required skills.
        Returns (score 0-100, list of covered skill IDs).
        """
        if not self.requirements:
            return Decimal('100'), []

        total_weight = Decimal('0')
        earned_weight = Decimal('0')
        covered: list[int] = []

        for req in self.requirements:
            # Mandatory skills have double weight
            req_weight = Decimal('2') if req.is_mandatory else Decimal('1')
            total_weight += req_weight

            candidate_level = candidate.skills.get(req.skill_id, 0)
            if candidate_level >= req.min_level:
                # Level surplus adds bonus (up to 100%)
                level_match = min(candidate_level / req.min_level, Decimal('1.5'))
                earned_weight += req_weight * Decimal(str(level_match))
                covered.append(req.skill_id)

        score = (earned_weight / total_weight * 100) if total_weight else Decimal('0')
        return min(score, Decimal('100')), covered

    # ── A: Availability Score ────────────────────────────────────────────────

    def _availability_score(self, candidate: CandidateProfile) -> Decimal:
        """
        100 if no vacation overlaps project period.
        0 if full overlap. Proportional otherwise.
        """
        project_days = (self.project_end - self.project_start).days + 1
        if project_days <= 0:
            return Decimal('100')

        blocked_days = 0
        for vac_start, vac_end in candidate.vacation_periods:
            overlap_start = max(vac_start, self.project_start)
            overlap_end = min(vac_end, self.project_end)
            if overlap_start <= overlap_end:
                blocked_days += (overlap_end - overlap_start).days + 1

        available_ratio = max(0, (project_days - blocked_days) / project_days)
        return Decimal(str(round(available_ratio * 100, 2)))

    # ── L: Workload Balance Score ────────────────────────────────────────────

    def _workload_score(self, candidate: CandidateProfile) -> Decimal:
        """
        Score based on current utilization.
        <60%  → high score (fresh resource)
        60-85% → medium score
        >85%  → penalized
        100%+ → 0 (overloaded)
        """
        if candidate.weekly_hours <= 0:
            return Decimal('0')

        utilization_pct = (candidate.current_allocated_hours / candidate.weekly_hours) * 100

        if utilization_pct >= 100:
            return Decimal('0')
        elif utilization_pct >= MAX_LOAD_PCT:
            # Penalized zone: 85-100% → score 0-30
            score = 30 * (1 - (utilization_pct - MAX_LOAD_PCT) / (100 - MAX_LOAD_PCT))
        elif utilization_pct >= 60:
            # Normal zone: 60-85% → score 30-75
            score = 30 + 45 * (1 - (utilization_pct - 60) / 25)
        else:
            # Optimal zone: 0-60% → score 75-100
            score = 75 + 25 * (1 - utilization_pct / 60)

        return Decimal(str(round(score, 2)))

    # ── T: Time Compatibility Score ──────────────────────────────────────────

    def _time_score(
        self,
        candidate: CandidateProfile,
        team_candidates: list[CandidateProfile],
    ) -> Decimal:
        """
        Score based on chronotype distribution and working hours overlap with team.
        Solo candidate scores 80 as baseline.
        """
        if not team_candidates:
            return Decimal('80')

        chronotype_map = {'lark': 0, 'intermediate': 1, 'owl': 2}
        candidate_ct = chronotype_map.get(candidate.chronotype, 1)
        team_chronotypes = [chronotype_map.get(c.chronotype, 1) for c in team_candidates]

        if team_chronotypes:
            avg_ct = sum(team_chronotypes) / len(team_chronotypes)
            ct_diff = abs(candidate_ct - avg_ct)
            # 0 diff → 100, 2 diff → 40
            ct_score = max(40, 100 - ct_diff * 30)
        else:
            ct_score = 80

        # Working hours overlap
        def time_to_minutes(t: str) -> int:
            h, m = map(int, t.split(':'))
            return h * 60 + m

        c_start = time_to_minutes(candidate.work_start)
        c_end = time_to_minutes(candidate.work_end)
        if c_end <= c_start:
            return Decimal(str(round(ct_score * 0.6, 2)))

        overlap_scores = []
        for tc in team_candidates:
            t_start = time_to_minutes(tc.work_start)
            t_end = time_to_minutes(tc.work_end)
            overlap = max(0, min(c_end, t_end) - max(c_start, t_start))
            c_duration = c_end - c_start
            overlap_pct = overlap / c_duration if c_duration > 0 else 0
            overlap_scores.append(overlap_pct)

        avg_overlap = sum(overlap_scores) / len(overlap_scores) if overlap_scores else 0.8
        final = ct_score * 0.5 + avg_overlap * 100 * 0.5
        return Decimal(str(round(final, 2)))

    # ── C: Compatibility Score ───────────────────────────────────────────────

    def _compatibility_score(
        self,
        candidate: CandidateProfile,
        team_candidates: list[CandidateProfile],
    ) -> Decimal:
        """
        Score based on mutual collaboration preferences.
        Range: -2 (avoid) to +2 (strongly prefer). Normalized to 0-100.
        """
        if not team_candidates:
            return Decimal('75')

        scores = []
        for tc in team_candidates:
            # Bidirectional: average of both preferences
            fwd = candidate.compatibility_scores.get(tc.employee_id, 0)
            bwd = tc.compatibility_scores.get(candidate.employee_id, 0)
            bilateral = (fwd + bwd) / 2
            # Normalize from -2..2 → 0..100
            normalized = (bilateral + 2) / 4 * 100
            scores.append(normalized)

        avg = sum(scores) / len(scores) if scores else 75
        return Decimal(str(round(avg, 2)))

    # ── Hard Filter ──────────────────────────────────────────────────────────

    def is_eligible(self, candidate: CandidateProfile) -> tuple[bool, str]:
        """
        Hard constraint filter: completely excludes a candidate.
        Returns (eligible: bool, reason: str).
        """
        # 1. Check vacation overlap
        for vac_start, vac_end in candidate.vacation_periods:
            if vac_start <= self.project_end and vac_end >= self.project_start:
                # Full project overlap → ineligible
                project_days = (self.project_end - self.project_start).days + 1
                overlap_start = max(vac_start, self.project_start)
                overlap_end = min(vac_end, self.project_end)
                overlap_days = (overlap_end - overlap_start).days + 1
                if overlap_days >= project_days * 0.75:
                    return False, (
                        f'Отпуск перекрывает более 75% проекта '
                        f'({vac_start} — {vac_end})'
                    )

        # 2. Check critical mandatory skills
        mandatory_reqs = [r for r in self.requirements if r.is_mandatory]
        missing_mandatory = [
            r.skill_name for r in mandatory_reqs
            if candidate.skills.get(r.skill_id, 0) < r.min_level
        ]

        # Candidate is eligible even if missing mandatory skills —
        # they will score low on K but won't be hard-excluded
        # (hard exclusion only if 100% overloaded)
        if candidate.weekly_hours > 0:
            util_pct = (candidate.current_allocated_hours / candidate.weekly_hours) * 100
            if util_pct >= 100:
                return False, f'Сотрудник полностью перегружен ({util_pct:.0f}% загрузки)'

        return True, ''

    # ── Score All Candidates ─────────────────────────────────────────────────

    def score_candidate(
        self,
        candidate: CandidateProfile,
        team_members: list[CandidateProfile] = None,
    ) -> CandidateScores:
        team_members = team_members or []
        result = CandidateScores(
            employee_id=candidate.employee_id,
            full_name=candidate.full_name,
        )

        eligible, reason = self.is_eligible(candidate)
        if not eligible:
            result.is_eligible = False
            result.disqualification_reason = reason
            return result

        skill_s, covered = self._skill_score(candidate)
        result.skill_score = skill_s
        result.covered_skills = covered
        result.availability_score = self._availability_score(candidate)
        result.workload_score = self._workload_score(candidate)
        result.time_score = self._time_score(candidate, team_members)
        result.compatibility_score = self._compatibility_score(candidate, team_members)
        result.compute_total()

        # Build human-readable reason
        result.contribution_reason = self._build_reason(candidate, result)
        return result

    def _build_reason(self, candidate: CandidateProfile, scores: CandidateScores) -> str:
        parts = []
        covered_names = [
            r.skill_name for r in self.requirements if r.skill_id in scores.covered_skills
        ]
        if covered_names:
            parts.append(f'Покрывает навыки: {", ".join(covered_names)}')

        util = (candidate.current_allocated_hours / candidate.weekly_hours * 100
                if candidate.weekly_hours else 0)
        if util < 60:
            parts.append(f'Высокая доступность ({util:.0f}% загрузки)')
        elif util < 85:
            parts.append(f'Нормальная загрузка ({util:.0f}%)')
        else:
            parts.append(f'⚠️ Высокая загрузка ({util:.0f}%)')

        if scores.availability_score < 80:
            parts.append('⚠️ Частичное пересечение с отпуском')

        return '. '.join(parts)


class TeamCompositionBuilder:
    """
    Greedy iterative team builder.
    Selects candidates one by one, re-scoring after each addition
    to account for team dynamics (chronotype mix, compatibility).
    """

    def __init__(
        self,
        engine: TeamScoringEngine,
        all_candidates: list[CandidateProfile],
        team_size: int,
        strategy: str = 'balanced',
    ):
        self.engine = engine
        self.all_candidates = all_candidates
        self.team_size = team_size
        self.strategy = strategy

    def build(self) -> list[CandidateScores]:
        """
        Build an optimal team using greedy selection with dynamic rescoring.
        """
        selected: list[CandidateProfile] = []
        selected_scores: list[CandidateScores] = []
        remaining = list(self.all_candidates)

        # Apply strategy-specific boost
        strategy_boosts = self._get_strategy_boosts()

        for _ in range(self.team_size):
            if not remaining:
                break

            best_score: Optional[CandidateScores] = None
            best_candidate: Optional[CandidateProfile] = None

            for candidate in remaining:
                scores = self.engine.score_candidate(candidate, selected)
                if not scores.is_eligible:
                    continue

                # Apply strategy-specific modifier
                modified_total = scores.total_score * strategy_boosts.get(
                    self._dominant_attribute(scores), Decimal('1')
                )
                scores.total_score = modified_total

                if best_score is None or modified_total > best_score.total_score:
                    best_score = scores
                    best_candidate = candidate

            if best_candidate and best_score:
                selected.append(best_candidate)
                selected_scores.append(best_score)
                remaining.remove(best_candidate)

        return selected_scores

    def _dominant_attribute(self, scores: CandidateScores) -> str:
        attrs = {
            'skill': scores.skill_score,
            'workload': scores.workload_score,
            'time': scores.time_score,
        }
        return max(attrs, key=lambda k: attrs[k])

    def _get_strategy_boosts(self) -> dict[str, Decimal]:
        if self.strategy == 'max_skills':
            return {'skill': Decimal('1.2')}
        elif self.strategy == 'balanced_load':
            return {'workload': Decimal('1.3')}
        elif self.strategy == 'max_schedule':
            return {'time': Decimal('1.3')}
        return {}


def generate_team_variants(
    requirements: list[SkillRequirement],
    candidates: list[CandidateProfile],
    project_start: date,
    project_end: date,
    team_size: int,
) -> list[dict]:
    """
    Generate 3 team variant strategies.
    Returns list of dicts with variant metadata and selected members.
    """
    engine = TeamScoringEngine(requirements, project_start, project_end)

    strategies = [
        ('Максимальный уровень компетенций', 'max_skills'),
        ('Оптимальный баланс нагрузки', 'balanced_load'),
        ('Максимальное совпадение графиков', 'max_schedule'),
    ]

    variants = []
    for variant_name, strategy in strategies:
        builder = TeamCompositionBuilder(engine, candidates, team_size, strategy)
        selected = builder.build()

        if not selected:
            logger.warning('Strategy %s produced no candidates', strategy)
            continue

        # Compute aggregate scores
        def avg(attr):
            vals = [getattr(s, attr) for s in selected]
            return round(sum(vals) / len(vals), 2) if vals else 0

        # Skill coverage
        all_required_ids = {r.skill_id for r in requirements}
        covered_ids = set()
        for s in selected:
            covered_ids.update(s.covered_skills)
        skill_coverage_pct = (
            len(covered_ids) / len(all_required_ids) * 100
            if all_required_ids else 100
        )

        # Missing skills
        missing = [
            r.skill_name for r in requirements
            if r.skill_id not in covered_ids and r.is_mandatory
        ]

        variants.append({
            'variant_name': variant_name,
            'strategy': strategy,
            'members': selected,
            'total_score': avg('total_score'),
            'skill_score': avg('skill_score'),
            'availability_score': avg('availability_score'),
            'workload_score': avg('workload_score'),
            'time_score': avg('time_score'),
            'compatibility_score': avg('compatibility_score'),
            'skill_coverage_pct': round(skill_coverage_pct, 1),
            'explanation': {
                'strengths': _build_strengths(selected, avg),
                'risks': _build_risks(selected, missing),
                'missing_mandatory_skills': missing,
            }
        })

    return variants


def _build_strengths(selected: list[CandidateScores], avg_fn) -> list[str]:
    strengths = []
    if avg_fn('skill_score') >= 80:
        strengths.append('Высокое соответствие навыков требованиям проекта')
    if avg_fn('availability_score') >= 90:
        strengths.append('Команда полностью доступна на весь период проекта')
    if avg_fn('workload_score') >= 75:
        strengths.append('Сбалансированная загрузка — нет перегруженных специалистов')
    if avg_fn('time_score') >= 80:
        strengths.append('Совпадение рабочих часов и хронотипов')
    if avg_fn('compatibility_score') >= 80:
        strengths.append('Высокая взаимная совместимость членов команды')
    return strengths


def _build_risks(selected: list[CandidateScores], missing: list[str]) -> list[str]:
    risks = []
    if missing:
        risks.append(f'Отсутствие обязательных навыков: {", ".join(missing)}')
    overloaded = [s.full_name for s in selected if s.workload_score < 40]
    if overloaded:
        risks.append(f'Высокая нагрузка у: {", ".join(overloaded)}')
    low_avail = [s.full_name for s in selected if s.availability_score < 70]
    if low_avail:
        risks.append(f'Частичная недоступность у: {", ".join(low_avail)}')
    return risks
