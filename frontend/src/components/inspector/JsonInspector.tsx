import React, { useState } from 'react'
import { Copy, Check, Search, ChevronRight, ChevronDown } from 'lucide-react'
import { redactSecrets } from '../../utils/redaction'

interface JsonInspectorProps {
  data: any
  title?: string
  initialExpanded?: boolean
}

export const JsonInspector: React.FC<JsonInspectorProps> = ({
  data,
  title = 'JSON Data',
  initialExpanded = true,
}) => {
  const [copied, setCopied] = useState(false)
  const [search, setSearch] = useState('')
  const [isCollapsed, setIsCollapsed] = useState(!initialExpanded)

  const sanitized = redactSecrets(data)
  const jsonString = JSON.stringify(sanitized, null, 2)

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const highlightMatches = (text: string) => {
    if (!search.trim()) return text
    const parts = text.split(new RegExp(`(${search})`, 'gi'))
    return (
      <>
        {parts.map((part, i) =>
          part.toLowerCase() === search.toLowerCase() ? (
            <mark key={i} className="bg-amber-300 dark:bg-amber-700 dark:text-white px-0.5 rounded">
              {part}
            </mark>
          ) : (
            part
          )
        )}
      </>
    )
  }

  return (
    <div className="border border-slate-200 dark:border-slate-800 rounded-lg overflow-hidden bg-slate-950 text-slate-100 font-mono text-xs shadow-sm">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-900 border-b border-slate-800 select-none">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="flex items-center gap-1.5 font-sans font-medium text-slate-300 hover:text-white transition-colors"
        >
          {isCollapsed ? <ChevronRight size={14} /> : <ChevronDown size={14} />}
          <span>{title}</span>
        </button>

        <div className="flex items-center gap-2">
          <div className="relative flex items-center">
            <Search size={12} className="absolute left-2 text-slate-500" />
            <input
              type="text"
              placeholder="Search JSON..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-6 pr-2 py-0.5 text-xs bg-slate-800 text-slate-200 border border-slate-700 rounded focus:outline-none focus:border-indigo-500 font-sans"
            />
          </div>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded border border-slate-700 transition-colors font-sans"
            title="Copy JSON"
          >
            {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {!isCollapsed && (
        <pre className="p-3 overflow-x-auto max-h-96 leading-relaxed">
          <code>{highlightMatches(jsonString)}</code>
        </pre>
      )}
    </div>
  )
}
