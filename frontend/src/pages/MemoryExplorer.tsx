import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { EmptyState } from '../components/feedback/EmptyState'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { getMemoryRecords, searchMemory, getMemoryStatistics } from '../api/memory'

export const MemoryExplorer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any>(null)
  const [isSearching, setIsSearching] = useState(false)

  const { data: records, isLoading: loadingRecords } = useQuery({
    queryKey: ['memoryRecords'],
    queryFn: () => getMemoryRecords(),
  })

  const { data: stats } = useQuery({
    queryKey: ['memoryStats'],
    queryFn: getMemoryStatistics,
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

  const recordList = Array.isArray(records?.data) ? records.data : Array.isArray(records) ? records : []

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

      {/* Memory Records Table / List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card title="Memory Records Inventory">
            {loadingRecords ? (
              <Skeleton rows={4} />
            ) : recordList.length === 0 ? (
              <EmptyState title="No Memory Records" description="No active memory records found in repository." />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 font-semibold border-b border-slate-200 dark:border-slate-700">
                    <tr>
                      <th className="p-3">ID / Key</th>
                      <th className="p-3">User / Session</th>
                      <th className="p-3">Type</th>
                      <th className="p-3">Content</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                    {recordList.map((rec: any, i: number) => (
                      <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                        <td className="p-3 font-mono font-medium text-indigo-600 dark:text-indigo-400">
                          {rec.id || rec.key || `rec_${i}`}
                        </td>
                        <td className="p-3 text-slate-600 dark:text-slate-300">{rec.user_id || rec.session_id || 'Global'}</td>
                        <td className="p-3">
                          <Badge variant="neutral">{rec.type || 'conversational'}</Badge>
                        </td>
                        <td className="p-3 text-slate-700 dark:text-slate-300 truncate max-w-xs">
                          {typeof rec.content === 'string' ? rec.content : JSON.stringify(rec.content)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        <div>
          <Card title="Memory Subsystem Statistics">
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
