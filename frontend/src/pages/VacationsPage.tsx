import React, { useEffect, useState } from 'react';
import {
  Calendar,
  CheckCircle2,
  XCircle,
  Clock,
  Plus,
  AlertTriangle,
  Filter,
  Check,
  X,
} from 'lucide-react';
import { VacationsAPI, EmployeesAPI, AuthAPI } from '../api/client';

export const VacationsPage: React.FC = () => {
  const currentUser = AuthAPI.getCurrentUser();
  const isEmployeeRole = currentUser?.role === 'employee';
  const canManage = currentUser?.role === 'admin' || currentUser?.role === 'project_manager';

  const [vacations, setVacations] = useState<any[]>([]);
  const [employees, setAllEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  // Create vacation modal
  const [showModal, setShowModal] = useState(false);
  const [employeeId, setEmployeeId] = useState<number | ''>('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [vacationType, setVacationType] = useState('annual');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadVacations();
  }, []);

  const loadVacations = async () => {
    try {
      setLoading(true);
      const [vacData, empData] = await Promise.all([
        VacationsAPI.list(),
        EmployeesAPI.list(),
      ]);
      setVacations(vacData);
      setAllEmployees(empData);
    } catch (err) {
      console.error('Failed to load vacations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await VacationsAPI.approve(id);
      loadVacations();
    } catch (err) {
      console.error('Failed to approve vacation:', err);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await VacationsAPI.reject(id);
      loadVacations();
    } catch (err) {
      console.error('Failed to reject vacation:', err);
    }
  };

  const [modalError, setModalError] = useState<string | null>(null);

  const handleCreateVacation = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalError(null);
    if (!startDate || !endDate) {
      setModalError('Пожалуйста, укажите дату начала и окончания.');
      return;
    }
    if (endDate < startDate) {
      setModalError('Дата окончания отпуска не может быть раньше даты начала.');
      return;
    }
    if (!isEmployeeRole && !employeeId) {
      setModalError('Пожалуйста, выберите сотрудника.');
      return;
    }

    try {
      setSubmitting(true);
      const payload: any = {
        start_date: startDate,
        end_date: endDate,
        vacation_type: vacationType,
        reason,
        status: 'pending',
      };
      if (employeeId) {
        payload.employee = employeeId;
      }
      await VacationsAPI.create(payload);
      setShowModal(false);
      setModalError(null);
      setEmployeeId('');
      setStartDate('');
      setEndDate('');
      setReason('');
      loadVacations();
    } catch (err: any) {
      console.error('Failed to create vacation:', err);
      const msg = err.response?.data?.detail ||
                  err.response?.data?.non_field_errors?.[0] ||
                  err.response?.data?.start_date?.[0] ||
                  err.response?.data?.end_date?.[0] ||
                  'Ошибка при сохранении заявки на отпуск.';
      setModalError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setSubmitting(false);
    }
  };

  const filteredVacations = vacations.filter((v) => {
    if (statusFilter && v.status !== statusFilter) return false;
    return true;
  });

  const STATUS_MAP: Record<string, { label: string; color: string; icon: any }> = {
    pending: { label: 'На рассмотрении', color: 'badge-warning', icon: Clock },
    approved: { label: 'Одобрен', color: 'badge-success', icon: CheckCircle2 },
    rejected: { label: 'Отклонён', color: 'badge-danger', icon: XCircle },
  };

  const TYPE_MAP: Record<string, string> = {
    annual: 'Ежегодный отпуск',
    sick: 'Больничный',
    unpaid: 'За свой счет',
    remote_work: 'Удаленный режим',
    other: 'Иное',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="title-lg">Календарь и график отпусков</h1>
          <p className="text-muted" style={{ marginTop: '4px', fontSize: '14px' }}>
            Учет периодов отсутствия специалистов для предотвращения ресурсных конфликтов в проектах
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={16} />
          <span>Подать заявку</span>
        </button>
      </div>

      {/* Info notice */}
      <div style={{
        backgroundColor: 'rgba(99, 102, 241, 0.08)',
        border: '1px solid rgba(99, 102, 241, 0.25)',
        borderRadius: 'var(--radius-md)',
        padding: '14px 18px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        fontSize: '13px',
        color: '#cbd5e1',
      }}>
        <AlertTriangle size={18} color="var(--primary-light)" />
        <span>
          <strong>Правило алгоритма подбора:</strong> Любой подтвержденный отпуск, пересекающийся со сроками проекта, автоматически исключает специалиста из числа доступных кандидатов на этот период.
        </span>
      </div>

      {/* Filters */}
      <div className="glass-card" style={{ padding: '14px 20px', display: 'flex', gap: '12px', alignItems: 'center' }}>
        <span style={{ fontSize: '13px', color: 'var(--text-dim)', fontWeight: 600 }}>Фильтр по статусу:</span>
        <div style={{ display: 'flex', gap: '6px' }}>
          {[
            { id: '', label: 'Все заявки' },
            { id: 'pending', label: 'Ожидают решения' },
            { id: 'approved', label: 'Одобренные' },
            { id: 'rejected', label: 'Отклонённые' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setStatusFilter(item.id)}
              style={{
                padding: '6px 12px',
                borderRadius: 'var(--radius-sm)',
                border: statusFilter === item.id ? '1px solid var(--border-highlight)' : '1px solid transparent',
                backgroundColor: statusFilter === item.id ? 'var(--primary)' : 'var(--bg-surface-elevated)',
                color: statusFilter === item.id ? '#ffffff' : 'var(--text-muted)',
                fontSize: '12px',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Vacations Table */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Загрузка отпусков...
        </div>
      ) : filteredVacations.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '48px' }}>
          <p className="text-muted">Записей об отпусках не найдено</p>
        </div>
      ) : (
        <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Сотрудник</th>
                  <th>Тип отсутствия</th>
                  <th>Период</th>
                  <th>Длительность</th>
                  <th>Статус</th>
                  <th>Причина / комментарий</th>
                  {canManage && <th style={{ textAlign: 'right' }}>Решение</th>}
                </tr>
              </thead>
              <tbody>
                {filteredVacations.map((v) => {
                  const stat = STATUS_MAP[v.status] || { label: v.status, color: 'badge-info', icon: Clock };
                  const Icon = stat.icon;
                  const emp = v.employee;
                  const duration = v.duration_days || Math.round((new Date(v.end_date).getTime() - new Date(v.start_date).getTime()) / (1000 * 60 * 60 * 24)) + 1;

                  return (
                    <tr key={v.id}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{emp?.user?.first_name} {emp?.user?.last_name}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>{emp?.department?.name}</div>
                      </td>
                      <td>
                        <span style={{ fontSize: '13px', fontWeight: 500 }}>{TYPE_MAP[v.vacation_type] || v.vacation_type}</span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontFamily: 'var(--font-mono)' }}>
                          <Calendar size={13} color="var(--primary-light)" />
                          {v.start_date} — {v.end_date}
                        </div>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '13px' }}>
                        {duration} дн.
                      </td>
                      <td>
                        <span className={`badge ${stat.color}`}>
                          <Icon size={12} />
                          {stat.label}
                        </span>
                      </td>
                      <td style={{ fontSize: '13px', color: 'var(--text-muted)', maxWidth: '240px' }}>
                        {v.reason || '—'}
                      </td>
                      {canManage && (
                        <td style={{ textAlign: 'right' }}>
                          {v.status === 'pending' ? (
                            <div style={{ display: 'inline-flex', gap: '6px' }}>
                              <button
                                className="btn btn-success btn-sm"
                                onClick={() => handleApprove(v.id)}
                                title="Одобрить заявку"
                              >
                                <Check size={13} />
                                <span>Одобрить</span>
                              </button>
                              <button
                                className="btn btn-danger btn-sm"
                                onClick={() => handleReject(v.id)}
                                title="Отклонить"
                              >
                                <X size={13} />
                              </button>
                            </div>
                          ) : (
                            <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Решено</span>
                          )}
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Vacation Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 className="title-md">Регистрация периода отпуска</h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateVacation} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {modalError && (
                <div style={{
                  padding: '10px 14px',
                  backgroundColor: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: 'var(--radius-sm)',
                  color: '#ef4444',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}>
                  <AlertTriangle size={16} />
                  <span>{modalError}</span>
                </div>
              )}
              {isEmployeeRole ? (
                <div style={{ padding: '12px 14px', backgroundColor: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '13px' }}>
                  <span style={{ color: 'var(--text-dim)' }}>Сотрудник: </span>
                  <strong style={{ color: '#ffffff' }}>{currentUser?.first_name} {currentUser?.last_name} ({currentUser?.email})</strong>
                </div>
              ) : (
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                    Сотрудник *
                  </label>
                  <select
                    required
                    className="select-field"
                    value={employeeId}
                    onChange={(e) => setEmployeeId(Number(e.target.value))}
                  >
                    <option value="">-- Выберите сотрудника --</option>
                    {employees.map((e) => (
                      <option key={e.id} value={e.id}>
                        {e.user?.first_name} {e.user?.last_name} ({e.department?.name})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Тип отсутствия
                </label>
                <select
                  className="select-field"
                  value={vacationType}
                  onChange={(e) => setVacationType(e.target.value)}
                >
                  <option value="annual">Ежегодный оплачиваемый отпуск</option>
                  <option value="sick">Больничный лист</option>
                  <option value="unpaid">Отпуск за свой счет</option>
                  <option value="remote_work">Удаленная работа</option>
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
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
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                    Дата окончания *
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

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Причина или комментарий
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Плановый ежегодный отдых..."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '10px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Отмена
                </button>
                <button type="submit" disabled={submitting} className="btn btn-primary">
                  {submitting ? 'Сохранение...' : 'Зарегистрировать отпуск'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
