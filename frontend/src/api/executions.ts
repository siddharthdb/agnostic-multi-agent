import { apiClient, API_BASE_URL } from './client'
import type { Execution, ExecutionDetail } from '../types/execution'

export const executionsApi = {
  list: (params?: { workflow_id?: string; status?: string }) => {
    const search = new URLSearchParams()
    if (params?.workflow_id) search.set('workflow_id', params.workflow_id)
    if (params?.status) search.set('status', params.status)
    const qs = search.toString()
    return apiClient.get<Execution[]>(`/executions${qs ? `?${qs}` : ''}`)
  },
  get: (id: string) => apiClient.get<ExecutionDetail>(`/executions/${id}`),
  cancel: (id: string) => apiClient.post<Execution>(`/executions/${id}/cancel`),
  eventsUrl: (id: string, since?: number) =>
    `${API_BASE_URL}/executions/${id}/events${since !== undefined ? `?since=${since}` : ''}`,
}
