import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Briefcase,
  Calendar,
  Activity,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Clock,
  TrendingUp,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { AnalyticsAPI } from '../api/client';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [noTeamProjects, setNoTeamProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const [dashData, noTeamData] = await Promise.all([
        AnalyticsAPI.dashboard(),
        AnalyticsAPI.projectsWithoutTeam(),
      ]);
      setStats(dashData);
      setNoTeamProjects(noTeamData.projects || []);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const CHRONO_COLORS: Record<string, string> = {
    lark: '#f59e0b',
    owl: '#6366f1',
    intermediate: '#10b981',
  };

  const CHRONO_LABELS: Record<string, string> = {
    lark: 'Жаворонок (раннее утро)',
    owl: 'Сова (вечерний тип)',
    intermediate: 'Промежуточный тип',
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <div style={{ color: 'var(--primary-light)', fontSize: '16px', fontWeight: 500 }}>
          Загрузка аналитики...
        </div>
      </div>
    );
  }

  const chronotypeData = (stats?.chronotype_distribution || []).map((item: any) => ({
    name: CHRONO_LABELS[item.chronotype] || item.chronotype,
    value: item.count,
    color: CHRONO_COLORS[item.chronotype] || '#a855f7',
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Title & Quick Action */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="title-lg">Главная аналитическая панель</h1>
          <p className="text-muted" style={{ marginTop: '4px', fontSize: '14px' }}>
            Обзор загрузки ресурсов, доступности специалистов и текущих проектных команд
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/team-builder')}
        >
          <Sparkles size={16} />
          <span>Сформировать команду</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        <div className="glass-card stat-card">
          <div className="stat-icon-wrapper" style={{ backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
            <Users size={26} />
          </div>
          <div>
            <div className="stat-value">{stats?.employees?.total || 0}</div>
            <div className="stat-label">Сотрудников ({stats?.employees?.active || 0} активных)</div>
          </div>
        </div>

        <div className="glass-card stat-card">
          <div className="stat-icon-wrapper" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
            <Briefcase size={26} />
          </div>
          <div>
            <div className="stat-value">{stats?.projects?.active || 0}</div>
            <div className="stat-label">Активных проектов (из {stats?.projects?.total || 0})</div>
          </div>
        </div>

        <div className="glass-card stat-card">
          <div className="stat-icon-wrapper" style={{ backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            <Calendar size={26} />
          </div>
          <div>
            <div className="stat-value">{stats?.vacations?.pending || 0}</div>
            <div className="stat-label">Заявок на отпуск на рассмотрении</div>
          </div>
        </div>

        <div className="glass-card stat-card">
          <div className="stat-icon-wrapper" style={{ backgroundColor: 'rgba(6, 182, 212, 0.15)', color: '#38bdf8' }}>
            <Activity size={26} />
          </div>
          <div>
            <div className="stat-value">
              {stats?.avg_utilization_pct !== undefined ? `${stats.avg_utilization_pct}%` : '0%'}
            </div>
            <div className="stat-label">Средняя утилизация мощностей</div>
          </div>
        </div>
      </div>

      {/* Warning Banner: Projects Without Teams */}
      {noTeamProjects.length > 0 && (
        <div style={{
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: 'var(--radius-lg)',
          padding: '20px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '50%',
              backgroundColor: 'rgba(245, 158, 11, 0.18)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fbbf24',
            }}>
              <AlertTriangle size={22} />
            </div>
            <div>
              <div style={{ fontSize: '15px', fontWeight: 600, color: '#fef08a' }}>
                Внимание: {noTeamProjects.length} проект(ов) ожидают назначения команды!
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px' }}>
                {noTeamProjects.map((p) => p.name).join(' • ')}
              </div>
            </div>
          </div>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => navigate('/team-builder')}
            style={{ borderColor: 'rgba(245, 158, 11, 0.4)', color: '#fbbf24' }}
          >
            <span>Подобрать состав</span>
            <ArrowRight size={14} />
          </button>
        </div>
      )}

      {/* Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '24px' }}>
        {/* Department Workload Bar Chart */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h2 className="title-md">Загрузка по отделам</h2>
              <div className="text-muted" style={{ fontSize: '13px' }}>Средний процент занятости рабочего времени</div>
            </div>
            <TrendingUp size={18} color="var(--primary-light)" />
          </div>

          <div style={{ height: '280px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.department_workloads || []} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="department" stroke="#64748b" fontSize={11} interval={0} angle={-15} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                  formatter={(val: any) => [`${val}%`, 'Загрузка']}
                />
                <Bar dataKey="utilization_pct" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chronotype Distribution */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h2 className="title-md">Распределение по хронотипам</h2>
              <div className="text-muted" style={{ fontSize: '13px' }}>Учет рабочих биоритмов и предпочтений встреч</div>
            </div>
            <Clock size={18} color="var(--secondary)" />
          </div>

          <div style={{ height: '280px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chronotypeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={95}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {chronotypeData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                />
                <Legend
                  verticalAlign="bottom"
                  formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: '12px' }}>{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Overloaded Employees & Recommendations */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h2 className="title-md">Сотрудники с высокой нагрузкой (&gt;85%)</h2>
            <div className="text-muted" style={{ fontSize: '13px' }}>
              Кандидаты, требующие разгрузки перед назначением на новые проекты
            </div>
          </div>
          <span className="badge badge-warning">
            {stats?.overloaded_employees?.length || 0} специалистов
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Сотрудник</th>
                <th>Текущая утилизация</th>
                <th>Шкала загрузки</th>
                <th>Статус риска</th>
              </tr>
            </thead>
            <tbody>
              {(stats?.overloaded_employees || []).length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                    Перегруженных специалистов не выявлено — баланс нагрузки в норме!
                  </td>
                </tr>
              ) : (
                stats.overloaded_employees.map((emp: any, idx: number) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600 }}>{emp.name}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#f87171' }}>
                      {emp.utilization_pct}%
                    </td>
                    <td style={{ width: '220px' }}>
                      <div className="progress-track">
                        <div
                          className="progress-fill"
                          style={{
                            width: `${Math.min(emp.utilization_pct, 100)}%`,
                            backgroundColor: emp.utilization_pct > 100 ? '#ef4444' : '#f59e0b',
                          }}
                        />
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-danger">Высокий риск выгорания</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
