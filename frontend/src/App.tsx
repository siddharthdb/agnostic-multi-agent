import { NavLink, Route, Routes } from 'react-router-dom'
import { AgentsPage } from './pages/AgentsPage'
import { WorkflowsListPage } from './pages/WorkflowsListPage'
import { WorkflowBuilderPage } from './pages/WorkflowBuilderPage'
import { ExecutionsListPage } from './pages/ExecutionsListPage'
import { ExecutionDetailPage } from './pages/ExecutionDetailPage'

function App() {
  return (
    <div className="app-shell">
      <nav className="app-nav">
        <span className="app-title">Multi-Agent Orchestrator</span>
        <NavLink to="/agents" className={({ isActive }) => (isActive ? 'active' : '')}>
          Agents
        </NavLink>
        <NavLink to="/workflows" className={({ isActive }) => (isActive ? 'active' : '')}>
          Workflows
        </NavLink>
        <NavLink to="/executions" className={({ isActive }) => (isActive ? 'active' : '')}>
          Executions
        </NavLink>
      </nav>
      <main className="app-content">
        <Routes>
          <Route path="/" element={<AgentsPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/workflows" element={<WorkflowsListPage />} />
          <Route path="/workflows/:workflowId" element={<WorkflowBuilderPage />} />
          <Route path="/executions" element={<ExecutionsListPage />} />
          <Route path="/executions/:executionId" element={<ExecutionDetailPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
