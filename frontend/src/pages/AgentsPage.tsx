import { useEffect, useState } from 'react'
import { agentsApi } from '../api/agents'
import { ApiError } from '../api/client'
import { AgentForm } from '../components/agents/AgentForm'
import { AgentTable } from '../components/agents/AgentTable'
import type { Agent } from '../types/agent'

export function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingAgent, setEditingAgent] = useState<Agent | null | undefined>(undefined)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setAgents(await agentsApi.list())
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load agents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="page">
      <div className="page-header">
        <h1>Agents</h1>
        <button className="primary" onClick={() => setEditingAgent(null)}>
          New Agent
        </button>
      </div>
      {error && <div className="error-banner">{error}</div>}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <AgentTable agents={agents} onEdit={(agent) => setEditingAgent(agent)} onChanged={load} />
      )}
      {editingAgent !== undefined && (
        <AgentForm
          agent={editingAgent}
          onClose={() => setEditingAgent(undefined)}
          onSaved={() => {
            setEditingAgent(undefined)
            load()
          }}
        />
      )}
    </div>
  )
}
