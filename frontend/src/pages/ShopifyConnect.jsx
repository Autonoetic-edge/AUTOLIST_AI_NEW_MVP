import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { shopifyAPI } from '../services/api'

export default function ShopifyConnect() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [connected, setConnected] = useState(false)
  const [formData, setFormData] = useState({
    shopDomain: '',
    accessToken: '',
  })

  const handleConnect = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await shopifyAPI.connect(formData.shopDomain, formData.accessToken)
      setSuccess(response.data.message)
      setConnected(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect to Shopify store')
    } finally {
      setLoading(false)
    }
  }

  const handleSync = async () => {
    setSyncing(true)
    setError('')
    setSuccess('')

    try {
      const response = await shopifyAPI.syncProducts(formData.shopDomain)
      setSuccess(`Successfully synced ${response.data.products_count} products!`)

      // Navigate to products page after short delay
      setTimeout(() => {
        navigate('/products')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to sync products')
    } finally {
      setSyncing(false)
    }
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Connect Shopify Store</h1>
        <p className="text-gray-600 mt-1">
          Link your Shopify store to import products for mapping
        </p>
      </div>

      {/* Connection status card */}
      {connected && (
        <div className="card mb-6 bg-emerald-50 border-emerald-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-emerald-800">Store Connected</h3>
              <p className="text-sm text-emerald-700 mt-1">{formData.shopDomain}</p>
            </div>
          </div>
        </div>
      )}

      {/* Main form card */}
      <div className="card">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            <div className="flex">
              <span className="text-red-500 mr-2">⚠️</span>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-lg">
            <div className="flex">
              <span className="mr-2">✨</span>
              <p className="text-sm">{success}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleConnect} className="space-y-6">
          <div>
            <label htmlFor="shopDomain" className="block text-sm font-medium text-gray-700 mb-1">
              Shop Domain
            </label>
            <input
              type="text"
              id="shopDomain"
              name="shopDomain"
              value={formData.shopDomain}
              onChange={handleChange}
              className="input"
              placeholder="mystore.myshopify.com"
              required
              disabled={connected}
            />
            <p className="mt-1 text-xs text-gray-500">
              Your Shopify store domain (e.g., mystore.myshopify.com)
            </p>
          </div>

          <div>
            <label htmlFor="accessToken" className="block text-sm font-medium text-gray-700 mb-1">
              Access Token
            </label>
            <input
              type="password"
              id="accessToken"
              name="accessToken"
              value={formData.accessToken}
              onChange={handleChange}
              className="input"
              placeholder="shpat_xxxxxxxxxxxxx"
              required
              disabled={connected}
            />
            <p className="mt-1 text-xs text-gray-500">
              Your Shopify Admin API access token
            </p>
          </div>

          {!connected ? (
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Connecting...
                </span>
              ) : (
                'Connect Store'
              )}
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSync}
              disabled={syncing}
              className="btn-success w-full py-3"
            >
              {syncing ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Syncing Products...
                </span>
              ) : (
                'Sync Products'
              )}
            </button>
          )}
        </form>
      </div>

      {/* Help section */}
      <div className="mt-8 card bg-gray-50 border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-3">How to get your Access Token</h3>
        <ol className="text-sm text-gray-600 space-y-2 list-decimal list-inside">
          <li>Go to your Shopify Admin → Settings → Apps and sales channels</li>
          <li>Click "Develop apps" → "Create an app"</li>
          <li>Configure Admin API scopes (read_products required)</li>
          <li>Install the app and copy the Admin API access token</li>
        </ol>
      </div>
    </div>
  )
}
