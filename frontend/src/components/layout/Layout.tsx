import React, { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { Breadcrumbs } from './Breadcrumbs'
import { ErrorBoundary } from '../feedback/ErrorBoundary'

export const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 dark:bg-slate-950 font-sans">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header />
        <Breadcrumbs />

        <main className="flex-1 overflow-y-auto p-6">
          <ErrorBoundary fallbackTitle="Page Layout Subsystem Error">
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}
