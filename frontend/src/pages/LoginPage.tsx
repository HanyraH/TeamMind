import React, { useState } from 'react';
import { Zap, Shield, Briefcase, UserCheck, ArrowRight, Lock, Mail } from 'lucide-react';
import { AuthAPI } from '../api/client';

interface LoginPageProps {
  onLoginSuccess: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (loginEmail?: string, loginPassword?: string) => {
    const e = loginEmail || email;
    const p = loginPassword || password;
    if (!e || !p) {
      setError('Пожалуйста, укажите email и пароль');
      return;
    }

    try {
      setLoading(true);
      setError('');
      await AuthAPI.login(e, p);
      onLoginSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Неверный логин или пароль');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (quickEmail: string, quickPassword: string) => {
    setEmail(quickEmail);
    setPassword(quickPassword);
    handleLogin(quickEmail, quickPassword);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at 50% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 60%), #0a0e17',
      padding: '24px',
    }}>
      <div className="glass-card" style={{ maxWidth: '440px', width: '100%', padding: '36px' }}>
        {/* Logo & Title */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '14px',
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 20px rgba(99, 102, 241, 0.4)',
            marginBottom: '14px',
          }}>
            <Zap size={24} color="#ffffff" />
          </div>
          <h1 className="title-md" style={{ fontSize: '24px' }}>Вход в TeamMind</h1>
          <p className="text-muted" style={{ fontSize: '13px', marginTop: '4px' }}>
            Интеллектуальная система формирования проектных команд
          </p>
        </div>

        {error && (
          <div style={{
            backgroundColor: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            padding: '10px 14px',
            fontSize: '13px',
            color: '#f87171',
            marginBottom: '20px',
            textAlign: 'center',
          }}>
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#cbd5e1' }}>
              Email или логин
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} color="var(--text-dim)" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type="text"
                required
                className="input-field"
                placeholder="admin или admin@teammind.ru"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ paddingLeft: '38px' }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, marginBottom: '6px', color: '#cbd5e1' }}>
              Пароль
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} color="var(--text-dim)" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type="password"
                required
                className="input-field"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ paddingLeft: '38px' }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '8px', padding: '11px' }}
          >
            <span>{loading ? 'Авторизация...' : 'Войти в систему'}</span>
            <ArrowRight size={16} />
          </button>
        </form>

        {/* Quick Demo Login Buttons */}
        <div style={{ marginTop: '28px', borderTop: '1px solid var(--border-subtle)', paddingTop: '20px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.05em', textAlign: 'center', marginBottom: '12px' }}>
            Быстрый вход для демонстрации (1 клик):
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              style={{ justifyContent: 'flex-start', padding: '8px 12px' }}
              onClick={() => handleQuickLogin('admin@teammind.ru', 'AdminPassword123!')}
            >
              <Shield size={14} color="#818cf8" />
              <span>Администратор (логин: admin / пароль: admin)</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              style={{ justifyContent: 'flex-start', padding: '8px 12px' }}
              onClick={() => handleQuickLogin('pm@teammind.ru', 'ManagerPassword123!')}
            >
              <Briefcase size={14} color="#fbbf24" />
              <span>Руководитель проекта (логин: pm / пароль: pm)</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              style={{ justifyContent: 'flex-start', padding: '8px 12px' }}
              onClick={() => handleQuickLogin('dev@teammind.ru', 'DevPassword123!')}
            >
              <UserCheck size={14} color="#34d399" />
              <span>Сотрудник (логин: dev / пароль: dev)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
