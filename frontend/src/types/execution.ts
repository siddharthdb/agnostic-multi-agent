export type ExecutionStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
export type NodeStatus = 'pending' | 'running' | 'succeeded' | 'failed' | 'skipped'

export interface NodeState {
  status: NodeStatus
  input?: Record<string, unknown>
  output?: Record<string, unknown>
  error?: string | null
  started_at?: string
  ended_at?: string
}

export interface Execution {
  id: string
  workflow_id: string
  status: ExecutionStatus
  input_payload: Record<string, unknown>
  node_states: Record<string, NodeState>
  cancel_requested: boolean
  started_at: string | null
  ended_at: string | null
  created_at: string
}

export interface ExecutionEvent {
  seq: number
  event_type: string
  node_id: string | null
  payload: Record<string, unknown>
  created_at: string
}

export interface ExecutionDetail extends Execution {
  event_log: ExecutionEvent[]
}
