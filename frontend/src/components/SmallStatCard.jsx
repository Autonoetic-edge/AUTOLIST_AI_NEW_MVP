import { useState, useEffect } from 'react'

export default function SmallStatCard({
  title,
  value,
  change,
  changeType = 'neutral', // 'positive', 'negative', 'neutral'
  icon,
  loading = false,
  format = 'number', // 'number', 'percentage', 'currency'
}) {
  const formatValue = (val) => {
    if (val === null || val === undefined) return '-'

    switch (format) {
      case 'percentage':
        return `${(val * 100).toFixed(1)}%`
      case 'currency':
        return `$${val.toLocaleString()}`
      default:
        return val.toLocaleString()
    }
  }

  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return 'text-emerald-600'
      case 'negative':
        return 'text-red-600'
      default:
        return 'text-gray-500'
    }
  }

  const getChangeIcon = () => {
    switch (changeType) {
      case 'positive':
        return '↑'
      case 'negative':
        return '↓'
      default:
        return ''
    }
  }

  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-16"></div>
          </div>
          <div className="h-12 w-12 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <div className="flex items-baseline mt-1">
            <p className="text-2xl font-bold text-gray-900">
              {formatValue(value)}
            </p>
            {change !== undefined && (
              <span className={`ml-2 text-sm ${getChangeColor()}`}>
                {getChangeIcon()} {change}
              </span>
            )}
          </div>
        </div>
        {icon && (
          <div className="flex-shrink-0 ml-4">
            <div className="h-12 w-12 bg-indigo-50 rounded-lg flex items-center justify-center text-2xl">
              {icon}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Preset variants for common use cases
export function ProductsStatCard({ value, loading }) {
  return (
    <SmallStatCard
      title="Total Products"
      value={value}
      icon="📦"
      loading={loading}
    />
  )
}

export function MappingJobsStatCard({ pending, needsInput, completed, loading }) {
  return (
    <SmallStatCard
      title="Mapping Jobs"
      value={pending + needsInput + completed}
      icon="🗺️"
      loading={loading}
    />
  )
}

export function AutoFillRateCard({ value, loading }) {
  return (
    <SmallStatCard
      title="Auto-Fill Rate"
      value={value}
      format="percentage"
      icon="🤖"
      loading={loading}
    />
  )
}
