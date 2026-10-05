import React, { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from './components/layout/Layout'
import { Skeleton } from './components/common/Skeleton'

const Dashboard = lazy(() => import('./pages/Dashboard').then((m) => ({ default: m.Dashboard })))
const PromptStudio = lazy(() => import('./pages/PromptStudio').then((m) => ({ default: m.PromptStudio })))
const MemoryExplorer = lazy(() => import('./pages/MemoryExplorer').then((m) => ({ default: m.MemoryExplorer })))
const ToolExplorer = lazy(() => import('./pages/ToolExplorer').then((m) => ({ default: m.ToolExplorer })))
const GraphStudio = lazy(() => import('./pages/GraphStudio').then((m) => ({ default: m.GraphStudio })))
const AgentStudio = lazy(() => import('./pages/AgentStudio').then((m) => ({ default: m.AgentStudio })))
const KnowledgeStudio = lazy(() => import('./pages/KnowledgeStudio').then((m) => ({ default: m.KnowledgeStudio })))
const IntegrationStudio = lazy(() => import('./pages/IntegrationStudio').then((m) => ({ default: m.IntegrationStudio })))
const OperationsStudio = lazy(() => import('./pages/OperationsStudio').then((m) => ({ default: m.OperationsStudio })))
const RequestHistory = lazy(() => import('./pages/RequestHistory').then((m) => ({ default: m.RequestHistory })))
const ErrorViewer = lazy(() => import('./pages/ErrorViewer').then((m) => ({ default: m.ErrorViewer })))
const Settings = lazy(() => import('./pages/Settings').then((m) => ({ default: m.Settings })))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
})

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense
          fallback={
            <div className="p-8 space-y-4">
              <Skeleton rows={6} />
            </div>
          }
        >
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="prompts" element={<PromptStudio />} />
              <Route path="memory" element={<MemoryExplorer />} />
              <Route path="tools" element={<ToolExplorer />} />
              <Route path="graphs" element={<GraphStudio />} />
              <Route path="agents" element={<AgentStudio />} />
              <Route path="knowledge" element={<KnowledgeStudio />} />
              <Route path="integrations" element={<IntegrationStudio />} />
              <Route path="operations" element={<OperationsStudio />} />
              <Route path="requests" element={<RequestHistory />} />
              <Route path="errors" element={<ErrorViewer />} />
              <Route path="settings" element={<Settings />} />
              <Route path="*" element={<Dashboard />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
