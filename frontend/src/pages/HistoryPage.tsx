import React, { useEffect, useState } from 'react';
import { History, ShieldCheck, CheckCircle2, Clock, Calendar } from 'lucide-react';
import { TeamsAPI } from '../api/client';

export const HistoryPage: React.FC = () => {
  const [teams, setTeams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await TeamsAPI.list();
      setTeams(data);
    } catch (err) {
      console.error('Failed to load team history:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h1 className="title-lg">История и аудит формирования команд</h1>
        <p className="text-muted" style={{ marginTop: '4px', fontSize: '14px' }}>
          Архив запусков интеллектуального алгоритма, история изменений и утверждённых составов
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Загрузка журнала истории...
        </div>
      ) : teams.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '48px' }}>
          <p className="text-muted">Записей об сформированных командах пока нет</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {teams.map((t) => (
            <div key={t.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#ffffff' }}>{t.variant_name}</h2>
                    {t.approval_status === 'approved' ? (
                      <span className="badge badge-success">
                        <CheckCircle2 size={12} /> Утвержденная команда
                      </span>
                    ) : (
                      <span className="badge badge-warning">Вариант черновика</span>
                    )}
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Проект: <strong style={{ color: 'var(--text-main)' }}>{t.project?.name || `Проект #${t.project}`}</strong>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                  <div style={{ fontSize: '26px', fontFamily: 'var(--font-display)', fontWeight: 800, color: 'var(--primary-light)' }}>
                    {t.total_score}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>/ 100 баллов</div>
                </div>
              </div>

              {/* Score components breakdown */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', backgroundColor: 'rgba(255,255,255,0.02)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '12px' }}>
                <div>Навыки: <strong style={{ color: '#818cf8' }}>{t.skill_score}</strong></div>
                <div>Доступность: <strong style={{ color: '#34d399' }}>{t.availability_score}</strong></div>
                <div>Нагрузка: <strong style={{ color: '#fbbf24' }}>{t.workload_score}</strong></div>
                <div>Расписания: <strong style={{ color: '#38bdf8' }}>{t.time_score}</strong></div>
                <div>Совместимость: <strong style={{ color: '#c084fc' }}>{t.compatibility_score}</strong></div>
              </div>

              {/* Members */}
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-dim)', fontWeight: 600, marginBottom: '6px' }}>
                  Назначенные участники ({(t.members || []).length}):
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {(t.members || []).map((m: any) => (
                    <span
                      key={m.id}
                      style={{
                        padding: '3px 8px',
                        backgroundColor: 'var(--bg-surface-elevated)',
                        borderRadius: '4px',
                        fontSize: '12px',
                        border: '1px solid var(--border-subtle)',
                        color: '#cbd5e1',
                      }}
                    >
                      {m.employee?.user?.first_name} {m.employee?.user?.last_name} ({m.role_in_team || 'Специалист'})
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
