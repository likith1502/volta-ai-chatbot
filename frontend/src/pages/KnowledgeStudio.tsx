import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BookOpen, Search } from 'lucide-react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { getRAGSources, queryRAG, getRAGStatistics } from '../api/knowledge'

export const KnowledgeStudio: React.FC = () => {
  const [queryText, setQueryText] = useState('')
  const [queryResults, setQueryResults] = useState<any>(null)
  const [isQuerying, setIsQuerying] = useState(false)

  const { data: sources, isLoading } = useQuery({
    queryKey: ['ragSources'],
    queryFn: getRAGSources,
  })

  const { data: stats } = useQuery({
    queryKey: ['ragStats'],
    queryFn: getRAGStatistics,
  })

  const sourceList = Array.isArray(sources?.data) ? sources.data : Array.isArray(sources) ? sources : []

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!queryText.trim()) return
    setIsQuerying(true)
    try {
      const res = await queryRAG(queryText)
      setQueryResults(res)
    } catch (err: any) {
      setQueryResults({ error: err.message || 'RAG retrieval failed' })
    } finally {
      setIsQuerying(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Knowledge Studio (RAG)</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Inspect RAG knowledge sources, document chunking, semantic retrieval, and reranking pipelines (v7.6)
        </p>
      </div>

      {/* RAG Retrieval Test */}
      <Card title="Semantic Retrieval Playground">
        <form onSubmit={handleQuery} className="flex gap-3">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Enter retrieval query..."
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:border-indigo-500"
            />
          </div>
          <button
            type="submit"
            disabled={isQuerying || !queryText.trim()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-colors"
          >
            {isQuerying ? 'Retrieving...' : 'Execute Retrieval'}
          </button>
        </form>

        {queryResults && (
          <div className="mt-4">
            <JsonInspector data={queryResults} title="Retrieval Results Payload" />
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Registered Knowledge Sources" className="lg:col-span-2">
          {isLoading ? (
            <Skeleton rows={4} />
          ) : sourceList.length === 0 ? (
            <div className="text-xs text-slate-500 p-4">No active knowledge sources registered</div>
          ) : (
            <div className="space-y-3">
              {sourceList.map((src: any, i: number) => (
                <div
                  key={i}
                  className="p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-lg flex items-center justify-between"
                >
                  <div className="flex items-center gap-2">
                    <BookOpen size={16} className="text-indigo-500" />
                    <span className="text-xs font-medium text-slate-800 dark:text-slate-200">
                      {src.name || src.id || `source_${i}`}
                    </span>
                  </div>
                  <Badge variant="info">{src.chunks_count ? `${src.chunks_count} Chunks` : 'Indexed'}</Badge>
                </div>
              ))}
            </div>
          )}
        </Card>

        <div>
          <Card title="RAG Pipeline Statistics">
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
