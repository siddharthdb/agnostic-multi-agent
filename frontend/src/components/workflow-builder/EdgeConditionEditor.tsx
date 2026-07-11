import { useState } from 'react'
import type { ConditionOp, WorkflowEdgeCondition } from '../../types/workflow'

const OPS: ConditionOp[] = ['eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', 'contains']

interface EdgeConditionEditorProps {
  edgeId: string
  condition: WorkflowEdgeCondition | null | undefined
  onChange: (condition: WorkflowEdgeCondition | null) => void
  onClose: () => void
}

export function EdgeConditionEditor({ edgeId, condition, onChange, onClose }: EdgeConditionEditorProps) {
  const [field, setField] = useState(condition?.field ?? '')
  const [op, setOp] = useState<ConditionOp>(condition?.op ?? 'eq')
  const [value, setValue] = useState(condition?.value !== undefined ? String(condition.value) : '')

  function apply() {
    if (!field.trim()) {
      onChange(null)
    } else {
      let parsedValue: unknown = value
      try {
        parsedValue = JSON.parse(value)
      } catch {
        // keep as raw string if not valid JSON (e.g. bare word like "high")
      }
      onChange({ field, op, value: parsedValue })
    }
    onClose()
  }

  function clear() {
    onChange(null)
    onClose()
  }

  return (
    <div className="card edge-condition-editor">
      <h3>Edge condition: {edgeId}</h3>
      <p style={{ fontSize: 12 }}>
        Leave field blank for an unconditional edge. Field paths look like{' '}
        <code>$.nodes.n1.risk_level</code>.
      </p>
      <label>
        Field
        <input value={field} onChange={(e) => setField(e.target.value)} placeholder="$.nodes.n1.risk_level" />
      </label>
      <label>
        Operator
        <select value={op} onChange={(e) => setOp(e.target.value as ConditionOp)}>
          {OPS.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      </label>
      <label>
        Value (JSON, e.g. "high" or 3)
        <input value={value} onChange={(e) => setValue(e.target.value)} placeholder='"high"' />
      </label>
      <div className="modal-actions">
        <button onClick={clear}>Clear</button>
        <button onClick={onClose}>Cancel</button>
        <button className="primary" onClick={apply}>
          Apply
        </button>
      </div>
    </div>
  )
}
