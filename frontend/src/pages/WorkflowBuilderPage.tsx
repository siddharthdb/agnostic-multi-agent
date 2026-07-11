import { useParams } from 'react-router-dom'

export function WorkflowBuilderPage() {
  const { workflowId } = useParams<{ workflowId: string }>()
  return (
    <div className="page">
      <h1>Workflow Builder</h1>
      <p>{workflowId === 'new' ? 'New workflow' : `Editing ${workflowId}`}</p>
    </div>
  )
}
