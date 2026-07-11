export type WorkflowStatus = 'draft' | 'published'
export type ConditionOp = 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'contains'

export interface WorkflowEdgeCondition {
  field: string
  op: ConditionOp
  value: unknown
}

export interface WorkflowNode {
  id: string
  agent_id: string
  label?: string
  input_mapping?: Record<string, string>
}

export interface WorkflowEdge {
  from: string
  to: string
  condition?: WorkflowEdgeCondition | null
}

export interface WorkflowDefinition {
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
}

export interface Workflow {
  id: string
  name: string
  description: string
  definition: WorkflowDefinition
  version: number
  status: WorkflowStatus
  created_at: string
  updated_at: string
}

export interface WorkflowCreate {
  name: string
  description?: string
  definition: WorkflowDefinition
  status?: WorkflowStatus
}

export type WorkflowUpdate = Partial<WorkflowCreate>

export interface ValidationIssue {
  code: string
  message: string
  node_id?: string | null
  edge?: Record<string, unknown> | null
}

export interface ValidationResult {
  valid: boolean
  errors: ValidationIssue[]
  warnings: ValidationIssue[]
  topo_order: string[]
}
