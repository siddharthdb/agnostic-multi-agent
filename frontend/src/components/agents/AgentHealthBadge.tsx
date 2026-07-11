import type { AgentStatus } from '../../types/agent'

const LABELS: Record<AgentStatus, string> = {
  active: 'Active',
  inactive: 'Inactive',
  unhealthy: 'Unhealthy',
}

const CLASSES: Record<AgentStatus, string> = {
  active: 'success',
  inactive: 'neutral',
  unhealthy: 'danger',
}

export function AgentHealthBadge({ status }: { status: AgentStatus }) {
  return <span className={`badge ${CLASSES[status]}`}>{LABELS[status]}</span>
}
