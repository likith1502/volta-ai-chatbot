import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { GitFork, Play } from 'lucide-react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { getGraphs, executeGraph, getGraphMetrics } from '../api/graphs'

export const GraphStudio: React.FC = () => {
  const [selectedGraph, setSelectedGraph] = useState<string>('')
  const [initialStateInput, setInitialStateInput] = useState<string>('{\n  "input": "test state"\n}')
  const [execResult, setExecResult] = useState<any>(null)
  const [isExecuting, setIsExecuting] = useState(false)

  const { data: graphs, isLoading } = useQuery({
    queryKey: ['graphs'],
    queryFn: getGraphs,
  })

  const { data: metrics } = useQuery({
    queryKey: ['graphMetrics'],
    queryFn: getGraphMetrics,
  })

  const graphList = Array.isArray(graphs?.data) ? graphs.data : Array.isArray(graphs) ? graphs : []

  const handleExecute = async () => {
    if (!selectedGraph) return
    setIsExecuting(true)
    try {
      const state = JSON.parse(initialStateInput)
      const res = await executeGraph(selectedGraph, state)
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
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Graph Studio</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Inspect Graph State Runtime workflows, state transitions, and node execution graphs (v7.4)
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Registered Workflows" className="lg:col-span-1">
          {isLoading ? (
            <Skeleton rows={4} />
          ) : graphList.length === 0 ? (
            <div className="text-xs text-slate-500 p-4">No active workflow graphs</div>
          ) : (
            <div className="space-y-2">
              {graphList.map((g: any, i: number) => {
                const id = g.id || g.graph_id || g.name || `graph_${i}`
                const isSelected = selectedGraph === id

                return (
                  <button
                    key={i}
                    onClick={() => setSelectedGraph(id)}
                    className={`w-full text-left p-3 rounded-lg border text-xs transition-colors flex items-center justify-between ${
                      isSelected
                        ? 'bg-indigo-50 dark:bg-indigo-950/40 border-indigo-500 text-indigo-900 dark:text-indigo-200 font-semibold'
                        : 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <GitFork size={16} className="shrink-0 text-indigo-500" />
                      <span className="truncate">{id}</span>
                    </div>
                    <Badge variant="neutral">Stateful</Badge>
                  </button>
                )
              })}
            </div>
          )}
        </Card>

        <div className="lg:col-span-2 space-y-6">
          <Card title="Workflow Graph Runner">
            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Selected Graph Workflow:
                </label>
                <input
                  type="text"
                  readOnly
                  value={selectedGraph || 'Select a graph from the list'}
                  className="w-full px-3 py-1.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-md font-mono"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Initial State (JSON):
                </label>
                <textarea
                  rows={4}
                  value={initialStateInput}
                  onChange={(e) => setInitialStateInput(e.target.value)}
                  className="w-full p-3 font-mono text-xs bg-slate-950 text-slate-100 border border-slate-800 rounded-md focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                disabled={!selectedGraph || isExecuting}
                onClick={handleExecute}
                className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg font-semibold transition-colors"
              >
                <Play size={14} />
                <span>{isExecuting ? 'Running Graph...' : 'Execute Graph'}</span>
              </button>
            </div>
          </Card>

          {execResult && <JsonInspector data={execResult} title="Graph State Result" />}

          <Card title="Graph Metrics Payload">
            {metrics ? (
              <JsonInspector data={metrics} title="Metrics Payload" />
            ) : (
              <div className="text-xs text-slate-500 p-2">Metrics unavailable</div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
