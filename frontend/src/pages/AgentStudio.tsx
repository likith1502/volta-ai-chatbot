import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bot } from 'lucide-react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Skeleton } from '../components/common/Skeleton'
import { JsonInspector } from '../components/inspector/JsonInspector'
import { getAgents, getAgentHealth, getAgentStatistics } from '../api/agents'

export const AgentStudio: React.FC = () => {
  const { data: agents, isLoading } = useQuery({
    queryKey: ['agentsList'],
    queryFn: getAgents,
  })

  const { data: health } = useQuery({
    queryKey: ['agentHealth'],
    queryFn: getAgentHealth,
  })

  const { data: stats } = useQuery({
    queryKey: ['agentStats'],
    queryFn: getAgentStatistics,
  })

  const agentList = Array.isArray(agents?.data) ? agents.data : Array.isArray(agents) ? agents : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Agent Studio</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Inspect Multi-Agent Runtime agents, team roles, supervisor orchestration, and health (v7.5)
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card title="Registered Agents Inventory">
            {isLoading ? (
              <Skeleton rows={4} />
            ) : agentList.length === 0 ? (
              <div className="text-xs text-slate-500 p-4">No agents registered</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {agentList.map((agent: any, idx: number) => {
                  const name = agent.name || agent.agent_name || `agent_${idx}`
                  const role = agent.role || agent.type || 'Autonomous Agent'

                  return (
                    <div
                      key={idx}
                      className="p-4 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="p-2 bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 rounded-lg">
                            <Bot size={20} />
                          </div>
                          <div>
                            <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">{name}</h4>
                            <span className="text-[10px] text-slate-500">{role}</span>
                          </div>
                        </div>
                        <Badge variant="success">Ready</Badge>
                      </div>

                      {agent.tools && (
                        <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                          Tools: {Array.isArray(agent.tools) ? agent.tools.join(', ') : String(agent.tools)}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </Card>

          {health && <JsonInspector data={health} title="Agent Subsystem Health" />}
        </div>

        <div>
          <Card title="Agent Statistics & Telemetry">
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
