import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  MessageSquare,
  HardDrive,
  Wrench,
  GitFork,
  Bot,
  BookOpen,
  Boxes,
  Activity,
  History,
  AlertTriangle,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react'

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const navSections = [
    {
      title: 'OVERVIEW',
      items: [
        { name: 'Dashboard', path: '/', icon: LayoutDashboard },
      ],
    },
    {
      title: 'AI PLATFORM',
      items: [
        { name: 'Prompt Studio', path: '/prompts', icon: MessageSquare },
        { name: 'Memory Explorer', path: '/memory', icon: HardDrive },
        { name: 'Tool Explorer', path: '/tools', icon: Wrench },
        { name: 'Graph Studio', path: '/graphs', icon: GitFork },
        { name: 'Agent Studio', path: '/agents', icon: Bot },
        { name: 'Knowledge Studio', path: '/knowledge', icon: BookOpen },
      ],
    },
    {
      title: 'PLATFORM',
      items: [
        { name: 'Integration Studio', path: '/integrations', icon: Boxes, badge: '28' },
        { name: 'Operations Studio', path: '/operations', icon: Activity },
      ],
    },
    {
      title: 'OBSERVABILITY',
      items: [
        { name: 'Request History', path: '/requests', icon: History },
        { name: 'Error Viewer', path: '/errors', icon: AlertTriangle },
      ],
    },
    {
      title: 'SETTINGS',
      items: [
        { name: 'System Settings', path: '/settings', icon: Settings },
      ],
    },
  ]

  return (
    <aside
      className={`relative flex flex-col bg-slate-900 text-slate-300 border-r border-slate-800 transition-all duration-300 select-none ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-slate-800 bg-slate-950">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-indigo-600 text-white font-bold text-lg shadow-md shrink-0">
            V
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-white text-base tracking-wide">VOLTA AI</span>
              <span className="text-[10px] text-indigo-400 font-semibold tracking-widest uppercase">Admin Console</span>
            </div>
          )}
        </div>

        <button
          onClick={onToggle}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="p-1 rounded-md hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto py-4 px-2 space-y-6">
        {navSections.map((section, idx) => (
          <div key={idx}>
            {!collapsed && (
              <h4 className="px-3 text-[10px] font-bold text-slate-500 tracking-wider uppercase mb-2">
                {section.title}
              </h4>
            )}
            <nav className="space-y-1" aria-label={section.title}>
              {section.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                        : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                    }`
                  }
                  title={collapsed ? item.name : undefined}
                >
                  <item.icon size={18} className="shrink-0" />
                  {!collapsed && <span className="truncate flex-1">{item.name}</span>}
                  {!collapsed && item.badge && (
                    <span className="px-1.5 py-0.5 text-[10px] font-bold bg-indigo-500/20 text-indigo-400 rounded">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </nav>
          </div>
        ))}
      </div>

      {/* System Status Footer */}
      {!collapsed && (
        <div className="p-3 m-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <ShieldCheck size={16} className="text-emerald-400" />
            <div className="flex flex-col">
              <span className="text-slate-200 font-medium">Platform Ready</span>
              <span className="text-[10px] text-slate-500">v7.8 Production</span>
            </div>
          </div>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        </div>
      )}
    </aside>
  )
}
