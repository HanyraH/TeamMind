import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Sparkles,
  CalendarDays,
  History,
  Code2,
  ShieldCheck,
  Zap,
} from 'lucide-react';

interface SidebarProps {
  currentRole: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentRole }) => {
  const navItems = [
    { to: '/', label: 'Дашборд', icon: LayoutDashboard },
    { to: '/employees', label: 'Сотрудники', icon: Users },
    { to: '/projects', label: 'Проекты и задачи', icon: Briefcase },
    { to: '/team-builder', label: 'Конструктор команд', icon: Sparkles, highlight: true },
    { to: '/vacations', label: 'График отпусков', icon: CalendarDays },
    { to: '/history', label: 'История и аудит', icon: History },
    { to: '/graphql', label: 'GraphQL Explorer', icon: Code2 },
  ];

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div style={{ padding: '24px 20px', display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)',
        }}>
          <Zap size={20} color="#ffffff" />
        </div>
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 800, letterSpacing: '-0.02em', color: '#ffffff' }}>
            TeamMind
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 500, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            AI Team Assistant
          </div>
        </div>
      </div>

      {/* Nav Menu */}
      <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '11px 14px',
                borderRadius: 'var(--radius-md)',
                color: isActive ? '#ffffff' : 'var(--text-muted)',
                backgroundColor: isActive ? 'var(--bg-surface-elevated)' : 'transparent',
                textDecoration: 'none',
                fontSize: '14px',
                fontWeight: isActive ? 600 : 500,
                border: isActive ? '1px solid var(--border-highlight)' : '1px solid transparent',
                transition: 'all 0.15s ease',
              })}
            >
              <Icon size={18} color={item.highlight ? '#818cf8' : undefined} />
              <span>{item.label}</span>
              {item.highlight && (
                <span style={{
                  marginLeft: 'auto',
                  fontSize: '10px',
                  fontWeight: 700,
                  backgroundColor: 'rgba(99, 102, 241, 0.2)',
                  color: '#818cf8',
                  padding: '2px 6px',
                  borderRadius: '12px',
                  border: '1px solid rgba(99, 102, 241, 0.4)'
                }}>
                  AI
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-subtle)', backgroundColor: 'rgba(15, 21, 35, 0.6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981', boxShadow: '0 0 8px #10b981' }} />
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>Backend API Online</span>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
          Роль: <strong style={{ color: 'var(--text-main)' }}>{currentRole}</strong>
        </div>
      </div>
    </aside>
  );
};
