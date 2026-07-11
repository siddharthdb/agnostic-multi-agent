import { useState } from 'react'
import { agentsApi } from '../../api/agents'
import { ApiError } from '../../api/client'
import type { Agent, AgentStatus, AuthType, Protocol } from '../../types/agent'

interface AgentFormProps {
  agent?: Agent | null
  onClose: () => void
  onSaved: () => void
}

function stringifyJson(value: Record<string, unknown>): string {
  return JSON.stringify(value ?? {}, null, 2)
}

export function AgentForm({ agent, onClose, onSaved }: AgentFormProps) {
  const isEdit = Boolean(agent)
  const [name, setName] = useState(agent?.name ?? '')
  const [description, setDescription] = useState(agent?.description ?? '')
  const [protocol, setProtocol] = useState<Protocol>(agent?.protocol ?? 'REST')
  const [endpointUrl, setEndpointUrl] = useState(agent?.endpoint_url ?? '')
  const [healthCheckUrl, setHealthCheckUrl] = useState(agent?.health_check_url ?? '')
  const [authType, setAuthType] = useState<AuthType>(agent?.auth_type ?? 'none')
  const [authConfigText, setAuthConfigText] = useState(stringifyJson(agent?.auth_config ?? {}))
  const [inputSchemaText, setInputSchemaText] = useState(stringifyJson(agent?.input_schema ?? {}))
  const [outputSchemaText, setOutputSchemaText] = useState(
    stringifyJson(agent?.output_schema ?? {}),
  )
  const [tagsText, setTagsText] = useState((agent?.capability_tags ?? []).join(', '))
  const [status, setStatus] = useState<AgentStatus>(agent?.status ?? 'active')
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    let authConfig: Record<string, unknown>
    let inputSchema: Record<string, unknown>
    let outputSchema: Record<string, unknown>
    try {
      authConfig = authConfigText.trim() ? JSON.parse(authConfigText) : {}
      inputSchema = inputSchemaText.trim() ? JSON.parse(inputSchemaText) : {}
      outputSchema = outputSchemaText.trim() ? JSON.parse(outputSchemaText) : {}
    } catch {
      setError('auth_config, input_schema, and output_schema must be valid JSON')
      return
    }

    const payload = {
      name,
      description,
      protocol,
      endpoint_url: endpointUrl,
      auth_type: authType,
      auth_config: authConfig,
      input_schema: inputSchema,
      output_schema: outputSchema,
      capability_tags: tagsText
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean),
      status,
      health_check_url: healthCheckUrl || null,
    }

    setSaving(true)
    try {
      if (isEdit && agent) {
        await agentsApi.update(agent.id, payload)
      } else {
        await agentsApi.create(payload)
      }
      onSaved()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to save agent')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <h2>{isEdit ? `Edit ${agent?.name}` : 'New Agent'}</h2>
        {error && <div className="error-banner">{error}</div>}
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Name
            <input id="agent-name" value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label>
            Description
            <input
              id="agent-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </label>
          <label>
            Protocol
            <select
              id="agent-protocol"
              value={protocol}
              onChange={(e) => setProtocol(e.target.value as Protocol)}
            >
              <option value="REST">REST</option>
              <option value="A2A">A2A</option>
              <option value="MCP">MCP</option>
              <option value="GRPC">GRPC</option>
            </select>
          </label>
          <label>
            Endpoint URL
            <input
              id="agent-endpoint-url"
              value={endpointUrl}
              onChange={(e) => setEndpointUrl(e.target.value)}
              placeholder="http://localhost:9001/invoke"
              required
            />
          </label>
          <label>
            Health check URL
            <input
              id="agent-health-check-url"
              value={healthCheckUrl}
              onChange={(e) => setHealthCheckUrl(e.target.value)}
              placeholder="http://localhost:9001/health"
            />
          </label>
          <label>
            Auth type
            <select
              id="agent-auth-type"
              value={authType}
              onChange={(e) => setAuthType(e.target.value as AuthType)}
            >
              <option value="none">none</option>
              <option value="api_key">api_key</option>
              <option value="bearer">bearer</option>
            </select>
          </label>
          <label>
            Capability tags (comma separated)
            <input id="agent-tags" value={tagsText} onChange={(e) => setTagsText(e.target.value)} />
          </label>
          <label>
            Status
            <select
              id="agent-status"
              value={status}
              onChange={(e) => setStatus(e.target.value as AgentStatus)}
            >
              <option value="active">active</option>
              <option value="inactive">inactive</option>
              <option value="unhealthy">unhealthy</option>
            </select>
          </label>
          <label className="span-2">
            Auth config (JSON)
            <textarea
              id="agent-auth-config"
              rows={3}
              value={authConfigText}
              onChange={(e) => setAuthConfigText(e.target.value)}
            />
          </label>
          <label className="span-2">
            Input schema (JSON)
            <textarea
              id="agent-input-schema"
              rows={4}
              value={inputSchemaText}
              onChange={(e) => setInputSchemaText(e.target.value)}
            />
          </label>
          <label className="span-2">
            Output schema (JSON)
            <textarea
              id="agent-output-schema"
              rows={4}
              value={outputSchemaText}
              onChange={(e) => setOutputSchemaText(e.target.value)}
            />
          </label>
          <div className="span-2 modal-actions">
            <button type="button" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
