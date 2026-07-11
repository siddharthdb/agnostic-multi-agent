import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../api/client'
import { workflowsApi } from '../api/workflows'
import type { Workflow } from '../types/workflow'

export function WorkflowsListPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setWorkflows(await workflowsApi.list())
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load workflows')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function handleDelete(workflow: Workflow) {
    if (!confirm(`Delete workflow "${workflow.name}"?`)) return
    try {
      await workflowsApi.remove(workflow.id)
      load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to delete workflow')
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Workflows</h1>
        <Link to="/workflows/new">
          <button className="primary">New Workflow</button>
        </Link>
      </div>
      {error && <div className="error-banner">{error}</div>}
      {loading ? (
        <p>Loading...</p>
      ) : workflows.length === 0 ? (
        <div className="empty-state">No workflows yet.</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Version</th>
              <th>Nodes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {workflows.map((wf) => (
              <tr key={wf.id}>
                <td>
                  <strong>{wf.name}</strong>
                  {wf.description && <div style={{ fontSize: 12 }}>{wf.description}</div>}
                </td>
                <td>
                  <span className={`badge ${wf.status === 'published' ? 'success' : 'neutral'}`}>
                    {wf.status}
                  </span>
                </td>
                <td>{wf.version}</td>
                <td>{wf.definition.nodes.length}</td>
                <td>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <Link to={`/workflows/${wf.id}`}>
                      <button>Edit</button>
                    </Link>
                    <button onClick={() => handleDelete(wf)}>Delete</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
