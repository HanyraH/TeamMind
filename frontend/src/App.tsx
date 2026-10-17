import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { DashboardPage } from './pages/DashboardPage';
import { EmployeesPage } from './pages/EmployeesPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { TeamBuilderPage } from './pages/TeamBuilderPage';
import { VacationsPage } from './pages/VacationsPage';
import { HistoryPage } from './pages/HistoryPage';
import { GraphQLExplorerPage } from './pages/GraphQLExplorerPage';
import { LoginPage } from './pages/LoginPage';
import { AuthAPI, UserInfo } from './api/client';

export const App: React.FC = () => {
  const [user, setUser] = useState<UserInfo | null>(AuthAPI.getCurrentUser());
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    initAuth();
  }, []);

  const initAuth = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const me = await AuthAPI.me();
        setUser(me);
      } else {
        // Auto-login as Project Manager by default for seamless demo
        await handleRoleSwitch('pm@teammind.ru');
      }
    } catch {
      // If token invalid, auto-login as PM
      await handleRoleSwitch('pm@teammind.ru');
    } finally {
      setIsInitializing(false);
    }
  };

  const handleRoleSwitch = async (email: string) => {
    try {
      const passwords: Record<string, string[]> = {
        'admin@teammind.ru': ['AdminPassword123!', 'admin'],
        'pm@teammind.ru': ['ManagerPassword123!', 'pm', 'password'],
        'dev@teammind.ru': ['DevPassword123!', 'dev', 'password'],
      };
      const candidatePasswords = passwords[email] || ['Password123!'];
      let lastErr = null;
      for (const pw of candidatePasswords) {
        try {
          const res = await AuthAPI.login(email, pw);
          setUser(res.user);
          return;
        } catch (e) {
          lastErr = e;
        }
      }
      if (lastErr) console.error('Role switch failed:', lastErr);
    } catch (err) {
      console.error('Role switch failed:', err);
    }
  };

  const handleLogout = () => {
    AuthAPI.logout();
    setUser(null);
  };

  if (isInitializing) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', backgroundColor: '#0a0e17', color: '#818cf8', fontFamily: 'var(--font-sans)', fontSize: '16px' }}>
        Инициализация TeamMind...
      </div>
    );
  }

  if (!user) {
    return <LoginPage onLoginSuccess={() => initAuth()} />;
  }

  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar currentRole={user.role} />
        <div className="main-content">
          <Topbar
            user={user}
            onRoleSwitch={handleRoleSwitch}
            onLogout={handleLogout}
          />
          <main className="page-body">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/employees" element={<EmployeesPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/team-builder" element={<TeamBuilderPage />} />
              <Route path="/vacations" element={<VacationsPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/graphql" element={<GraphQLExplorerPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
