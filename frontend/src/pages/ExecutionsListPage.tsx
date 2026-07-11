import { useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { executionsApi } from '../api/executions'
import { ExecutionTable } from '../components/executions/ExecutionTable'
import { usePolling } from '../hooks/usePolling'
import type { Execution } from '../types/execution'

export function ExecutionsListPage() {
  const [executions, setExecutions] = useState<Execution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    try {
      setExecutions(await executionsApi.list())
      setError(null)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load executions')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  usePolling(load, 5000, true)

  return (
    <div className="page">
      <h1>Executions</h1>
      {error && <div className="error-banner">{error}</div>}
      {loading ? <p>Loading...</p> : <ExecutionTable executions={executions} />}
    </div>
  )
}
