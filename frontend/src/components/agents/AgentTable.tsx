import { useState } from 'react'
import { agentsApi } from '../../api/agents'
import type { Agent } from '../../types/agent'
import { AgentHealthBadge } from './AgentHealthBadge'

interface AgentTableProps {
  agents: Agent[]
  onEdit: (agent: Agent) => void
  onChanged: () => void
}

export function AgentTable({ agents, onEdit, onChanged }: AgentTableProps) {
  const [checkingId, setCheckingId] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [rowError, setRowError] = useState<string | null>(null)

  async function handleCheckHealth(id: string) {
    setCheckingId(id)
    setRowError(null)
    try {
      await agentsApi.checkHealth(id)
      onChanged()
    } catch {
      setRowError('Health check failed')
    } finally {
      setCheckingId(null)
    }
  }

  async function handleDelete(agent: Agent) {
    if (!confirm(`Delete agent "${agent.name}"?`)) return
    setDeletingId(agent.id)
    setRowError(null)
    try {
      await agentsApi.remove(agent.id)
      onChanged()
    } catch {
      setRowError(`Could not delete "${agent.name}" (it may be referenced by a published workflow)`)
    } finally {
      setDeletingId(null)
    }
  }

  if (agents.length === 0) {
    return <div className="empty-state">No agents registered yet.</div>
  }

  return (
    <>
      {rowError && <div className="error-banner">{rowError}</div>}
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Protocol</th>
            <th>Endpoint</th>
            <th>Tags</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {agents.map((agent) => (
            <tr key={agent.id}>
              <td>
                <strong>{agent.name}</strong>
                {agent.description && <div style={{ fontSize: 12 }}>{agent.description}</div>}
              </td>
              <td>{agent.protocol}</td>
              <td>
                <code>{agent.endpoint_url}</code>
              </td>
              <td>{agent.capability_tags.join(', ') || '—'}</td>
              <td>
                <AgentHealthBadge status={agent.status} />
              </td>
              <td>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button onClick={() => handleCheckHealth(agent.id)} disabled={checkingId === agent.id}>
                    {checkingId === agent.id ? 'Checking...' : 'Check health'}
                  </button>
                  <button onClick={() => onEdit(agent)}>Edit</button>
                  <button onClick={() => handleDelete(agent)} disabled={deletingId === agent.id}>
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
