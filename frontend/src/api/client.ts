import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT access token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const res = await axios.post('/api/auth/token/refresh/', { refresh });
          localStorage.setItem('access_token', res.data.access);
          originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
          return api(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user_info');
        }
      }
    }
    return Promise.reject(error);
  }
);

export interface UserInfo {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'project_manager' | 'employee';
  is_admin: boolean;
  is_project_manager: boolean;
  is_employee: boolean;
}

export const AuthAPI = {
  login: async (email: string, password: string) => {
    const res = await api.post('/auth/login/', { email, password });
    if (res.data.access) {
      localStorage.setItem('access_token', res.data.access);
      localStorage.setItem('refresh_token', res.data.refresh);
      localStorage.setItem('user_info', JSON.stringify(res.data.user));
    }
    return res.data;
  },
  me: async (): Promise<UserInfo> => {
    const res = await api.get('/auth/me/');
    localStorage.setItem('user_info', JSON.stringify(res.data));
    return res.data;
  },
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
  },
  getCurrentUser: (): UserInfo | null => {
    const data = localStorage.getItem('user_info');
    return data ? JSON.parse(data) : null;
  },
};

export const EmployeesAPI = {
  list: async (params?: any) => {
    const res = await api.get('/employees/', { params });
    return res.data.results !== undefined ? res.data.results : res.data;
  },
  get: async (id: number) => {
    const res = await api.get(`/employees/${id}/`);
    return res.data;
  },
  departments: async () => {
    const res = await api.get('/employees/departments/');
    return res.data.results !== undefined ? res.data.results : res.data;
  },
  positions: async () => {
    const res = await api.get('/employees/positions/');
    return res.data.results !== undefined ? res.data.results : res.data;
  },
  skills: async () => {
    const res = await api.get('/employees/skills/');
    return res.data.results !== undefined ? res.data.results : res.data;
  },
};

export const ProjectsAPI = {
  list: async (params?: any) => {
    const res = await api.get('/projects/', { params });
    return res.data.results !== undefined ? res.data.results : res.data;
  },
  get: async (id: number) => {
    const res = await api.get(`/projects/${id}/`);
    return res.data;
  },
  create: async (data: any) => {
    const res = await api.post('/projects/', data);
    return res.data;
  },
  tasks: async (projectId?: number) => {
    const res = await api.get('/projects/tasks/', { params: { project: projectId } });
    return res.data.results !== undefined ? res.data.results : res.data;
  },
  addSkillRequirement: async (projectId: number, data: any) => {
    const res = await api.post(`/projects/${projectId}/skill-requirements/`, data);
    return res.data;
  },
};

export const TeamsAPI = {
  list: async (params?: any) => {
    const res = await api.get('/teams/', { params });
    return res.data.results !== undefined ? res.data.results : res.data;
  },
  get: async (id: number) => {
    const res = await api.get(`/teams/${id}/`);
    return res.data;
  },
  generate: async (projectId: number, teamSize: number = 5) => {
    const res = await api.post('/teams/runs/generate/', {
      project_id: projectId,
      team_size: teamSize,
    });
    return res.data;
  },
  getRunStatus: async (runId: number) => {
    const res = await api.get(`/teams/runs/${runId}/status/`);
    return res.data;
  },
  approve: async (teamId: number) => {
    const res = await api.post(`/teams/${teamId}/approve/`);
    return res.data;
  },
  reject: async (teamId: number) => {
    const res = await api.post(`/teams/${teamId}/reject/`);
    return res.data;
  },
  addMember: async (teamId: number, employeeId: number, role: string) => {
    const res = await api.post(`/teams/${teamId}/members/add/`, {
      employee_id: employeeId,
      role_in_team: role,
    });
    return res.data;
  },
  removeMember: async (teamId: number, memberId: number) => {
    const res = await api.delete(`/teams/${teamId}/members/${memberId}/remove/`);
    return res.data;
  },
};

export const VacationsAPI = {
  list: async (params?: any) => {
    const res = await api.get('/vacations/', { params });
    return res.data.results !== undefined ? res.data.results : res.data;
  },
  create: async (data: any) => {
    const res = await api.post('/vacations/', data);
    return res.data;
  },
  approve: async (id: number) => {
    const res = await api.post(`/vacations/${id}/approve/`);
    return res.data;
  },
  reject: async (id: number) => {
    const res = await api.post(`/vacations/${id}/reject/`);
    return res.data;
  },
};

export const AnalyticsAPI = {
  dashboard: async () => {
    const res = await api.get('/analytics/dashboard/');
    return res.data;
  },
  projectsWithoutTeam: async () => {
    const res = await api.get('/analytics/projects-without-team/');
    return res.data;
  },
};

export const GraphQLAPI = {
  execute: async (query: string, variables: any = {}) => {
    const token = localStorage.getItem('access_token');
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await axios.post('/graphql/', { query, variables }, { headers });
    return res.data;
  },
};

export default api;
