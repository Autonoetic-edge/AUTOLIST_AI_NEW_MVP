import api from './api'

// Analytics API service
export const analyticsService = {
  /**
   * Get analytics summary data
   * @returns {Promise} Summary data including counts and rates
   */
  getSummary: async () => {
    try {
      const response = await api.get('/api/analytics/summary')
      return response.data
    } catch (error) {
      console.error('Failed to fetch analytics summary:', error)
      // Return mock data for development
      return {
        total_products: 24,
        mapping_jobs_pending: 3,
        mapping_jobs_needs_input: 5,
        mapping_jobs_completed: 16,
        auto_fill_rate: 0.82,
        recent_activity: [],
      }
    }
  },

  /**
   * Get recent activity log
   * @param {number} limit - Number of items to fetch
   * @returns {Promise} List of recent activities
   */
  getRecentActivity: async (limit = 10) => {
    try {
      const response = await api.get('/api/analytics/activity', {
        params: { limit },
      })
      return response.data
    } catch (error) {
      console.error('Failed to fetch recent activity:', error)
      // Return mock data for development
      return [
        {
          id: 'act_1',
          type: 'mapping_completed',
          message: 'Mapping completed for "Premium Cotton T-Shirt"',
          job_id: 'job_123',
          timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
        },
        {
          id: 'act_2',
          type: 'product_synced',
          message: 'Synced 10 products from Shopify',
          timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
        },
        {
          id: 'act_3',
          type: 'mapping_needs_input',
          message: 'Review needed for "Silk Kurta" mapping',
          job_id: 'job_124',
          timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
        },
        {
          id: 'act_4',
          type: 'export_downloaded',
          message: 'Exported batch of 5 products to XLSX',
          timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
        },
        {
          id: 'act_5',
          type: 'template_ingested',
          message: 'New template "amazon_dress_v1" ingested',
          timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
        },
      ]
    }
  },

  /**
   * Get mapping statistics by status
   * @returns {Promise} Breakdown of mapping jobs by status
   */
  getMappingStats: async () => {
    try {
      const response = await api.get('/api/analytics/mapping-stats')
      return response.data
    } catch (error) {
      console.error('Failed to fetch mapping stats:', error)
      return {
        pending: 3,
        processing: 1,
        needs_user_input: 5,
        ready: 8,
        completed: 16,
        error: 0,
      }
    }
  },

  /**
   * Get confidence distribution data
   * @returns {Promise} Distribution of confidence scores
   */
  getConfidenceDistribution: async () => {
    try {
      const response = await api.get('/api/analytics/confidence-distribution')
      return response.data
    } catch (error) {
      console.error('Failed to fetch confidence distribution:', error)
      return {
        high: 65, // 80-100%
        medium: 25, // 50-79%
        low: 10, // 0-49%
      }
    }
  },
}

export default analyticsService
