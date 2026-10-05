import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { getDeploymentEnvironment, getDeploymentHealth, getDeploymentAnalytics } from '../api/operations'

export const OperationsStudio: React.FC = () => {
  const { data: env, isLoading: loadingEnv } = useQuery({
    queryKey: ['deployEnv'],
    queryFn: getDeploymentEnvironment,
  })

  const { data: health, isLoading: loadingHealth } = useQuery({
    queryKey: ['deployHealth'],
    queryFn: getDeploymentHealth,
  })

  const { data: analytics } = useQuery({
    queryKey: ['deployAnalytics'],
    queryFn: getDeploymentAnalytics,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Operations Studio</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Deployment operations, scaling status, environment configuration, and release health (v7.8)
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Environment & Release Configuration" className="lg:col-span-2">
          {loadingEnv ? (
            <Skeleton rows={4} />
          ) : env ? (
            <JsonInspector data={env} title="Environment Config Payload" />
          ) : (
            <div className="text-xs text-slate-500 p-2">Environment settings unavailable</div>
          )}
        </Card>

        <div className="space-y-6">
          <Card title="Deployment Operational Health">
            {loadingHealth ? (
              <Skeleton rows={2} />
            ) : health ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500">Status</span>
                  <Badge variant="success">Green / Ready</Badge>
                </div>
                <JsonInspector data={health} title="Health Details" />
              </div>
            ) : (
              <div className="text-xs text-slate-500 p-2">Health report unavailable</div>
            )}
          </Card>

          <Card title="Operational Analytics">
            {analytics ? (
              <JsonInspector data={analytics} title="Analytics Payload" />
            ) : (
              <div className="text-xs text-slate-500 p-2">Operational analytics unavailable</div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
