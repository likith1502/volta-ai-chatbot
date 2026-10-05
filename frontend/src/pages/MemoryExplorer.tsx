import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { searchMemory, getMemoryStatistics, getMemoryMetrics } from '../api/memory'

export const MemoryExplorer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any>(null)
  const [isSearching, setIsSearching] = useState(false)

  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['memoryStats'],
    queryFn: getMemoryStatistics,
  })

  const { data: metrics } = useQuery({
    queryKey: ['memoryMetrics'],
    queryFn: getMemoryMetrics,
  })

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return
    setIsSearching(true)
    try {
      const res = await searchMemory(searchQuery)
      setSearchResults(res)
    } catch (err: any) {
      setSearchResults({ error: err.message || 'Search failed' })
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Memory Explorer</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Inspect short-term, long-term, and session memory repositories (v7.2)
        </p>
      </div>

      {/* Memory Search */}
      <Card title="Search Memory Records">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Enter search query..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:border-indigo-500"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching || !searchQuery.trim()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-colors"
          >
            {isSearching ? 'Searching...' : 'Search Memory'}
          </button>
        </form>

        {searchResults && (
          <div className="mt-4">
            <JsonInspector data={searchResults} title="Search Results" />
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Memory Subsystem Statistics">
          {loadingStats ? (
            <Skeleton rows={4} />
          ) : stats ? (
            <JsonInspector data={stats} title="Statistics Payload" />
          ) : (
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
              <span className="text-xs text-slate-500">Statistics State</span>
              <Badge variant="unavailable">Unavailable</Badge>
            </div>
          )}
        </Card>

        <Card title="Memory Metrics & Telemetry">
          {metrics ? (
            <JsonInspector data={metrics} title="Metrics Payload" />
          ) : (
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
              <span className="text-xs text-slate-500">Metrics State</span>
              <Badge variant="unavailable">Unavailable</Badge>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
