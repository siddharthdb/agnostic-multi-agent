import type { ValidationResult } from '../../types/workflow'

export function ValidationPanel({ result }: { result: ValidationResult | null }) {
  if (!result) return null

  return (
    <div className={`card validation-panel ${result.valid ? 'valid' : 'invalid'}`}>
      <strong>{result.valid ? 'Valid workflow' : 'Invalid workflow'}</strong>
      {result.errors.length > 0 && (
        <ul className="validation-list errors">
          {result.errors.map((issue, i) => (
            <li key={i}>
              <span className="badge danger">{issue.code}</span> {issue.message}
            </li>
          ))}
        </ul>
      )}
      {result.warnings.length > 0 && (
        <ul className="validation-list warnings">
          {result.warnings.map((issue, i) => (
            <li key={i}>
              <span className="badge warning">{issue.code}</span> {issue.message}
            </li>
          ))}
        </ul>
      )}
      {result.valid && result.topo_order.length > 0 && (
        <p style={{ fontSize: 12, marginTop: 8 }}>
          Execution order: {result.topo_order.join(' → ')}
        </p>
      )}
    </div>
  )
}
