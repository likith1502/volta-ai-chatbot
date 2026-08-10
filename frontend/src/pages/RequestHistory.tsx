import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card } from '../components/common/Card'
import { Skeleton } from '../components/common/Skeleton'
import { EmptyState } from '../components/feedback/EmptyState'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { getExecutionHistory } from '../api/runtime'

export const RequestHistory: React.FC = () => {
  const { data: history, isLoading } = useQuery({
    queryKey: ['requestHistory'],
    queryFn: getExecutionHistory,
    refetchInterval: 30000,
  })

  const historyList = Array.isArray(history?.data) ? history.data : Array.isArray(history) ? history : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Request Execution History</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Audit execution requests, duration, model parameters, and runtime execution logs
        </p>
      </div>

      <Card title={`Execution Records (${historyList.length})`}>
        {isLoading ? (
          <Skeleton rows={5} />
        ) : historyList.length === 0 ? (
          <EmptyState title="No Execution History" description="No requests have been executed yet in the runtime engine." />
        ) : (
          <div className="space-y-4">
            <JsonInspector data={historyList} title="Raw Execution History Payload" />
          </div>
        )}
      </Card>
    </div>
  )
}
