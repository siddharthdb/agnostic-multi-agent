import { apiClient } from './client'
import type { Agent, AgentCreate, AgentHealthResult, AgentUpdate } from '../types/agent'

export const agentsApi = {
  list: () => apiClient.get<Agent[]>('/agents'),
  get: (id: string) => apiClient.get<Agent>(`/agents/${id}`),
  create: (data: AgentCreate) => apiClient.post<Agent>('/agents', data),
  update: (id: string, data: AgentUpdate) => apiClient.put<Agent>(`/agents/${id}`, data),
  remove: (id: string) => apiClient.delete<void>(`/agents/${id}`),
  checkHealth: (id: string) => apiClient.get<AgentHealthResult>(`/agents/${id}/health`),
}
