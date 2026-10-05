import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { queryRAG, getRAGStatistics, getRAGAnalytics } from '../api/knowledge'

export const KnowledgeStudio: React.FC = () => {
  const [queryText, setQueryText] = useState('')
  const [queryResults, setQueryResults] = useState<any>(null)
  const [isQuerying, setIsQuerying] = useState(false)

  const { data: stats, isLoading } = useQuery({
    queryKey: ['ragStats'],
    queryFn: getRAGStatistics,
  })

  const { data: analytics } = useQuery({
    queryKey: ['ragAnalytics'],
    queryFn: getRAGAnalytics,
  })

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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="RAG Subsystem Telemetry & Statistics">
          {isLoading ? (
            <Skeleton rows={4} />
          ) : stats ? (
            <JsonInspector data={stats} title="RAG Statistics Payload" />
          ) : (
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
              <span className="text-xs text-slate-500">RAG Statistics</span>
              <Badge variant="unavailable">Unavailable</Badge>
            </div>
          )}
        </Card>

        <Card title="RAG Knowledge Pipeline Analytics">
          {analytics ? (
            <JsonInspector data={analytics} title="RAG Analytics Payload" />
          ) : (
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
              <span className="text-xs text-slate-500">Analytics Data</span>
              <Badge variant="unavailable">Unavailable</Badge>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
