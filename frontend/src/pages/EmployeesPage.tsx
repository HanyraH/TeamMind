import React, { useEffect, useState } from 'react';
import {
  Search,
  Filter,
  User,
  Clock,
  Briefcase,
  ChevronRight,
  Layers,
  LayoutGrid,
  Table as TableIcon,
  X,
  Star,
  Calendar,
} from 'lucide-react';
import { EmployeesAPI } from '../api/client';

export const EmployeesPage: React.FC = () => {
  const [employees, setEmployees] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('');
  const [selectedChrono, setSelectedChrono] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('table');

  // Modal detail
  const [selectedEmployee, setSelectedEmployee] = useState<any | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [empData, deptData] = await Promise.all([
        EmployeesAPI.list(),
        EmployeesAPI.departments(),
      ]);
      setEmployees(empData);
      setDepartments(deptData);
    } catch (err) {
      console.error('Failed to load employees:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredEmployees = employees.filter((emp) => {
    const fullName = (emp.full_name || `${emp.user?.first_name || ''} ${emp.user?.last_name || ''}`).toLowerCase();
    const pos = (emp.position?.name || emp.position_name || '').toLowerCase();
    const dept = emp.department?.name || emp.department_name || '';
    const q = search.toLowerCase();

    if (q && !fullName.includes(q) && !pos.includes(q)) return false;
    if (selectedDept && dept !== selectedDept) return false;
    if (selectedChrono && emp.chronotype !== selectedChrono) return false;
    if (selectedFormat && emp.work_format !== selectedFormat) return false;
    return true;
  });

  const CHRONO_MAP: Record<string, { label: string; color: string }> = {
    lark: { label: 'Жаворонок', color: 'badge-warning' },
    owl: { label: 'Сова', color: 'badge-purple' },
    intermediate: { label: 'Промежуточный', color: 'badge-info' },
  };

  const FORMAT_MAP: Record<string, string> = {
    remote: 'Удаленно',
    office: 'Офис',
    hybrid: 'Гибрид',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="title-lg">Каталог сотрудников</h1>
          <p className="text-muted" style={{ marginTop: '4px', fontSize: '14px' }}>
            Всего в базе {employees.length} специалистов с профилями компетенций и предпочтений
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px', backgroundColor: 'var(--bg-surface)', padding: '4px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => setViewMode('table')}
            style={{
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: viewMode === 'table' ? 'var(--primary)' : 'transparent',
              color: viewMode === 'table' ? '#fff' : 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '13px',
            }}
          >
            <TableIcon size={14} />
            <span>Таблица</span>
          </button>
          <button
            onClick={() => setViewMode('grid')}
            style={{
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: viewMode === 'grid' ? 'var(--primary)' : 'transparent',
              color: viewMode === 'grid' ? '#fff' : 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '13px',
            }}
          >
            <LayoutGrid size={14} />
            <span>Карточки</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-card" style={{ padding: '16px 20px', display: 'flex', flexWrap: 'wrap', gap: '14px', alignItems: 'center' }}>
        <div style={{ flex: '1 1 260px', position: 'relative' }}>
          <Search size={16} color="var(--text-dim)" style={{ position: 'absolute', left: '12px', top: '12px' }} />
          <input
            type="text"
            className="input-field"
            placeholder="Поиск по ФИО, должности или навыку..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ paddingLeft: '38px' }}
          />
        </div>

        <select
          className="select-field"
          value={selectedDept}
          onChange={(e) => setSelectedDept(e.target.value)}
          style={{ width: '200px' }}
        >
          <option value="">Все отделы</option>
          {departments.map((d) => (
            <option key={d.id} value={d.name}>{d.name}</option>
          ))}
        </select>

        <select
          className="select-field"
          value={selectedChrono}
          onChange={(e) => setSelectedChrono(e.target.value)}
          style={{ width: '170px' }}
        >
          <option value="">Все хронотипы</option>
          <option value="lark">Жаворонок</option>
          <option value="owl">Сова</option>
          <option value="intermediate">Промежуточный</option>
        </select>

        <select
          className="select-field"
          value={selectedFormat}
          onChange={(e) => setSelectedFormat(e.target.value)}
          style={{ width: '160px' }}
        >
          <option value="">Любой формат</option>
          <option value="remote">Удаленно</option>
          <option value="office">Офис</option>
          <option value="hybrid">Гибрид</option>
        </select>

        {(search || selectedDept || selectedChrono || selectedFormat) && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => {
              setSearch('');
              setSelectedDept('');
              setSelectedChrono('');
              setSelectedFormat('');
            }}
          >
            Сбросить
          </button>
        )}
      </div>

      {/* Employees Content */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Загрузка базы специалистов...
        </div>
      ) : filteredEmployees.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '48px' }}>
          <p className="text-muted">По вашему запросу не найдено ни одного сотрудника</p>
        </div>
      ) : viewMode === 'table' ? (
        /* TABLE VIEW */
        <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Сотрудник</th>
                  <th>Отдел и должность</th>
                  <th>Хронотип</th>
                  <th>Формат</th>
                  <th>Ставка</th>
                  <th>Ключевые навыки</th>
                  <th style={{ textAlign: 'right' }}>Действие</th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.slice(0, 50).map((emp) => {
                  const chrono = CHRONO_MAP[emp.chronotype] || { label: emp.chronotype, color: 'badge-info' };
                  const firstName = emp.user?.first_name || (emp.full_name ? emp.full_name.split(' ')[0] : '');
                  const lastName = emp.user?.last_name || (emp.full_name ? emp.full_name.split(' ').slice(1).join(' ') : '');
                  const fullName = (emp.full_name || `${firstName} ${lastName}`).trim() || 'Сотрудник';
                  const email = emp.email || emp.user?.email || '';
                  const posName = emp.position?.name || emp.position_name || '—';
                  const deptName = emp.department?.name || emp.department_name || '—';
                  const skillsList = emp.skills && emp.skills.length > 0 ? emp.skills : (emp.primary_skills || []);

                  return (
                    <tr
                      key={emp.id}
                      onClick={() => setSelectedEmployee(emp)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <div style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: '50%',
                            backgroundColor: 'var(--bg-surface-elevated)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '12px',
                            fontWeight: 600,
                            color: 'var(--primary-light)',
                          }}>
                            {firstName?.[0] || 'E'}
                          </div>
                          <div>
                            <div style={{ fontWeight: 600 }}>{fullName}</div>
                            <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>{email}</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: '13px', fontWeight: 500 }}>{posName}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{deptName}</div>
                      </td>
                      <td>
                        <span className={`badge ${chrono.color}`}>{chrono.label}</span>
                      </td>
                      <td>
                        <span style={{ fontSize: '13px' }}>{FORMAT_MAP[emp.work_format] || emp.work_format}</span>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '13px' }}>
                        {emp.weekly_hours} ч/нед
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', maxWidth: '260px' }}>
                          {skillsList.slice(0, 3).map((s: any, idx: number) => (
                            <span
                              key={s.id || idx}
                              style={{
                                fontSize: '11px',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                                border: '1px solid var(--border-subtle)',
                                color: '#cbd5e1',
                              }}
                            >
                              {s.skill?.name || s.name || s.skill_name} L{s.level}
                            </span>
                          ))}
                          {skillsList.length > 3 && (
                            <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                              +{skillsList.length - 3}
                            </span>
                          )}
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedEmployee(emp);
                          }}
                        >
                          <span>Карточка</span>
                          <ChevronRight size={14} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {filteredEmployees.length > 50 && (
            <div style={{ padding: '12px 20px', borderTop: '1px solid var(--border-subtle)', textAlign: 'center', fontSize: '13px', color: 'var(--text-muted)' }}>
              Показано первых 50 специалистов из {filteredEmployees.length}. Используйте поиск и фильтры для точной выборки.
            </div>
          )}
        </div>
      ) : (
        /* GRID VIEW */
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
          {filteredEmployees.slice(0, 30).map((emp) => {
            const chrono = CHRONO_MAP[emp.chronotype] || { label: emp.chronotype, color: 'badge-info' };
            const firstName = emp.user?.first_name || (emp.full_name ? emp.full_name.split(' ')[0] : '');
            const lastName = emp.user?.last_name || (emp.full_name ? emp.full_name.split(' ').slice(1).join(' ') : '');
            const fullName = (emp.full_name || `${firstName} ${lastName}`).trim() || 'Сотрудник';
            const posName = emp.position?.name || emp.position_name || '—';
            const deptName = emp.department?.name || emp.department_name || '—';
            const skillsList = emp.skills && emp.skills.length > 0 ? emp.skills : (emp.primary_skills || []);

            return (
              <div
                key={emp.id}
                className="glass-card glass-card-hover"
                onClick={() => setSelectedEmployee(emp)}
                style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '14px' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      width: '42px',
                      height: '42px',
                      borderRadius: '50%',
                      backgroundColor: 'rgba(99, 102, 241, 0.15)',
                      color: '#818cf8',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 700,
                    }}>
                      {firstName?.[0] || 'E'}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '15px' }}>{fullName}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{posName}</div>
                    </div>
                  </div>
                  <span className={`badge ${chrono.color}`}>{chrono.label}</span>
                </div>

                <div style={{ fontSize: '12px', color: 'var(--text-dim)', borderTop: '1px solid var(--border-subtle)', paddingTop: '10px' }}>
                  Отдел: <strong style={{ color: 'var(--text-main)' }}>{deptName}</strong> • Ставка: {emp.weekly_hours}ч
                </div>

                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {skillsList.slice(0, 4).map((s: any, idx: number) => (
                    <span
                      key={s.id || idx}
                      style={{
                        fontSize: '11px',
                        padding: '3px 8px',
                        borderRadius: '6px',
                        backgroundColor: 'rgba(99, 102, 241, 0.08)',
                        border: '1px solid rgba(99, 102, 241, 0.2)',
                        color: '#cbd5e1',
                      }}
                    >
                      {s.skill?.name || s.name || s.skill_name} <strong style={{ color: '#818cf8' }}>L{s.level}</strong>
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Employee Detail Modal */}
      {selectedEmployee && (
        <div className="modal-overlay" onClick={() => setSelectedEmployee(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            {/* Modal Header */}
            <div style={{ padding: '24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                <div style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  fontSize: '20px',
                  fontWeight: 700,
                  boxShadow: '0 4px 16px rgba(99, 102, 241, 0.3)'
                }}>
                  {(selectedEmployee.user?.first_name?.[0] || selectedEmployee.full_name?.[0] || 'E')}
                </div>
                <div>
                  <h2 className="title-md">
                    {selectedEmployee.full_name || `${selectedEmployee.user?.first_name || ''} ${selectedEmployee.user?.last_name || ''}`.trim() || 'Сотрудник'}
                  </h2>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {selectedEmployee.position?.name || selectedEmployee.position_name || '—'} • {selectedEmployee.department?.name || selectedEmployee.department_name || '—'}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setSelectedEmployee(null)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '4px' }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Bio */}
              {selectedEmployee.bio && (
                <div style={{ fontSize: '14px', color: '#cbd5e1', backgroundColor: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: 'var(--radius-md)' }}>
                  {selectedEmployee.bio}
                </div>
              )}

              {/* Working hours & Chronotype */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div style={{ backgroundColor: 'var(--bg-surface-elevated)', padding: '14px', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginBottom: '4px' }}>Рабочий интервал</div>
                  <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Clock size={15} color="var(--primary-light)" />
                    {selectedEmployee.preferred_work_start || '09:00'} — {selectedEmployee.preferred_work_end || '18:00'}
                  </div>
                </div>

                <div style={{ backgroundColor: 'var(--bg-surface-elevated)', padding: '14px', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginBottom: '4px' }}>Окно для встреч и созвонов</div>
                  <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Calendar size={15} color="var(--secondary)" />
                    {selectedEmployee.preferred_meeting_start || '10:00'} — {selectedEmployee.preferred_meeting_end || '17:00'}
                  </div>
                </div>
              </div>

              {/* Skills */}
              <div>
                <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '10px', color: '#cbd5e1' }}>
                  Профессиональные навыки и компетенции
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {((selectedEmployee.skills && selectedEmployee.skills.length > 0) ? selectedEmployee.skills : (selectedEmployee.primary_skills || [])).map((s: any, idx: number) => (
                    <div
                      key={s.id || idx}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '10px 14px',
                        backgroundColor: 'var(--bg-surface-elevated)',
                        borderRadius: 'var(--radius-sm)',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 500, fontSize: '14px' }}>{s.skill?.name || s.name || s.skill_name}</span>
                        {s.is_primary && <span className="badge badge-purple" style={{ fontSize: '10px' }}>Основной</span>}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ display: 'flex', gap: '3px' }}>
                          {[1, 2, 3, 4, 5].map((levelDot) => (
                            <div
                              key={levelDot}
                              style={{
                                width: '8px',
                                height: '8px',
                                borderRadius: '50%',
                                backgroundColor: levelDot <= s.level ? 'var(--primary)' : 'rgba(255,255,255,0.1)',
                              }}
                            />
                          ))}
                        </div>
                        <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                          Уровень {s.level}/5
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Work Preferences */}
              {selectedEmployee.work_preferences && (
                <div style={{ backgroundColor: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.15)', padding: '14px', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-light)', marginBottom: '6px' }}>
                    Предпочтения командной работы
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                    Стиль общения: <strong>{selectedEmployee.work_preferences.communication_style}</strong> • 
                    Формат взаимодействия: <strong>{selectedEmployee.work_preferences.collaboration_style}</strong> • 
                    Желаемый размер команды: <strong>{selectedEmployee.work_preferences.preferred_team_size_min}–{selectedEmployee.work_preferences.preferred_team_size_max} чел.</strong>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedEmployee(null)}>
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
