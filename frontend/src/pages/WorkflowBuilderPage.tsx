import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { agentsApi } from '../api/agents'
import { ApiError } from '../api/client'
import { workflowsApi } from '../api/workflows'
import { DagCanvas } from '../components/workflow-builder/DagCanvas'
import { ValidationPanel } from '../components/workflow-builder/ValidationPanel'
import type { Agent } from '../types/agent'
import type { ValidationResult, WorkflowDefinition, WorkflowStatus } from '../types/workflow'

const EMPTY_DEFINITION: WorkflowDefinition = { nodes: [], edges: [] }

export function WorkflowBuilderPage() {
  const { workflowId } = useParams<{ workflowId: string }>()
  const navigate = useNavigate()
  const isNew = workflowId === 'new'

  const [agents, setAgents] = useState<Agent[]>([])
  const [agentsLoaded, setAgentsLoaded] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [status, setStatus] = useState<WorkflowStatus>('draft')
  const [persistedId, setPersistedId] = useState<string | null>(isNew ? null : (workflowId ?? null))
  const [definition, setDefinition] = useState<WorkflowDefinition>(EMPTY_DEFINITION)
  const [loading, setLoading] = useState(!isNew)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [runInput, setRunInput] = useState('{}')

  useEffect(() => {
    agentsApi
      .list()
      .then(setAgents)
      .catch(() => {})
      .finally(() => setAgentsLoaded(true))
  }, [])

  useEffect(() => {
    if (isNew) return
    setLoading(true)
    workflowsApi
      .get(workflowId!)
      .then((wf) => {
        setName(wf.name)
        setDescription(wf.description)
        setStatus(wf.status)
        setDefinition(wf.definition)
        setPersistedId(wf.id)
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Failed to load workflow'))
      .finally(() => setLoading(false))
  }, [workflowId, isNew])

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      if (persistedId) {
        await workflowsApi.update(persistedId, { name, description, definition })
      } else {
        const created = await workflowsApi.create({ name, description, definition, status: 'draft' })
        setPersistedId(created.id)
        navigate(`/workflows/${created.id}`, { replace: true })
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to save workflow')
    } finally {
      setSaving(false)
    }
  }

  async function handleValidate() {
    if (!persistedId) {
      setError('Save the workflow before validating')
      return
    }
    setError(null)
    try {
      setValidationResult(await workflowsApi.validate(persistedId))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Validation failed')
    }
  }

  async function handlePublish() {
    if (!persistedId) return
    setError(null)
    try {
      const updated = await workflowsApi.update(persistedId, { status: 'published' })
      setStatus(updated.status)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to publish workflow')
    }
  }

  async function handleRun() {
    if (!persistedId) return
    let payload: Record<string, unknown>
    try {
      payload = JSON.parse(runInput)
    } catch {
      setError('Run input must be valid JSON')
      return
    }
    setError(null)
    try {
      const execution = await workflowsApi.execute(persistedId, payload)
      navigate(`/executions/${execution.id}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to start execution')
    }
  }

  if (loading || !agentsLoaded) {
    return (
      <div className="page">
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className="page workflow-builder-page">
      <div className="page-header">
        <div>
          <input
            className="workflow-name-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Workflow name"
          />
          <div>
            <span className={`badge ${status === 'published' ? 'success' : 'neutral'}`}>{status}</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={handleValidate}>Validate</button>
          <button onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </button>
          <button onClick={handlePublish} disabled={!persistedId || status === 'published'}>
            Publish
          </button>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
      <input
        className="workflow-description-input"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
      />

      <DagCanvas initialDefinition={definition} agents={agents} onChange={setDefinition} />

      <ValidationPanel result={validationResult} />

      <div className="card run-panel">
        <h3>Run workflow</h3>
        <textarea rows={3} value={runInput} onChange={(e) => setRunInput(e.target.value)} />
        <button className="primary" onClick={handleRun} disabled={!persistedId}>
          Execute
        </button>
      </div>
    </div>
  )
}
