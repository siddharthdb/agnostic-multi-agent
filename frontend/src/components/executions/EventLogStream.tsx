import { useEffect, useRef } from 'react'
import type { ExecutionEvent } from '../../types/execution'

interface EventLogStreamProps {
  events: ExecutionEvent[]
  connected: boolean
}

export function EventLogStream({ events, connected }: EventLogStreamProps) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [events.length])

  return (
    <div className="event-log">
      <div className="event-log-header">
        <h3>Event log</h3>
        <span className={`badge ${connected ? 'success' : 'neutral'}`}>
          {connected ? 'live' : 'connecting...'}
        </span>
      </div>
      <div className="event-log-body">
        {events.length === 0 && <p style={{ fontSize: 13 }}>No events yet.</p>}
        {events.map((e) => (
          <div key={e.seq} className="event-log-line">
            <span className="event-log-seq">#{e.seq}</span>
            <span className="event-log-type">{e.event_type}</span>
            {e.node_id && <span className="event-log-node">{e.node_id}</span>}
            {Object.keys(e.payload).length > 0 && <code>{JSON.stringify(e.payload)}</code>}
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  )
}
