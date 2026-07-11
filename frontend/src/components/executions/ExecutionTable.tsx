import { Link } from 'react-router-dom'
import type { Execution } from '../../types/execution'
import { ExecutionStatusBadge } from './ExecutionStatusBadge'

export function ExecutionTable({ executions }: { executions: Execution[] }) {
  if (executions.length === 0) {
    return <div className="empty-state">No executions yet.</div>
  }

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Workflow</th>
          <th>Status</th>
          <th>Started</th>
          <th>Ended</th>
        </tr>
      </thead>
      <tbody>
        {executions.map((e) => (
          <tr key={e.id}>
            <td>
              <Link to={`/executions/${e.id}`}>
                <code>{e.id}</code>
              </Link>
            </td>
            <td>
              <code>{e.workflow_id}</code>
            </td>
            <td>
              <ExecutionStatusBadge status={e.status} />
            </td>
            <td>{e.started_at ? new Date(e.started_at).toLocaleString() : '—'}</td>
            <td>{e.ended_at ? new Date(e.ended_at).toLocaleString() : '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
