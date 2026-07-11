import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { ApiError } from '../api/client'
import { executionsApi } from '../api/executions'
import { EventLogStream } from '../components/executions/EventLogStream'
import { ExecutionStatusBadge } from '../components/executions/ExecutionStatusBadge'
import { NodeStateTimeline } from '../components/executions/NodeStateTimeline'
import { useSse } from '../hooks/useSse'
import { usePolling } from '../hooks/usePolling'
import type { ExecutionDetail as ExecutionDetailType } from '../types/execution'

const ACTIVE_STATUSES = new Set(['queued', 'running'])

export function ExecutionDetailPage() {
  const { executionId } = useParams<{ executionId: string }>()
  const [execution, setExecution] = useState<ExecutionDetailType | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [cancelling, setCancelling] = useState(false)
  const { events, connected } = useSse(executionId ?? null)

  async function load() {
    if (!executionId) return
    try {
      setExecution(await executionsApi.get(executionId))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load execution')
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [executionId])

  // SSE drives the live log; re-fetch the execution itself whenever a new
  // event arrives so node_states/status always come from the backend's
  // source of truth rather than being derived client-side from the log.
  useEffect(() => {
    if (events.length > 0) load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [events.length])

  const isActive = execution ? ACTIVE_STATUSES.has(execution.status) : false
  usePolling(load, 3000, isActive && !connected)

  async function handleCancel() {
    if (!executionId) return
    setCancelling(true)
    try {
      await executionsApi.cancel(executionId)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to cancel execution')
    } finally {
      setCancelling(false)
    }
  }

  if (!execution) {
    return (
      <div className="page">
        {error ? <div className="error-banner">{error}</div> : <p>Loading...</p>}
      </div>
    )
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>
            Execution <code>{execution.id}</code>
          </h1>
          <ExecutionStatusBadge status={execution.status} />
        </div>
        {isActive && (
          <button onClick={handleCancel} disabled={cancelling || execution.cancel_requested}>
            {execution.cancel_requested || cancelling ? 'Cancelling...' : 'Cancel'}
          </button>
        )}
      </div>
      {error && <div className="error-banner">{error}</div>}

      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Input</h3>
        <code>{JSON.stringify(execution.input_payload)}</code>
      </div>

      <h2>Node states</h2>
      <NodeStateTimeline nodeStates={execution.node_states} />

      <EventLogStream events={events.length > 0 ? events : execution.event_log} connected={connected} />
    </div>
  )
}
