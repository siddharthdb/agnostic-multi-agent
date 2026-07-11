import type { ExecutionStatus } from '../../types/execution'

const CLASSES: Record<ExecutionStatus, string> = {
  queued: 'neutral',
  running: 'warning',
  completed: 'success',
  failed: 'danger',
  cancelled: 'neutral',
}

export function ExecutionStatusBadge({ status }: { status: ExecutionStatus }) {
  return <span className={`badge ${CLASSES[status]}`}>{status}</span>
}
