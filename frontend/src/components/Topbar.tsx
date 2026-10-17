import React from 'react';
import { User, LogOut, Shield, Briefcase, UserCheck } from 'lucide-react';
import { AuthAPI, UserInfo } from '../api/client';

interface TopbarProps {
  user: UserInfo | null;
  onRoleSwitch: (email: string) => void;
  onLogout: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ user, onRoleSwitch, onLogout }) => {
  const roles = [
    { email: 'admin@teammind.ru', label: 'Администратор', role: 'admin', icon: Shield },
    { email: 'pm@teammind.ru', label: 'Руководитель проекта', role: 'project_manager', icon: Briefcase },
    { email: 'dev@teammind.ru', label: 'Сотрудник', role: 'employee', icon: UserCheck },
  ];

  return (
    <header style={{
      height: '68px',
      borderBottom: '1px solid var(--border-subtle)',
      backgroundColor: 'rgba(15, 21, 35, 0.75)',
      backdropFilter: 'blur(12px)',
      padding: '0 36px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      zIndex: 10,
    }}>
      {/* Demo Role Switcher */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '12px', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Демо-роль:
        </span>
        <div style={{ display: 'flex', gap: '6px', backgroundColor: 'var(--bg-surface)', padding: '4px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          {roles.map((r) => {
            const isSelected = user?.email === r.email;
            const Icon = r.icon;
            return (
              <button
                key={r.email}
                onClick={() => onRoleSwitch(r.email)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  fontSize: '12px',
                  fontWeight: isSelected ? 600 : 400,
                  borderRadius: 'var(--radius-sm)',
                  border: isSelected ? '1px solid var(--border-highlight)' : '1px solid transparent',
                  backgroundColor: isSelected ? 'var(--primary)' : 'transparent',
                  color: isSelected ? '#ffffff' : 'var(--text-muted)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <Icon size={13} />
                <span>{r.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* User profile & logout */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: 'var(--bg-surface-elevated)',
            border: '1px solid var(--border-medium)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--primary-light)',
            fontWeight: 600,
            fontSize: '14px',
          }}>
            {user ? `${user.first_name[0] || 'U'}${user.last_name[0] || ''}` : <User size={18} />}
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>
              {user ? `${user.first_name} ${user.last_name}` : 'Гость'}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {user?.email || 'Не авторизован'}
            </div>
          </div>
        </div>

        <button
          onClick={onLogout}
          title="Выйти"
          style={{
            background: 'transparent',
            border: '1px solid var(--border-subtle)',
            color: 'var(--text-muted)',
            padding: '8px',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <LogOut size={16} />
        </button>
      </div>
    </header>
  );
};
