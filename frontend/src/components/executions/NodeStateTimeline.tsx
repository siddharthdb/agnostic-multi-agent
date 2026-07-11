import type { NodeState, NodeStatus } from '../../types/execution'

const CLASSES: Record<NodeStatus, string> = {
  pending: 'neutral',
  running: 'warning',
  succeeded: 'success',
  failed: 'danger',
  skipped: 'neutral',
}

export function NodeStateTimeline({ nodeStates }: { nodeStates: Record<string, NodeState> }) {
  const entries = Object.entries(nodeStates)
  if (entries.length === 0) {
    return <p style={{ fontSize: 13 }}>No nodes have started yet.</p>
  }

  return (
    <div className="node-timeline">
      {entries.map(([nodeId, state]) => (
        <div key={nodeId} className="node-timeline-item">
          <span className={`badge ${CLASSES[state.status]}`}>{state.status}</span>
          <strong>{nodeId}</strong>
          {state.error && <span style={{ color: 'var(--danger)', fontSize: 12 }}>{state.error}</span>}
          {state.output && <code className="node-output">{JSON.stringify(state.output)}</code>}
        </div>
      ))}
    </div>
  )
}
