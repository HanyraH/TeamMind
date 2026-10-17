import React, { useState } from 'react';
import { Code2, Play, Check, Copy, BookOpen } from 'lucide-react';
import { GraphQLAPI } from '../api/client';

export const GraphQLExplorerPage: React.FC = () => {
  const PRESETS = [
    {
      title: 'Сводные метрики дашборда',
      query: `query GetDashboardMetrics {
  dashboardMetrics {
    totalEmployees
    activeEmployees
    totalProjects
    activeProjects
    pendingVacations
    avgWorkloadPct
  }
}`,
    },
    {
      title: 'Утилизация отделов',
      query: `query GetDepartmentWorkloads {
  departmentWorkloads {
    department
    employeeCount
    avgUtilizationPct
  }
}`,
    },
    {
      title: 'Варианты команд по проекту (Project #1)',
      query: `query GetProjectTeams {
  projectTeams(projectId: 1) {
    id
    variantName
    totalScore
    skillCoveragePct
    approvalStatus
  }
}`,
    },
    {
      title: 'Мутация: Утверждение состава команды',
      query: `mutation ApproveTeamVariant {
  approveTeam(teamId: 1) {
    teamId
    approvalStatus
    approvedBy
  }
}`,
    },
  ];

  const [query, setQuery] = useState(PRESETS[0].query);
  const [response, setResponse] = useState<string>('{\n  "data": null\n}');
  const [executing, setExecuting] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleExecute = async () => {
    try {
      setExecuting(true);
      const res = await GraphQLAPI.execute(query);
      setResponse(JSON.stringify(res, null, 2));
    } catch (err: any) {
      setResponse(JSON.stringify(err.response?.data || { error: err.message }, null, 2));
    } finally {
      setExecuting(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(response);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="title-lg">GraphQL Explorer</h1>
          <p className="text-muted" style={{ marginTop: '4px', fontSize: '14px' }}>
            Интерактивная консоль для выполнения Query и Mutation через Strawberry GraphQL endpoint (/graphql/)
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={handleExecute}
          disabled={executing}
        >
          <Play size={16} fill="currentColor" />
          <span>{executing ? 'Выполнение...' : 'Выполнить запрос'}</span>
        </button>
      </div>

      {/* Query Presets */}
      <div className="glass-card" style={{ padding: '16px 20px' }}>
        <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '10px' }}>
          Готовые шаблоны запросов (Query / Mutation):
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setQuery(p.query);
                setResponse('{\n  "data": null\n}');
              }}
            >
              <BookOpen size={13} color="var(--primary-light)" />
              <span>{p.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Editor & Response Split View */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', minHeight: '480px' }}>
        {/* Editor Box */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 20px', backgroundColor: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Code2 size={16} color="var(--primary-light)" />
            <span style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>GraphQL Редактор</span>
          </div>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              width: '100%',
              backgroundColor: 'transparent',
              border: 'none',
              color: '#a5b4fc',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              lineHeight: '1.6',
              padding: '20px',
              outline: 'none',
              resize: 'none',
            }}
          />
        </div>

        {/* Response Box */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 20px', backgroundColor: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>Ответ сервера (JSON)</span>
            <button
              onClick={handleCopy}
              className="btn btn-secondary btn-sm"
              style={{ padding: '4px 8px', fontSize: '11px' }}
            >
              {copied ? <Check size={12} color="#10b981" /> : <Copy size={12} />}
              <span>{copied ? 'Скопировано' : 'Копировать'}</span>
            </button>
          </div>
          <pre
            style={{
              flex: 1,
              width: '100%',
              backgroundColor: 'transparent',
              color: '#34d399',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              lineHeight: '1.6',
              padding: '20px',
              margin: 0,
              overflowY: 'auto',
            }}
          >
            {response}
          </pre>
        </div>
      </div>
    </div>
  );
};
