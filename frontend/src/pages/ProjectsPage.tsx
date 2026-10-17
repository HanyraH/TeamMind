import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Briefcase,
  Plus,
  Calendar,
  Clock,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  X,
  Target,
  ListTodo,
} from 'lucide-react';
import { ProjectsAPI, EmployeesAPI } from '../api/client';

export const ProjectsPage: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<any[]>([]);
  const [skills, setSkills] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Create Project Modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [priority, setPriority] = useState('medium');
  const [plannedHours, setPlannedHours] = useState('320');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const [projData, skillsData] = await Promise.all([
        ProjectsAPI.list(),
        EmployeesAPI.skills(),
      ]);
      setProjects(projData);
      setSkills(skillsData);
    } catch (err) {
      console.error('Failed to load projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !startDate || !endDate) return;

    try {
      setSubmitting(true);
      const newProj = await ProjectsAPI.create({
        name,
        description,
        start_date: startDate,
        end_date: endDate,
        priority,
        planned_hours: parseInt(plannedHours) || 300,
        status: 'planning',
      });

      setShowCreateModal(false);
      setName('');
      setDescription('');
      setStartDate('');
      setEndDate('');
      loadProjects();

      // Navigate to team builder with new project
      navigate(`/team-builder?projectId=${newProj.id}`);
    } catch (err) {
      console.error('Failed to create project:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const PRIORITY_MAP: Record<string, { label: string; color: string }> = {
    low: { label: 'Низкий', color: 'badge-info' },
    medium: { label: 'Средний', color: 'badge-warning' },
    high: { label: 'Высокий', color: 'badge-danger' },
    critical: { label: 'Критический', color: 'badge-danger' },
  };

  const STATUS_MAP: Record<string, { label: string; color: string }> = {
    planning: { label: 'Планирование', color: 'badge-warning' },
    active: { label: 'В работе', color: 'badge-success' },
    completed: { label: 'Завершен', color: 'badge-info' },
    on_hold: { label: 'Приостановлен', color: 'badge-danger' },
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="title-lg">Проекты и проектные требования</h1>
          <p className="text-muted" style={{ marginTop: '4px', fontSize: '14px' }}>
            Управление проектными требованиями к навыкам, трудоемкости и составам команд
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus size={16} />
          <span>Новый проект</span>
        </button>
      </div>

      {/* Projects List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Загрузка проектов...
        </div>
      ) : projects.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '48px' }}>
          <p className="text-muted">Проекты пока не созданы. Создайте первый проект!</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {projects.map((proj) => {
            const prio = PRIORITY_MAP[proj.priority] || { label: proj.priority, color: 'badge-info' };
            const stat = STATUS_MAP[proj.status] || { label: proj.status, color: 'badge-info' };

            return (
              <div key={proj.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {/* Project Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#ffffff' }}>{proj.name}</h2>
                      <span className={`badge ${stat.color}`}>{stat.label}</span>
                      <span className={`badge ${prio.color}`}>Приоритет: {prio.label}</span>
                    </div>
                    {proj.description && (
                      <p style={{ fontSize: '14px', color: 'var(--text-muted)', marginTop: '6px', maxWidth: '800px', lineHeight: '1.5' }}>
                        {proj.description}
                      </p>
                    )}
                  </div>

                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => navigate(`/team-builder?projectId=${proj.id}`)}
                    >
                      <Sparkles size={14} />
                      <span>Конструктор команды</span>
                    </button>
                  </div>
                </div>

                {/* Timeline and Metrics */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '24px', padding: '12px 16px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', fontSize: '13px', color: 'var(--text-dim)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Calendar size={14} color="var(--primary-light)" />
                    Сроки: <strong style={{ color: 'var(--text-main)' }}>{proj.start_date}</strong> — <strong style={{ color: 'var(--text-main)' }}>{proj.end_date}</strong>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Clock size={14} color="var(--warning)" />
                    Плановая трудоемкость: <strong style={{ color: 'var(--text-main)' }}>{proj.planned_hours || 320} часов</strong>
                  </div>
                </div>

                {/* Skill Requirements */}
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.04em', marginBottom: '8px' }}>
                    Требования к компетенциям команды:
                  </div>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {(proj.skill_requirements || []).length === 0 ? (
                      <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                        Требования к навыкам формируются автоматически при запуске подбора
                      </span>
                    ) : (
                      proj.skill_requirements.map((req: any) => (
                        <div
                          key={req.id}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '4px 10px',
                            backgroundColor: 'var(--bg-surface-elevated)',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '12px',
                          }}
                        >
                          <span style={{ fontWeight: 600, color: '#f8fafc' }}>{req.skill?.name || req.skill_name}</span>
                          <span style={{ color: 'var(--primary-light)', fontFamily: 'var(--font-mono)' }}>мин. L{req.min_level}</span>
                          {req.is_mandatory && (
                            <span style={{ color: '#f87171', fontWeight: 700 }} title="Обязательный навык">*</span>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 className="title-md">Создание нового проекта</h2>
              <button onClick={() => setShowCreateModal(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateProject} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#cbd5e1' }}>
                  Название проекта *
                </label>
                <input
                  type="text"
                  required
                  className="input-field"
                  placeholder="Например: Модернизация платежного шлюза"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#cbd5e1' }}>
                  Описание и цели проекта
                </label>
                <textarea
                  className="input-field"
                  rows={3}
                  placeholder="Опишите задачи, стек и цели команды..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#cbd5e1' }}>
                    Дата начала *
                  </label>
                  <input
                    type="date"
                    required
                    className="input-field"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#cbd5e1' }}>
                    Дата завершения *
                  </label>
                  <input
                    type="date"
                    required
                    className="input-field"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#cbd5e1' }}>
                    Приоритет
                  </label>
                  <select
                    className="select-field"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                  >
                    <option value="low">Низкий</option>
                    <option value="medium">Средний</option>
                    <option value="high">Высокий</option>
                    <option value="critical">Критический</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#cbd5e1' }}>
                    Плановые часы
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    value={plannedHours}
                    onChange={(e) => setPlannedHours(e.target.value)}
                  />
                </div>
              </div>

              <div style={{ padding: '16px 0 0', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn-primary"
                >
                  {submitting ? 'Создание...' : 'Создать проект'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
