import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Play, FileText } from 'lucide-react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { getPromptTemplates, getPromptProfiles, renderPromptTemplate } from '../api/prompts'

export const PromptStudio: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [variablesInput, setVariablesInput] = useState<string>('{\n  "user_name": "Valued User"\n}')
  const [renderResult, setRenderResult] = useState<any>(null)
  const [isRendering, setIsRendering] = useState(false)

  const { data: templates, isLoading: loadingTemplates } = useQuery({
    queryKey: ['promptTemplates'],
    queryFn: getPromptTemplates,
  })

  const { data: profiles, isLoading: loadingProfiles } = useQuery({
    queryKey: ['promptProfiles'],
    queryFn: getPromptProfiles,
  })

  const templateList = Array.isArray(templates?.data) ? templates.data : Array.isArray(templates) ? templates : []

  const handleRender = async () => {
    if (!selectedTemplate) return
    setIsRendering(true)
    try {
      const parsedVars = JSON.parse(variablesInput)
      const res = await renderPromptTemplate(selectedTemplate, parsedVars)
      setRenderResult(res)
    } catch (e: any) {
      setRenderResult({ error: e.message || 'Invalid variables JSON or rendering failed' })
    } finally {
      setIsRendering(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Prompt Studio</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Inspect registered prompt templates, prompt profiles, variable schemas, and render templates
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Templates List */}
        <Card title="Registered Prompt Templates" className="lg:col-span-1">
          {loadingTemplates ? (
            <Skeleton rows={4} />
          ) : templateList.length === 0 ? (
            <div className="text-xs text-slate-500 p-4">No prompt templates registered</div>
          ) : (
            <div className="space-y-2">
              {templateList.map((tpl: any, idx: number) => {
                const id = tpl.id || tpl.name || `template_${idx}`
                const isSelected = selectedTemplate === id

                return (
                  <button
                    key={idx}
                    onClick={() => setSelectedTemplate(id)}
                    className={`w-full text-left p-3 rounded-lg border text-xs transition-colors flex items-center justify-between ${
                      isSelected
                        ? 'bg-indigo-50 dark:bg-indigo-950/40 border-indigo-500 text-indigo-900 dark:text-indigo-200 font-semibold'
                        : 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileText size={16} className="shrink-0 text-indigo-500" />
                      <span className="truncate">{id}</span>
                    </div>
                    <Badge variant="info">v1.0</Badge>
                  </button>
                )
              })}
            </div>
          )}
        </Card>

        {/* Template Inspector & Renderer */}
        <div className="lg:col-span-2 space-y-6">
          <Card title="Template Renderer & Variable Playground">
            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Selected Template ID:
                </label>
                <input
                  type="text"
                  readOnly
                  value={selectedTemplate || 'Select a template from the list'}
                  className="w-full px-3 py-1.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-md font-mono"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Variables (JSON):
                </label>
                <textarea
                  rows={4}
                  value={variablesInput}
                  onChange={(e) => setVariablesInput(e.target.value)}
                  className="w-full p-3 font-mono text-xs bg-slate-950 text-slate-100 border border-slate-800 rounded-md focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                disabled={!selectedTemplate || isRendering}
                onClick={handleRender}
                className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg font-semibold transition-colors shadow-xs"
              >
                <Play size={14} />
                <span>{isRendering ? 'Rendering...' : 'Render Prompt'}</span>
              </button>
            </div>
          </Card>

          {renderResult && (
            <JsonInspector data={renderResult} title="Render Result Payload" />
          )}

          <Card title="Prompt Profiles Overview">
            {loadingProfiles ? (
              <Skeleton rows={2} />
            ) : (
              <JsonInspector data={profiles} title="Profiles Registry Data" />
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
