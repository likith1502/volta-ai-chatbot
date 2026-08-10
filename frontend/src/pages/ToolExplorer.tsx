import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Wrench, Play } from 'lucide-react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { getRegisteredTools, executeTool, getToolStatistics } from '../api/tools'

export const ToolExplorer: React.FC = () => {
  const [selectedTool, setSelectedTool] = useState<string>('')
  const [paramInput, setParamInput] = useState<string>('{}')
  const [execResult, setExecResult] = useState<any>(null)
  const [isExec, setIsExec] = useState(false)

  const { data: tools, isLoading } = useQuery({
    queryKey: ['registeredTools'],
    queryFn: getRegisteredTools,
  })

  const { data: stats } = useQuery({
    queryKey: ['toolStats'],
    queryFn: getToolStatistics,
  })

  const toolList = Array.isArray(tools?.data) ? tools.data : Array.isArray(tools) ? tools : []

  const handleExecute = async () => {
    if (!selectedTool) return
    setIsExec(true)
    try {
      const params = JSON.parse(paramInput)
      const res = await executeTool(selectedTool, params)
      setExecResult(res)
    } catch (e: any) {
      setExecResult({ error: e.message || 'Tool execution failed' })
    } finally {
      setIsExec(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Tool Explorer</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Inspect registered tool definitions, capabilities, and execute tool pipelines (v7.3)
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Registered Tools Inventory" className="lg:col-span-1">
          {isLoading ? (
            <Skeleton rows={4} />
          ) : toolList.length === 0 ? (
            <div className="text-xs text-slate-500 p-4">No tools registered</div>
          ) : (
            <div className="space-y-2">
              {toolList.map((t: any, i: number) => {
                const name = t.name || t.tool_name || `tool_${i}`
                const isSelected = selectedTool === name

                return (
                  <button
                    key={i}
                    onClick={() => setSelectedTool(name)}
                    className={`w-full text-left p-3 rounded-lg border text-xs transition-colors flex items-center justify-between ${
                      isSelected
                        ? 'bg-indigo-50 dark:bg-indigo-950/40 border-indigo-500 text-indigo-900 dark:text-indigo-200 font-semibold'
                        : 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <Wrench size={16} className="shrink-0 text-indigo-500" />
                      <span className="truncate">{name}</span>
                    </div>
                    <Badge variant="success">Active</Badge>
                  </button>
                )
              })}
            </div>
          )}
        </Card>

        <div className="lg:col-span-2 space-y-6">
          <Card title="Tool Execution Console">
            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Target Tool Name:
                </label>
                <input
                  type="text"
                  readOnly
                  value={selectedTool || 'Select a tool from the list'}
                  className="w-full px-3 py-1.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-md font-mono"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Parameters Payload (JSON):
                </label>
                <textarea
                  rows={4}
                  value={paramInput}
                  onChange={(e) => setParamInput(e.target.value)}
                  className="w-full p-3 font-mono text-xs bg-slate-950 text-slate-100 border border-slate-800 rounded-md focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                disabled={!selectedTool || isExec}
                onClick={handleExecute}
                className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg font-semibold transition-colors"
              >
                <Play size={14} />
                <span>{isExec ? 'Executing...' : 'Execute Tool'}</span>
              </button>
            </div>
          </Card>

          {execResult && <JsonInspector data={execResult} title="Execution Response Payload" />}

          <Card title="Tool System Statistics">
            {stats ? (
              <JsonInspector data={stats} title="Statistics Payload" />
            ) : (
              <div className="text-xs text-slate-500 p-2">Statistics unavailable</div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
