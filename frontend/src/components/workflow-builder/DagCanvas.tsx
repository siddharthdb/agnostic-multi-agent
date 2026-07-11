import { useCallback, useRef, useState, useEffect } from 'react'
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
  type Connection,
  type Edge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { AgentNode, type AgentNodeType, type AgentNodeData } from './AgentNode'
import { EdgeConditionEditor } from './EdgeConditionEditor'
import { NodePalette } from './NodePalette'
import type { Agent } from '../../types/agent'
import type { WorkflowDefinition, WorkflowEdgeCondition, WorkflowNode } from '../../types/workflow'

const nodeTypes = { agentNode: AgentNode }

interface WorkflowEdgeData {
  condition?: WorkflowEdgeCondition | null
  [key: string]: unknown
}

type FlowEdge = Edge<WorkflowEdgeData>

function edgeLabel(condition: WorkflowEdgeCondition | null | undefined): string | undefined {
  if (!condition) return undefined
  return `${condition.field} ${condition.op} ${JSON.stringify(condition.value)}`
}

function definitionToFlow(
  definition: WorkflowDefinition,
  agents: Agent[],
): { nodes: AgentNodeType[]; edges: FlowEdge[] } {
  const agentsById = new Map(agents.map((a) => [a.id, a]))
  const nodes: AgentNodeType[] = definition.nodes.map((n, i) => {
    const agent = agentsById.get(n.agent_id)
    const position = n.position ?? { x: 80 + (i % 4) * 220, y: 80 + Math.floor(i / 4) * 140 }
    return {
      id: n.id,
      type: 'agentNode',
      position,
      data: {
        agentId: n.agent_id,
        agentName: agent?.name ?? n.agent_id,
        protocol: agent?.protocol ?? '?',
        label: n.label,
        inputMapping: n.input_mapping ?? {},
      },
    }
  })
  const edges: FlowEdge[] = definition.edges.map((e) => ({
    id: `${e.from}->${e.to}`,
    source: e.from,
    target: e.to,
    label: edgeLabel(e.condition),
    data: { condition: e.condition ?? null },
  }))
  return { nodes, edges }
}

function flowToDefinition(nodes: AgentNodeType[], edges: FlowEdge[]): WorkflowDefinition {
  return {
    nodes: nodes.map(
      (n): WorkflowNode => ({
        id: n.id,
        agent_id: n.data.agentId,
        label: n.data.label,
        input_mapping: (n.data.inputMapping as Record<string, string>) ?? {},
        position: n.position,
      }),
    ),
    edges: edges.map((e) => ({
      from: e.source,
      to: e.target,
      condition: e.data?.condition ?? null,
    })),
  }
}

function nextNodeId(nodes: AgentNodeType[]): string {
  const used = new Set(nodes.map((n) => n.id))
  let i = nodes.length + 1
  while (used.has(`n${i}`)) i += 1
  return `n${i}`
}

interface DagCanvasProps {
  initialDefinition: WorkflowDefinition
  agents: Agent[]
  onChange: (definition: WorkflowDefinition) => void
}

function DagCanvasInner({ initialDefinition, agents, onChange }: DagCanvasProps) {
  const initial = definitionToFlow(initialDefinition, agents)
  const [nodes, setNodes, onNodesChange] = useNodesState<AgentNodeType>(initial.nodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState<FlowEdge>(initial.edges)
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)
  const rfInstance = useReactFlow()

  useEffect(() => {
    onChange(flowToDefinition(nodes, edges))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes, edges])

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) =>
        addEdge<FlowEdge>({ ...connection, data: { condition: null } }, eds),
      )
    },
    [setEdges],
  )

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()
      const agentId = event.dataTransfer.getData('application/x-agent-id')
      const agentName = event.dataTransfer.getData('application/x-agent-name')
      const protocol = event.dataTransfer.getData('application/x-agent-protocol')
      if (!agentId) return
      const position = rfInstance.screenToFlowPosition({ x: event.clientX, y: event.clientY })
      setNodes((nds) => {
        const id = nextNodeId(nds)
        const data: AgentNodeData = { agentId, agentName, protocol, inputMapping: {} }
        return nds.concat({ id, type: 'agentNode', position, data })
      })
    },
    [rfInstance, setNodes],
  )

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const selectedEdge = edges.find((e) => e.id === selectedEdgeId) ?? null

  function updateEdgeCondition(condition: WorkflowEdgeCondition | null) {
    if (!selectedEdgeId) return
    setEdges((eds) =>
      eds.map((e) =>
        e.id === selectedEdgeId ? { ...e, data: { condition }, label: edgeLabel(condition) } : e,
      ),
    )
  }

  return (
    <div className="dag-builder">
      <NodePalette agents={agents} />
      <div className="dag-canvas" ref={wrapperRef} onDrop={onDrop} onDragOver={onDragOver}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onEdgeClick={(_, edge) => setSelectedEdgeId(edge.id)}
          onPaneClick={() => setSelectedEdgeId(null)}
          deleteKeyCode={['Backspace', 'Delete']}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>
      {selectedEdge && (
        <EdgeConditionEditor
          edgeId={selectedEdge.id}
          condition={selectedEdge.data?.condition}
          onChange={updateEdgeCondition}
          onClose={() => setSelectedEdgeId(null)}
        />
      )}
    </div>
  )
}

export function DagCanvas(props: DagCanvasProps) {
  return (
    <ReactFlowProvider>
      <DagCanvasInner {...props} />
    </ReactFlowProvider>
  )
}
