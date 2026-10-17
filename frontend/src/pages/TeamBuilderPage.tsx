import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Sparkles,
  ShieldCheck,
  Check,
  AlertTriangle,
  Users,
  Clock,
  Briefcase,
  Layers,
  ArrowRight,
  UserPlus,
  Trash2,
  TrendingUp,
  Cpu,
  BarChart3,
  Calendar,
} from 'lucide-react';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip,
} from 'recharts';
import { ProjectsAPI, TeamsAPI, EmployeesAPI } from '../api/client';

export const TeamBuilderPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialProjectId = searchParams.get('projectId');

  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | ''>(
    initialProjectId ? parseInt(initialProjectId) : ''
  );
  const [teamSize, setTeamSize] = useState<number>(5);

  // Generation status
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeRunId, setActiveRunId] = useState<number | null>(null);
  const [variants, setVariants] = useState<any[]>([]);
  const [selectedVariantIndex, setSelectedVariantIndex] = useState<number>(0);

  // Manual editing
  const [showAddMember, setShowAddMember] = useState(false);
  const [allEmployees, setAllEmployees] = useState<any[]>([]);
  const [selectedAddEmployeeId, setSelectedAddEmployeeId] = useState<number | ''>('');
  const [addMemberRole, setAddMemberRole] = useState('');

  useEffect(() => {
    loadProjectsAndEmployees();
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      loadTeamsForProject(selectedProjectId);
    }
  }, [selectedProjectId]);

  const loadProjectsAndEmployees = async () => {
    try {
      const [projData, empData] = await Promise.all([
        ProjectsAPI.list(),
        EmployeesAPI.list(),
      ]);
      setProjects(projData);
      setAllEmployees(empData);
      if (!selectedProjectId && projData.length > 0) {
        setSelectedProjectId(projData[0].id);
      }
    } catch (err) {
      console.error('Failed to load projects/employees:', err);
    }
  };

  const loadTeamsForProject = async (projId: number) => {
    try {
      const teams = await TeamsAPI.list({ project: projId });
      setVariants(teams);
      setSelectedVariantIndex(0);
    } catch (err) {
      console.error('Failed to load teams:', err);
    }
  };

  const handleStartGeneration = async () => {
    if (!selectedProjectId) return;

    try {
      setIsGenerating(true);
      const res = await TeamsAPI.generate(selectedProjectId, teamSize);
      setActiveRunId(res.run_id);

      // Poll status every 1 second
      const pollInterval = setInterval(async () => {
        try {
          const runStatus = await TeamsAPI.getRunStatus(res.run_id);
          if (runStatus.status === 'succeeded') {
            clearInterval(pollInterval);
            setIsGenerating(false);
            loadTeamsForProject(selectedProjectId);
          } else if (runStatus.status === 'failed') {
            clearInterval(pollInterval);
            setIsGenerating(false);
            alert(`Ошибка генерации: ${runStatus.error_message}`);
          }
        } catch {
          clearInterval(pollInterval);
          setIsGenerating(false);
        }
      }, 1000);
    } catch (err) {
      console.error('Failed to start team generation:', err);
      setIsGenerating(false);
    }
  };

  const handleApproveTeam = async (teamId: number) => {
    try {
      await TeamsAPI.approve(teamId);
      if (selectedProjectId) {
        loadTeamsForProject(selectedProjectId);
      }
    } catch (err) {
      console.error('Failed to approve team:', err);
    }
  };

  const handleRemoveMember = async (teamId: number, memberId: number) => {
    try {
      await TeamsAPI.removeMember(teamId, memberId);
      if (selectedProjectId) {
        loadTeamsForProject(selectedProjectId);
      }
    } catch (err) {
      console.error('Failed to remove member:', err);
    }
  };

  const handleAddMember = async () => {
    if (!selectedAddEmployeeId || !currentTeam) return;
    try {
      await TeamsAPI.addMember(currentTeam.id, Number(selectedAddEmployeeId), addMemberRole);
      setShowAddMember(false);
      setSelectedAddEmployeeId('');
      setAddMemberRole('');
      if (selectedProjectId) {
        loadTeamsForProject(selectedProjectId);
      }
    } catch (err) {
      console.error('Failed to add member:', err);
    }
  };

  const currentProject = projects.find((p) => p.id === selectedProjectId);
  const currentTeam = variants[selectedVariantIndex];

  // Radar chart data for criteria comparison
  const radarData = [
    {
      subject: 'Навыки (35%)',
      fullMark: 100,
      ...(variants.reduce((acc, v, idx) => {
        acc[`variant_${idx}`] = parseFloat(v.skill_score) || 0;
        return acc;
      }, {} as any)),
    },
    {
      subject: 'Доступность (25%)',
      fullMark: 100,
      ...(variants.reduce((acc, v, idx) => {
        acc[`variant_${idx}`] = parseFloat(v.availability_score) || 0;
        return acc;
      }, {} as any)),
    },
    {
      subject: 'Баланс нагрузки (20%)',
      fullMark: 100,
      ...(variants.reduce((acc, v, idx) => {
        acc[`variant_${idx}`] = parseFloat(v.workload_score) || 0;
        return acc;
      }, {} as any)),
    },
    {
      subject: 'Расписания (10%)',
      fullMark: 100,
      ...(variants.reduce((acc, v, idx) => {
        acc[`variant_${idx}`] = parseFloat(v.time_score) || 0;
        return acc;
      }, {} as any)),
    },
    {
      subject: 'Совместимость (10%)',
      fullMark: 100,
      ...(variants.reduce((acc, v, idx) => {
        acc[`variant_${idx}`] = parseFloat(v.compatibility_score) || 0;
        return acc;
      }, {} as any)),
    },
  ];

  const RADAR_COLORS = ['#6366f1', '#10b981', '#f59e0b'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Header */}
      <div>
        <h1 className="title-lg">Интеллектуальный конструктор команд</h1>
        <p className="text-muted" style={{ marginTop: '4px', fontSize: '14px' }}>
          Автоматический многокритериальный подбор состава на основе формулы: S = 0.35K + 0.25A + 0.20L + 0.10T + 0.10C
        </p>
      </div>

      {/* Control Panel */}
      <div className="glass-card" style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', alignItems: 'flex-end', flex: 1 }}>
          <div style={{ minWidth: '280px', flex: '1 1 300px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px', color: '#cbd5e1' }}>
              Целевой проект
            </label>
            <select
              className="select-field"
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(Number(e.target.value))}
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.start_date} — {p.end_date})
                </option>
              ))}
            </select>
          </div>

          <div style={{ width: '180px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px', color: '#cbd5e1' }}>
              Размер команды: <strong style={{ color: 'var(--primary-light)' }}>{teamSize} чел.</strong>
            </label>
            <input
              type="range"
              min={3}
              max={8}
              value={teamSize}
              onChange={(e) => setTeamSize(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--primary)' }}
            />
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleStartGeneration}
          disabled={isGenerating || !selectedProjectId}
          style={{ minWidth: '220px' }}
        >
          {isGenerating ? (
            <>
              <div style={{ width: '16px', height: '16px', border: '2px solid #ffffff', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
              <span>Анализ и расчет...</span>
            </>
          ) : (
            <>
              <Sparkles size={16} />
              <span>Подобрать варианты</span>
            </>
          )}
        </button>
      </div>

      {/* Variants Selection Tabs */}
      {variants.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {variants.map((v, idx) => {
            const isSelected = selectedVariantIndex === idx;
            const isApproved = v.approval_status === 'approved';

            return (
              <div
                key={v.id}
                onClick={() => setSelectedVariantIndex(idx)}
                className={`glass-card ${isSelected ? '' : 'glass-card-hover'}`}
                style={{
                  cursor: 'pointer',
                  border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                  boxShadow: isSelected ? '0 0 20px rgba(99, 102, 241, 0.3)' : undefined,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                  position: 'relative',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>
                      Вариант #{idx + 1}
                    </span>
                    <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#ffffff', marginTop: '2px' }}>
                      {v.variant_name}
                    </h3>
                  </div>
                  {isApproved ? (
                    <span className="badge badge-success">
                      <Check size={12} /> Утвержден
                    </span>
                  ) : (
                    <span className="badge badge-warning">Черновик</span>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                  <div style={{ fontSize: '32px', fontFamily: 'var(--font-display)', fontWeight: 800, color: 'var(--primary-light)' }}>
                    {v.total_score}
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>из 100 баллов</div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-dim)', borderTop: '1px solid var(--border-subtle)', paddingTop: '10px' }}>
                  <span>Покрытие навыков: <strong style={{ color: '#ffffff' }}>{v.skill_coverage_pct}%</strong></span>
                  <span>Участников: <strong style={{ color: '#ffffff' }}>{(v.members || []).length}</strong></span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Selected Variant Detail */}
      {currentTeam && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '24px' }}>
          {/* Radar Chart Criteria Comparison */}
          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h2 className="title-md">Сравнение критериев оценки</h2>
                <div className="text-muted" style={{ fontSize: '13px' }}>
                  Баланс навыков, отсутствия отпусков, нагрузки и совместимости
                </div>
              </div>
              <BarChart3 size={18} color="var(--primary-light)" />
            </div>

            <div style={{ height: '340px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.1)" />
                  <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={12} />
                  <PolarRadiusAxis domain={[0, 100]} stroke="#64748b" />
                  {variants.map((v, idx) => (
                    <Radar
                      key={v.id}
                      name={v.variant_name}
                      dataKey={`variant_${idx}`}
                      stroke={RADAR_COLORS[idx % RADAR_COLORS.length]}
                      fill={RADAR_COLORS[idx % RADAR_COLORS.length]}
                      fillOpacity={selectedVariantIndex === idx ? 0.45 : 0.1}
                    />
                  ))}
                  <Legend />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Explanation, Strengths & Risks */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 className="title-md">Обоснование состава алгоритмом</h2>
                <div className="text-muted" style={{ fontSize: '13px' }}>
                  Анализ сильных сторон, ограничений и проектных рисков
                </div>
              </div>
              {currentTeam.approval_status !== 'approved' && (
                <button
                  className="btn btn-success btn-sm"
                  onClick={() => handleApproveTeam(currentTeam.id)}
                >
                  <ShieldCheck size={15} />
                  <span>Утвердить состав</span>
                </button>
              )}
            </div>

            {/* Strengths */}
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#34d399', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <Check size={15} />
                Сильные стороны варианта:
              </div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {(currentTeam.explanation?.strengths || [
                  '100% покрытие ключевых требований по технологическому стеку',
                  'Отсутствие пересечений с запланированными отпусками кандидатов',
                  'Высокий коэффициент совпадения рабочих интервалов'
                ]).map((str: string, i: number) => (
                  <li key={i} style={{ fontSize: '13px', color: '#cbd5e1', paddingLeft: '18px', position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0, color: '#34d399' }}>•</span>
                    {str}
                  </li>
                ))}
              </ul>
            </div>

            {/* Risks */}
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <AlertTriangle size={15} />
                Потенциальные риски:
              </div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {(currentTeam.explanation?.risks || [
                  'Один из участников имеет текущую нагрузку на уровне 75%',
                  'Разные предпочтения по хронотипу (жаворонок / сова)'
                ]).map((risk: string, i: number) => (
                  <li key={i} style={{ fontSize: '13px', color: '#cbd5e1', paddingLeft: '18px', position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0, color: '#fbbf24' }}>•</span>
                    {risk}
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommendations */}
            <div style={{ backgroundColor: 'rgba(99, 102, 241, 0.08)', padding: '12px 16px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--primary-light)', marginBottom: '4px' }}>
                Рекомендация руководителя:
              </div>
              <div style={{ fontSize: '13px', color: '#cbd5e1' }}>
                {(currentTeam.explanation?.recommendations || [
                  'Установить общее окно для командных синхронизаций с 13:00 до 16:00'
                ])[0]}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Team Members Table with Manual Editing */}
      {currentTeam && (
        <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
          <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 className="title-md">Состав команды: {currentTeam.variant_name}</h2>
              <div className="text-muted" style={{ fontSize: '13px' }}>
                Назначенные специалисты, их роли и вклад в баллы команды
              </div>
            </div>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setShowAddMember(true)}
            >
              <UserPlus size={14} />
              <span>Добавить участника</span>
            </button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Сотрудник</th>
                  <th>Роль в команде</th>
                  <th>Отдел</th>
                  <th>Хронотип</th>
                  <th>Индивидуальный балл</th>
                  <th>Причина назначения</th>
                  <th style={{ textAlign: 'right' }}>Действия</th>
                </tr>
              </thead>
              <tbody>
                {(currentTeam.members || []).map((m: any) => {
                  const emp = m.employee;
                  return (
                    <tr key={m.id}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{emp?.user?.first_name} {emp?.user?.last_name}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>{emp?.user?.email}</div>
                      </td>
                      <td>
                        <span className="badge badge-purple">{m.role_in_team || 'Разработчик'}</span>
                      </td>
                      <td>{emp?.department?.name || '—'}</td>
                      <td>
                        <span className="badge badge-info">{emp?.chronotype || 'intermediate'}</span>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--primary-light)' }}>
                        {m.contribution_score}
                      </td>
                      <td style={{ fontSize: '13px', color: 'var(--text-muted)', maxWidth: '300px' }}>
                        {m.reason || 'Оптимальное соответствие требованиям проекта'}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleRemoveMember(currentTeam.id, m.id)}
                          title="Исключить из состава"
                        >
                          <Trash2 size={13} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Member Modal */}
      {showAddMember && (
        <div className="modal-overlay" onClick={() => setShowAddMember(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 className="title-md">Ручное добавление специалиста в команду</h2>
              <button onClick={() => setShowAddMember(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                ✕
              </button>
            </div>

            <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Выберите сотрудника
                </label>
                <select
                  className="select-field"
                  value={selectedAddEmployeeId}
                  onChange={(e) => setSelectedAddEmployeeId(Number(e.target.value))}
                >
                  <option value="">-- Выберите специалиста из базы --</option>
                  {allEmployees.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.user?.first_name} {e.user?.last_name} — {e.position?.name} ({e.department?.name})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Роль в команде
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Например: Lead Frontend Архитектор"
                  value={addMemberRole}
                  onChange={(e) => setAddMemberRole(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '12px' }}>
                <button className="btn btn-secondary" onClick={() => setShowAddMember(false)}>
                  Отмена
                </button>
                <button
                  className="btn btn-primary"
                  onClick={handleAddMember}
                  disabled={!selectedAddEmployeeId}
                >
                  Добавить в команду
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
