import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { productsAPI, templatesAPI, mappingAPI } from '../services/api'

// Sample templates for demo (until templates API is implemented)
// Templates are matched by category to product_type (case-insensitive)
const SAMPLE_TEMPLATES = [
  { schema_id: 'amazon_shirt_v1', marketplace: 'amazon', category: 'shirt' },
  { schema_id: 'amazon_kurta_v1', marketplace: 'amazon', category: 'kurta' },
  { schema_id: 'amazon_dress_v1', marketplace: 'amazon', category: 'dress' },
  { schema_id: 'amazon_saree_v1', marketplace: 'amazon', category: 'saree' },
  { schema_id: 'amazon_tshirt_v1', marketplace: 'amazon', category: 't-shirt' },
]

export default function Products() {
  const navigate = useNavigate()
  const [products, setProducts] = useState([])
  const [allTemplates, setAllTemplates] = useState(SAMPLE_TEMPLATES)
  const [selectedProducts, setSelectedProducts] = useState([])
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [selectedProductType, setSelectedProductType] = useState('all')
  const [loading, setLoading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    // Load products and templates
    loadData()
  }, [])

  // Extract unique product types from products
  const productTypes = useMemo(() => {
    const types = new Set(products.map(p => p.product_type?.toLowerCase() || 'uncategorized'))
    return ['all', ...Array.from(types).sort()]
  }, [products])

  // Filter products by selected product type
  const filteredProducts = useMemo(() => {
    if (selectedProductType === 'all') {
      return products
    }
    return products.filter(
      p => (p.product_type?.toLowerCase() || 'uncategorized') === selectedProductType
    )
  }, [products, selectedProductType])

  // Group products by product type for display
  const groupedProducts = useMemo(() => {
    const groups = {}
    products.forEach(p => {
      const type = p.product_type?.toLowerCase() || 'uncategorized'
      if (!groups[type]) {
        groups[type] = []
      }
      groups[type].push(p)
    })
    return groups
  }, [products])

  // Filter templates based on selected product type
  const availableTemplates = useMemo(() => {
    if (selectedProductType === 'all') {
      return allTemplates
    }
    // Match templates where category contains or matches the product type
    return allTemplates.filter(t => {
      const category = t.category?.toLowerCase() || ''
      const productType = selectedProductType.toLowerCase()
      return category.includes(productType) || productType.includes(category)
    })
  }, [allTemplates, selectedProductType])

  // Reset template selection when product type changes
  useEffect(() => {
    setSelectedTemplate('')
    setSelectedProducts([])
  }, [selectedProductType])

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      // Fetch real products from API
      const productsRes = await productsAPI.getAll({ limit: 250 })
      
      // Transform to expected format for display
      const formattedProducts = productsRes.data.map(p => ({
        id: p.id,
        title: p.title,
        product_type: p.product_type || 'Uncategorized',
        vendor: p.vendor || 'N/A',
        variants_count: p.variants?.length || 1,
        images: p.images || [],
        status: 'active',
      }))
      
      setProducts(formattedProducts)
      
      // TODO: Fetch templates when API is implemented
      // const templatesRes = await templatesAPI.getAll()
      // setAllTemplates(templatesRes.data)
    } catch (err) {
      console.error('Failed to load data:', err)
      if (err.response?.status === 401) {
        setError('Please log in to view products')
      } else {
        setError('Failed to load products. Make sure you have synced products from Shopify.')
      }
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

  const selectAllFiltered = () => {
    if (selectedProducts.length === filteredProducts.length) {
      setSelectedProducts([])
    } else {
      setSelectedProducts(filteredProducts.map((p) => p.id))
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
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600 mt-1">
            Select products to map to marketplace templates
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">
            {selectedProducts.length} of {filteredProducts.length} selected
          </p>
          <button
            onClick={loadData}
            disabled={loading}
            className="mt-2 text-sm text-indigo-600 hover:text-indigo-700"
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          <div className="flex">
            <span className="text-red-500 mr-2">⚠️</span>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Product Type Filter Tabs */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2 border-b border-gray-200 pb-3">
          {productTypes.map((type) => {
            const count = type === 'all' 
              ? products.length 
              : (groupedProducts[type]?.length || 0)
            const isActive = selectedProductType === type
            
            return (
              <button
                key={type}
                onClick={() => setSelectedProductType(type)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {type === 'all' ? 'All Products' : type.charAt(0).toUpperCase() + type.slice(1)}
                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                  isActive ? 'bg-indigo-500 text-white' : 'bg-gray-200 text-gray-600'
                }`}>
                  {count}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Template selector - Only shows templates matching product type */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Target Template
              {selectedProductType !== 'all' && (
                <span className="ml-2 text-xs text-indigo-600">
                  (Showing templates for {selectedProductType})
                </span>
              )}
            </label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="input"
              disabled={availableTemplates.length === 0}
            >
              <option value="">
                {availableTemplates.length === 0 
                  ? 'No templates for this product type' 
                  : 'Select a template...'}
              </option>
              {availableTemplates.map((template) => (
                <option key={template.schema_id} value={template.schema_id}>
                  {template.marketplace.toUpperCase()} - {template.category}
                </option>
              ))}
            </select>
            {selectedProductType !== 'all' && availableTemplates.length === 0 && (
              <p className="mt-1 text-xs text-amber-600">
                No template available for "{selectedProductType}". Select "All Products" to see all templates.
              </p>
            )}
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
                  checked={filteredProducts.length > 0 && selectedProducts.length === filteredProducts.length}
                  onChange={selectAllFiltered}
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
            {filteredProducts.map((product) => (
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

      {/* Empty state for filtered products */}
      {filteredProducts.length === 0 && !loading && products.length > 0 && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900">No products in this category</h3>
          <p className="text-gray-500 mt-1">
            Select a different product type or view all products
          </p>
          <button
            onClick={() => setSelectedProductType('all')}
            className="btn-secondary mt-4"
          >
            View All Products
          </button>
        </div>
      )}

      {/* Empty state for no products */}
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
