import { useParams } from 'react-router-dom'

export function ExecutionDetailPage() {
  const { executionId } = useParams<{ executionId: string }>()
  return (
    <div className="page">
      <h1>Execution {executionId}</h1>
    </div>
  )
}
