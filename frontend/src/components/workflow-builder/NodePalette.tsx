import type { Agent } from '../../types/agent'

interface NodePaletteProps {
  agents: Agent[]
}

export function NodePalette({ agents }: NodePaletteProps) {
  function handleDragStart(e: React.DragEvent, agent: Agent) {
    e.dataTransfer.setData('application/x-agent-id', agent.id)
    e.dataTransfer.setData('application/x-agent-name', agent.name)
    e.dataTransfer.setData('application/x-agent-protocol', agent.protocol)
    e.dataTransfer.effectAllowed = 'move'
  }

  if (agents.length === 0) {
    return (
      <div className="node-palette">
        <h3>Agents</h3>
        <p style={{ fontSize: 13 }}>No agents registered. Add one on the Agents page first.</p>
      </div>
    )
  }

  return (
    <div className="node-palette">
      <h3>Agents</h3>
      <p style={{ fontSize: 12, marginBottom: 8 }}>Drag onto the canvas to add a node.</p>
      {agents.map((agent) => (
        <div
          key={agent.id}
          className="node-palette-item"
          draggable
          onDragStart={(e) => handleDragStart(e, agent)}
        >
          <strong>{agent.name}</strong>
          <span>{agent.protocol}</span>
        </div>
      ))}
    </div>
  )
}
