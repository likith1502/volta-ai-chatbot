import React from 'react'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">System Settings & Configuration</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Configure controlled polling intervals, API base paths, theme preferences, and RBAC permissions
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Controlled Polling Configuration">
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-lg">
              <span className="font-medium text-slate-700 dark:text-slate-300">Health Polling Interval</span>
              <Badge variant="info">10 Seconds</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-lg">
              <span className="font-medium text-slate-700 dark:text-slate-300">Runtime Metrics Polling</span>
              <Badge variant="info">15 Seconds</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-lg">
              <span className="font-medium text-slate-700 dark:text-slate-300">Integration Health Polling</span>
              <Badge variant="info">30 Seconds</Badge>
            </div>
          </div>
        </Card>

        <Card title="Security & RBAC Configuration">
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-lg">
              <span className="font-medium text-slate-700 dark:text-slate-300">Active Role</span>
              <Badge variant="success">Admin / Full Access</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-lg">
              <span className="font-medium text-slate-700 dark:text-slate-300">Secret Redaction Engine</span>
              <Badge variant="success">sk-*** Enabled</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-lg">
              <span className="font-medium text-slate-700 dark:text-slate-300">Legacy UI Mount</span>
              <Badge variant="neutral">Active at /console</Badge>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
