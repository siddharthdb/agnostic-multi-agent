import { useEffect, useState } from 'react'
import { executionsApi } from '../api/executions'
import type { ExecutionEvent } from '../types/execution'

const TERMINAL_EVENT_TYPES = new Set([
  'execution_completed',
  'execution_failed',
  'execution_cancelled',
])

export function useSse(executionId: string | null) {
  const [events, setEvents] = useState<ExecutionEvent[]>([])
  const [connected, setConnected] = useState(false)
  const [finished, setFinished] = useState(false)

  useEffect(() => {
    if (!executionId) return
    setEvents([])
    setFinished(false)
    setConnected(false)

    let lastSeq = -1
    let es: EventSource | null = null
    let stopped = false
    let retryTimer: ReturnType<typeof setTimeout> | null = null

    function connect() {
      if (stopped) return
      es = new EventSource(
        executionsApi.eventsUrl(executionId!, lastSeq >= 0 ? lastSeq : undefined),
      )
      es.onopen = () => setConnected(true)
      es.onmessage = (msg) => {
        const event = JSON.parse(msg.data) as ExecutionEvent
        if (event.seq <= lastSeq) return
        lastSeq = event.seq
        setEvents((prev) => [...prev, event])
        if (TERMINAL_EVENT_TYPES.has(event.event_type)) {
          stopped = true
          setFinished(true)
          es?.close()
        }
      }
      es.onerror = () => {
        setConnected(false)
        es?.close()
        if (!stopped) {
          retryTimer = setTimeout(connect, 2000)
        }
      }
    }

    connect()

    return () => {
      stopped = true
      if (retryTimer) clearTimeout(retryTimer)
      es?.close()
    }
  }, [executionId])

  return { events, connected, finished }
}
