import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { productsAPI, templatesAPI, mappingAPI } from '../services/api'

// Sample products for demo
const SAMPLE_PRODUCTS = [
  {
    id: 'prod_1',
    title: 'Premium Cotton T-Shirt - Blue',
    product_type: 'Shirt',
    vendor: 'AutoList Fashion',
    variants_count: 3,
    images: [{ src: 'https://via.placeholder.com/80' }],
    status: 'active',
  },
  {
    id: 'prod_2',
    title: 'Traditional Silk Kurta - Maroon',
    product_type: 'Kurta',
    vendor: 'AutoList Fashion',
    variants_count: 2,
    images: [{ src: 'https://via.placeholder.com/80' }],
    status: 'active',
  },
]

// Sample templates for demo
const SAMPLE_TEMPLATES = [
  { schema_id: 'amazon_shirt_v1', marketplace: 'amazon', category: 'shirt' },
  { schema_id: 'amazon_kurta_v1', marketplace: 'amazon', category: 'kurta' },
]

export default function Products() {
  const navigate = useNavigate()
  const [products, setProducts] = useState(SAMPLE_PRODUCTS)
  const [templates, setTemplates] = useState(SAMPLE_TEMPLATES)
  const [selectedProducts, setSelectedProducts] = useState([])
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [loading, setLoading] = useState(false)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    // Load products and templates
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      // In production, these would be actual API calls
      // const productsRes = await productsAPI.getAll()
      // const templatesRes = await templatesAPI.getAll()
      // setProducts(productsRes.data)
      // setTemplates(templatesRes.data)
    } catch (err) {
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleProduct = (productId) => {
    setSelectedProducts((prev) =>
      prev.includes(productId)
        ? prev.filter((id) => id !== productId)
        : [...prev, productId]
    )
  }

  const selectAll = () => {
    if (selectedProducts.length === products.length) {
      setSelectedProducts([])
    } else {
      setSelectedProducts(products.map((p) => p.id))
    }
  }

  const handleStartMapping = async () => {
    if (!selectedTemplate || selectedProducts.length === 0) {
      return
    }

    setProcessing(true)
    try {
      // Create mapping jobs for selected products
      // In production, this would be actual API calls
      // for (const productId of selectedProducts) {
      //   await mappingAPI.createJob(productId, selectedTemplate)
      // }

      // Navigate to mapping preview
      navigate('/mapping')
    } catch (err) {
      console.error('Failed to create mapping jobs:', err)
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div>
      {/* Page header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600 mt-1">
            Select products to map to marketplace templates
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">
            {selectedProducts.length} of {products.length} selected
          </p>
        </div>
      </div>

      {/* Template selector */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Target Template
            </label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="input"
            >
              <option value="">Select a template...</option>
              {templates.map((template) => (
                <option key={template.schema_id} value={template.schema_id}>
                  {template.marketplace.toUpperCase()} - {template.category}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleStartMapping}
              disabled={!selectedTemplate || selectedProducts.length === 0 || processing}
              className="btn-primary"
            >
              {processing ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Processing...
                </span>
              ) : (
                `Map ${selectedProducts.length} Product${selectedProducts.length !== 1 ? 's' : ''}`
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Products table */}
      <div className="table-container">
        <table className="table">
          <thead className="table-header">
            <tr>
              <th className="w-12">
                <input
                  type="checkbox"
                  checked={selectedProducts.length === products.length}
                  onChange={selectAll}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </th>
              <th>Product</th>
              <th>Type</th>
              <th>Vendor</th>
              <th>Variants</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody className="table-body">
            {products.map((product) => (
              <tr
                key={product.id}
                className={`table-row-hover cursor-pointer ${
                  selectedProducts.includes(product.id) ? 'bg-indigo-50' : ''
                }`}
                onClick={() => toggleProduct(product.id)}
              >
                <td>
                  <input
                    type="checkbox"
                    checked={selectedProducts.includes(product.id)}
                    onChange={() => toggleProduct(product.id)}
                    onClick={(e) => e.stopPropagation()}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                </td>
                <td>
                  <div className="flex items-center">
                    <div className="h-10 w-10 flex-shrink-0">
                      {product.images?.[0]?.src ? (
                        <img
                          src={product.images[0].src}
                          alt={product.title}
                          className="h-10 w-10 rounded-lg object-cover"
                        />
                      ) : (
                        <div className="h-10 w-10 rounded-lg bg-gray-200 flex items-center justify-center">
                          <span className="text-gray-400">📦</span>
                        </div>
                      )}
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {product.title}
                      </div>
                      <div className="text-xs text-gray-500">
                        ID: {product.id}
                      </div>
                    </div>
                  </div>
                </td>
                <td>
                  <span className="badge-gray">{product.product_type || 'N/A'}</span>
                </td>
                <td className="text-sm text-gray-600">{product.vendor || 'N/A'}</td>
                <td className="text-sm text-gray-600">{product.variants_count || 1}</td>
                <td>
                  <span className={`badge ${product.status === 'active' ? 'badge-success' : 'badge-gray'}`}>
                    {product.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Empty state */}
      {products.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">📦</div>
          <h3 className="text-lg font-medium text-gray-900">No products yet</h3>
          <p className="text-gray-500 mt-1">
            Connect your Shopify store to sync products
          </p>
          <button
            onClick={() => navigate('/connect')}
            className="btn-primary mt-4"
          >
            Connect Shopify
          </button>
        </div>
      )}
    </div>
  )
}
