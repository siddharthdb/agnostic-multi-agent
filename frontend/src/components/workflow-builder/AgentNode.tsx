import { Handle, Position, type NodeProps, type Node } from '@xyflow/react'

export interface AgentNodeData {
  agentId: string
  agentName: string
  protocol: string
  label?: string
  inputMapping?: Record<string, string>
  [key: string]: unknown
}

export type AgentNodeType = Node<AgentNodeData, 'agentNode'>

export function AgentNode({ id, data, selected }: NodeProps<AgentNodeType>) {
  return (
    <div className={`dag-node${selected ? ' selected' : ''}`}>
      <Handle type="target" position={Position.Left} />
      <div className="dag-node-id">{id}</div>
      <div className="dag-node-agent">{data.agentName || '(unknown agent)'}</div>
      <div className="dag-node-protocol">{data.protocol}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
