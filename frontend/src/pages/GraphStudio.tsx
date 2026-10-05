import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Play } from 'lucide-react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { getGraphHealth, executeGraph, getGraphStatistics, getGraphAnalytics } from '../api/graphs'

export const GraphStudio: React.FC = () => {
  const [graphId, setGraphId] = useState('workflow_chat_graph')
  const [initialStateInput, setInitialStateInput] = useState('{\n  "messages": []\n}')
  const [execResult, setExecResult] = useState<any>(null)
  const [isExecuting, setIsExecuting] = useState(false)

  const { data: health, isLoading: loadingHealth } = useQuery({
    queryKey: ['graphHealth'],
    queryFn: getGraphHealth,
  })

  const { data: stats } = useQuery({
    queryKey: ['graphStats'],
    queryFn: getGraphStatistics,
  })

  const { data: analytics } = useQuery({
    queryKey: ['graphAnalytics'],
    queryFn: getGraphAnalytics,
  })

  const handleExecute = async () => {
    if (!graphId) return
    setIsExecuting(true)
    try {
      const parsedState = JSON.parse(initialStateInput)
      const res = await executeGraph(graphId, parsedState)
      setExecResult(res)
    } catch (e: any) {
      setExecResult({ error: e.message || 'Graph execution failed' })
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Graph Studio (State Runtime)</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Inspect Graph State Runtime, state transitions, conditional edges, and execution nodes (v7.4)
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Graph Workflow Runner" className="lg:col-span-2">
          <div className="space-y-4 text-xs">
            <div>
              <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                Target Graph ID:
              </label>
              <input
                type="text"
                value={graphId}
                onChange={(e) => setGraphId(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-md font-mono"
              />
            </div>

            <div>
              <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                Initial State Payload (JSON):
              </label>
              <textarea
                rows={4}
                value={initialStateInput}
                onChange={(e) => setInitialStateInput(e.target.value)}
                className="w-full p-3 font-mono text-xs bg-slate-950 text-slate-100 border border-slate-800 rounded-md focus:outline-none focus:border-indigo-500"
              />
            </div>

            <button
              disabled={!graphId || isExecuting}
              onClick={handleExecute}
              className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg font-semibold transition-colors"
            >
              <Play size={14} />
              <span>{isExecuting ? 'Executing Graph...' : 'Run Graph Workflow'}</span>
            </button>
          </div>

          {execResult && (
            <div className="mt-4">
              <JsonInspector data={execResult} title="Execution State Transitions" />
            </div>
          )}
        </Card>

        <div className="space-y-6">
          <Card title="Graph Subsystem Health">
            {loadingHealth ? (
              <Skeleton rows={2} />
            ) : health ? (
              <JsonInspector data={health} title="Health State" />
            ) : (
              <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
                <span className="text-xs text-slate-500">Subsystem Health</span>
                <Badge variant="unavailable">Unavailable</Badge>
              </div>
            )}
          </Card>

          <Card title="Graph System Statistics">
            {stats ? (
              <JsonInspector data={stats} title="Statistics Payload" />
            ) : (
              <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
                <span className="text-xs text-slate-500">Statistics</span>
                <Badge variant="unavailable">Unavailable</Badge>
              </div>
            )}
          </Card>

          {analytics && (
            <Card title="Graph Analytics">
              <JsonInspector data={analytics} title="Analytics Payload" />
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
