import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (email, password) =>
    api.post('/api/auth/token', { email, password }),

  register: (email, password, name) =>
    api.post('/api/auth/register', { email, password, name }),

  getMe: () =>
    api.get('/api/auth/me'),
}

// Shopify API
export const shopifyAPI = {
  connect: (shopDomain, accessToken) =>
    api.post('/api/shopify/connect', {
      shop_domain: shopDomain,
      access_token: accessToken,
    }),

  syncProducts: (shopDomain) =>
    api.post('/api/shopify/sync-products', { shop_domain: shopDomain }),

  getProducts: (shopDomain, limit = 50, offset = 0) =>
    api.get('/api/shopify/products', {
      params: { shop_domain: shopDomain, limit, offset },
    }),

  getStatus: (shopDomain) =>
    api.get(`/api/shopify/status/${shopDomain}`),
}

// Products API
export const productsAPI = {
  getAll: (params = {}) =>
    api.get('/api/products', { params }),

  getById: (productId) =>
    api.get(`/api/products/${productId}`),

  getCount: (params = {}) =>
    api.get('/api/products/count', { params }),

  delete: (productId) =>
    api.delete(`/api/products/${productId}`),

  getMapping: (productId, schemaId) =>
    api.get(`/api/products/${productId}/mapping`, {
      params: { schema_id: schemaId },
    }),
}

// Mapping API
export const mappingAPI = {
  createJob: (productId, schemaId) =>
    api.post('/api/mapping/jobs', {
      product_id: productId,
      template_schema_id: schemaId,
    }),

  getJob: (jobId) =>
    api.get(`/api/mapping/jobs/${jobId}`),

  updateJob: (jobId, updates) =>
    api.patch(`/api/mapping/jobs/${jobId}`, { updates }),

  approveJob: (jobId) =>
    api.post(`/api/mapping/jobs/${jobId}/approve`),

  getJobs: (params = {}) =>
    api.get('/api/mapping/jobs', { params }),
}

// Templates API
export const templatesAPI = {
  getAll: () =>
    api.get('/api/templates'),

  getById: (schemaId) =>
    api.get(`/api/templates/${schemaId}`),

  ingest: (file, marketplace, category) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('marketplace', marketplace)
    formData.append('category', category)
    return api.post('/api/templates/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// Export API
export const exportAPI = {
  downloadXlsx: (jobId) =>
    api.get(`/api/export/${jobId}/xlsx`, { responseType: 'blob' }),

  downloadBatch: (jobIds) =>
    api.post('/api/export/batch', { job_ids: jobIds }, { responseType: 'blob' }),

  getPreview: (jobId) =>
    api.get(`/api/export/${jobId}/preview`),
}

// Analytics API
export const analyticsAPI = {
  getSummary: () =>
    api.get('/api/analytics/summary'),

  getRecentActivity: (limit = 10) =>
    api.get('/api/analytics/activity', { params: { limit } }),
}

export default api
