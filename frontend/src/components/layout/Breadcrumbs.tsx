import React from 'react'
import { useLocation, Link } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'

export const Breadcrumbs: React.FC = () => {
  const location = useLocation()
  const pathnames = location.pathname.split('/').filter((x) => x)

  const nameMap: Record<string, string> = {
    prompts: 'Prompt Studio',
    memory: 'Memory Explorer',
    tools: 'Tool Explorer',
    graphs: 'Graph Studio',
    agents: 'Agent Studio',
    knowledge: 'Knowledge Studio',
    integrations: 'Integration Studio',
    operations: 'Operations Studio',
    requests: 'Request History',
    errors: 'Error Viewer',
    settings: 'System Settings',
  }

  return (
    <nav className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 py-3 px-6 bg-slate-50/50 dark:bg-slate-900/30 border-b border-slate-200/60 dark:border-slate-800/60 select-none">
      <Link to="/" className="flex items-center gap-1 hover:text-slate-900 dark:hover:text-slate-200 transition-colors">
        <Home size={14} />
        <span>Dashboard</span>
      </Link>

      {pathnames.map((value, index) => {
        const to = `/${pathnames.slice(0, index + 1).join('/')}`
        const isLast = index === pathnames.length - 1
        const title = nameMap[value] || value

        return (
          <React.Fragment key={to}>
            <ChevronRight size={12} className="text-slate-400" />
            {isLast ? (
              <span className="font-semibold text-slate-900 dark:text-slate-100">{title}</span>
            ) : (
              <Link to={to} className="hover:text-slate-900 dark:hover:text-slate-200 transition-colors">
                {title}
              </Link>
            )}
          </React.Fragment>
        )
      })}
    </nav>
  )
}
