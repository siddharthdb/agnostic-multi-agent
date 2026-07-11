import { apiClient } from './client'
import type { Execution } from '../types/execution'
import type { ValidationResult, Workflow, WorkflowCreate, WorkflowUpdate } from '../types/workflow'

export const workflowsApi = {
  list: () => apiClient.get<Workflow[]>('/workflows'),
  get: (id: string) => apiClient.get<Workflow>(`/workflows/${id}`),
  create: (data: WorkflowCreate) => apiClient.post<Workflow>('/workflows', data),
  update: (id: string, data: WorkflowUpdate) => apiClient.put<Workflow>(`/workflows/${id}`, data),
  remove: (id: string) => apiClient.delete<void>(`/workflows/${id}`),
  validate: (id: string) => apiClient.post<ValidationResult>(`/workflows/${id}/validate`),
  execute: (id: string, inputPayload: Record<string, unknown>) =>
    apiClient.post<Execution>(`/workflows/${id}/execute`, { input_payload: inputPayload }),
}
