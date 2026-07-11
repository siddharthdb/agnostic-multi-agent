export type Protocol = 'REST' | 'A2A' | 'MCP' | 'GRPC'
export type AuthType = 'none' | 'api_key' | 'bearer'
export type AgentStatus = 'active' | 'inactive' | 'unhealthy'

export interface Agent {
  id: string
  name: string
  description: string
  protocol: Protocol
  endpoint_url: string
  auth_type: AuthType
  auth_config: Record<string, unknown>
  input_schema: Record<string, unknown>
  output_schema: Record<string, unknown>
  capability_tags: string[]
  status: AgentStatus
  health_check_url: string | null
  created_at: string
  updated_at: string
}

export type AgentCreate = Omit<Agent, 'id' | 'created_at' | 'updated_at'>
export type AgentUpdate = Partial<AgentCreate>

export interface AgentHealthResult {
  agent_id: string
  status: AgentStatus
  reachable: boolean
  latency_ms: number | null
  error: string | null
}
