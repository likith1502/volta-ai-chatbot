import { Component, type ErrorInfo, type ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: ReactNode
  fallbackTitle?: string
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Subsystem UI Error Boundary caught an error:', error, errorInfo)
  }

  public handleReset = () => {
    this.setState({ hasError: false, error: undefined })
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 rounded-lg border border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-950/20 text-red-800 dark:text-red-300 flex flex-col gap-2">
          <div className="flex items-center gap-2 font-medium">
            <AlertTriangle size={18} className="text-red-600 dark:text-red-400" />
            <span>{this.props.fallbackTitle || 'Subsystem API Error'}</span>
          </div>
          <p className="text-xs text-red-600 dark:text-red-400">
            {this.state.error?.message || 'Failed to load subsystem component data.'}
          </p>
          <button
            onClick={this.handleReset}
            className="self-start flex items-center gap-1.5 px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-medium transition-colors"
          >
            <RefreshCw size={12} />
            <span>Retry Subsystem</span>
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
