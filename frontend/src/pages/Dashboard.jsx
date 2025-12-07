import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import SmallStatCard from '../components/SmallStatCard'
import analyticsService from '../services/analytics.service'

// Activity type icons
const activityIcons = {
  mapping_completed: '✅',
  product_synced: '📦',
  mapping_needs_input: '⚠️',
  export_downloaded: '📥',
  template_ingested: '📋',
  error: '❌',
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState({
    total_products: 0,
    mapping_jobs_pending: 0,
    mapping_jobs_needs_input: 0,
    mapping_jobs_completed: 0,
    auto_fill_rate: 0,
  })
  const [recentActivity, setRecentActivity] = useState([])

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      const [summaryData, activityData] = await Promise.all([
        analyticsService.getSummary(),
        analyticsService.getRecentActivity(10),
      ])
      setSummary(summaryData)
      setRecentActivity(activityData)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatTimeAgo = (timestamp) => {
    const now = new Date()
    const then = new Date(timestamp)
    const diff = Math.floor((now - then) / 1000)

    if (diff < 60) return 'Just now'
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
    return `${Math.floor(diff / 86400)}d ago`
  }

  const totalJobs = summary.mapping_jobs_pending + summary.mapping_jobs_needs_input + summary.mapping_jobs_completed

  return (
    <div>
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Overview of your product mapping activity
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SmallStatCard
          title="Total Products"
          value={summary.total_products}
          icon="📦"
          loading={loading}
        />
        <SmallStatCard
          title="Pending Jobs"
          value={summary.mapping_jobs_pending}
          icon="⏳"
          loading={loading}
        />
        <SmallStatCard
          title="Needs Review"
          value={summary.mapping_jobs_needs_input}
          icon="👁️"
          loading={loading}
        />
        <SmallStatCard
          title="Completed"
          value={summary.mapping_jobs_completed}
          icon="✅"
          loading={loading}
        />
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Auto-fill rate card */}
        <div className="card lg:col-span-1">
          <h3 className="text-sm font-medium text-gray-500 mb-4">Auto-Fill Rate</h3>

          {/* Progress circle */}
          <div className="flex justify-center mb-4">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  fill="none"
                  stroke="#E5E7EB"
                  strokeWidth="12"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  fill="none"
                  stroke="#4F46E5"
                  strokeWidth="12"
                  strokeDasharray={`${summary.auto_fill_rate * 351.86} 351.86`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-900">
                  {loading ? '-' : `${(summary.auto_fill_rate * 100).toFixed(0)}%`}
                </span>
              </div>
            </div>
          </div>

          <p className="text-center text-sm text-gray-600">
            Average confidence across all mappings
          </p>

          {/* Progress bar breakdown */}
          <div className="mt-6 space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">High confidence</span>
              <span className="font-medium text-emerald-600">65%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '65%' }}></div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Medium confidence</span>
              <span className="font-medium text-amber-600">25%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-amber-500 h-2 rounded-full" style={{ width: '25%' }}></div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Low confidence</span>
              <span className="font-medium text-red-600">10%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-red-500 h-2 rounded-full" style={{ width: '10%' }}></div>
            </div>
          </div>
        </div>

        {/* Recent activity */}
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500">Recent Activity</h3>
            <button
              onClick={loadDashboardData}
              className="text-sm text-indigo-600 hover:text-indigo-700"
            >
              Refresh
            </button>
          </div>

          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center space-x-3 animate-pulse">
                  <div className="w-8 h-8 bg-gray-200 rounded-lg"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/4"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : recentActivity.length > 0 ? (
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => {
                    if (activity.job_id) {
                      navigate(`/mapping/${activity.job_id}`)
                    }
                  }}
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                    <span>{activityIcons[activity.type] || '📌'}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatTimeAgo(activity.timestamp)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <span className="text-4xl">📋</span>
              <p className="text-gray-500 mt-2">No recent activity</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => navigate('/connect')}
          className="card-hover flex items-center p-4 text-left"
        >
          <div className="text-2xl mr-4">🔗</div>
          <div>
            <p className="font-medium text-gray-900">Connect Store</p>
            <p className="text-sm text-gray-500">Link your Shopify store</p>
          </div>
        </button>

        <button
          onClick={() => navigate('/products')}
          className="card-hover flex items-center p-4 text-left"
        >
          <div className="text-2xl mr-4">🗺️</div>
          <div>
            <p className="font-medium text-gray-900">Start Mapping</p>
            <p className="text-sm text-gray-500">Map products to templates</p>
          </div>
        </button>

        <button
          onClick={() => navigate('/download')}
          className="card-hover flex items-center p-4 text-left"
        >
          <div className="text-2xl mr-4">📥</div>
          <div>
            <p className="font-medium text-gray-900">Download Exports</p>
            <p className="text-sm text-gray-500">Get your completed mappings</p>
          </div>
        </button>
      </div>
    </div>
  )
}
