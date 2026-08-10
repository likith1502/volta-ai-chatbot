import React from 'react'

interface SkeletonProps {
  className?: string
  rows?: number
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = 'h-6 w-full', rows = 1 }) => {
  if (rows > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: rows }).map((_, i) => (
          <div
            key={i}
            className={`animate-pulse bg-slate-200 dark:bg-slate-800 rounded ${className}`}
          />
        ))}
      </div>
    )
  }

  return <div className={`animate-pulse bg-slate-200 dark:bg-slate-800 rounded ${className}`} />
}
