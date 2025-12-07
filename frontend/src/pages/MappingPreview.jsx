import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { mappingAPI } from '../services/api'

// Sample mapping data for demo
const SAMPLE_MAPPING = {
  job_id: 'job_123',
  product_id: 'prod_1',
  template_schema_id: 'amazon_shirt_v1',
  status: 'needs_user_input',
  mappings: {
    sku: { value: 'PCTS-BLU-S', source: 'variant.sku', confidence: 0.95 },
    title: { value: 'Premium Cotton T-Shirt - Blue', source: 'product.title', confidence: 0.95 },
    brand: { value: 'AutoList Fashion', source: 'product.vendor', confidence: 0.90 },
    description: { value: 'Soft, breathable cotton t-shirt perfect for summer.', source: 'product.description', confidence: 0.85 },
    fabric: { value: 'Cotton', source: 'ai_description', confidence: 0.75 },
    color: { value: 'Blue', source: 'extracted.colors', confidence: 0.80 },
    size: { value: 'S', source: 'variant.option1', confidence: 0.90 },
    price: { value: '29.99', source: 'variant.price', confidence: 0.95 },
    main_image_url: { value: 'https://example.com/image.jpg', source: 'product.images', confidence: 0.95 },
    parent_sku: { value: null, source: 'not_found', confidence: 0.0 },
  },
}

// Confidence badge component
const ConfidenceBadge = ({ confidence }) => {
  const getColor = (conf) => {
    if (conf >= 0.8) return 'badge-success'
    if (conf >= 0.5) return 'badge-warning'
    return 'badge-danger'
  }

  const getLabel = (conf) => {
    if (conf >= 0.8) return 'High'
    if (conf >= 0.5) return 'Medium'
    if (conf > 0) return 'Low'
    return 'Missing'
  }

  return (
    <div className="flex items-center space-x-2">
      <span className={`badge ${getColor(confidence)}`}>
        {getLabel(confidence)}
      </span>
      <span className="text-xs text-gray-500">
        {(confidence * 100).toFixed(0)}%
      </span>
    </div>
  )
}

// Editable field component
const EditableField = ({ field, mapping, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(mapping.value || '')

  const handleSave = () => {
    onUpdate(field, editValue)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditValue(mapping.value || '')
    setIsEditing(false)
  }

  return (
    <div className="flex items-center space-x-2">
      {isEditing ? (
        <>
          <input
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            className="input py-1 px-2 text-sm flex-1"
            autoFocus
          />
          <button onClick={handleSave} className="text-emerald-600 hover:text-emerald-700">
            ✓
          </button>
          <button onClick={handleCancel} className="text-red-600 hover:text-red-700">
            ✕
          </button>
        </>
      ) : (
        <>
          <span className={`flex-1 ${mapping.value ? '' : 'text-gray-400 italic'}`}>
            {mapping.value || 'Not mapped'}
          </span>
          <button
            onClick={() => setIsEditing(true)}
            className="text-gray-400 hover:text-indigo-600"
          >
            ✏️
          </button>
        </>
      )}
    </div>
  )
}

export default function MappingPreview() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [mapping, setMapping] = useState(SAMPLE_MAPPING)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [showApproveModal, setShowApproveModal] = useState(false)

  useEffect(() => {
    if (jobId) {
      loadMapping()
    }
  }, [jobId])

  const loadMapping = async () => {
    setLoading(true)
    try {
      // const response = await mappingAPI.getJob(jobId)
      // setMapping(response.data)
    } catch (err) {
      console.error('Failed to load mapping:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFieldUpdate = (field, newValue) => {
    setMapping((prev) => ({
      ...prev,
      mappings: {
        ...prev.mappings,
        [field]: {
          ...prev.mappings[field],
          value: newValue,
          source: 'user_edit',
          confidence: 1.0,
        },
      },
    }))
  }

  const handleApproveAll = () => {
    // Update all fields with AI suggestions to high confidence
    setMapping((prev) => ({
      ...prev,
      mappings: Object.fromEntries(
        Object.entries(prev.mappings).map(([field, data]) => [
          field,
          data.value ? { ...data, confidence: Math.max(data.confidence, 0.9) } : data,
        ])
      ),
    }))
  }

  const handleSaveAndDownload = async () => {
    setSaving(true)
    try {
      // await mappingAPI.approveJob(mapping.job_id)
      navigate('/download')
    } catch (err) {
      console.error('Failed to save mapping:', err)
    } finally {
      setSaving(false)
    }
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      pending: { class: 'badge-gray', label: 'Pending' },
      processing: { class: 'badge-info', label: 'Processing' },
      needs_user_input: { class: 'badge-warning', label: 'Needs Review' },
      ready: { class: 'badge-success', label: 'Ready' },
      completed: { class: 'badge-success', label: 'Completed' },
      error: { class: 'badge-danger', label: 'Error' },
    }
    const config = statusMap[status] || { class: 'badge-gray', label: status }
    return <span className={`badge ${config.class}`}>{config.label}</span>
  }

  const mappingEntries = Object.entries(mapping.mappings || {})
  const mappedCount = mappingEntries.filter(([_, m]) => m.value).length
  const avgConfidence = mappingEntries.reduce((sum, [_, m]) => sum + (m.value ? m.confidence : 0), 0) / mappedCount || 0

  return (
    <div>
      {/* Page header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mapping Preview</h1>
          <p className="text-gray-600 mt-1">
            Review and edit field mappings before export
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {getStatusBadge(mapping.status)}
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="card">
          <div className="text-sm text-gray-500">Fields Mapped</div>
          <div className="text-2xl font-bold text-gray-900">
            {mappedCount} / {mappingEntries.length}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500">Avg Confidence</div>
          <div className="text-2xl font-bold text-gray-900">
            {(avgConfidence * 100).toFixed(0)}%
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500">Template</div>
          <div className="text-lg font-medium text-gray-900">
            {mapping.template_schema_id}
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-gray-600">
              Fields with low confidence are highlighted. Edit values or approve AI suggestions.
            </p>
          </div>
          <div className="flex space-x-3">
            <button onClick={handleApproveAll} className="btn-secondary">
              Approve All Suggested
            </button>
            <button
              onClick={handleSaveAndDownload}
              disabled={saving}
              className="btn-primary"
            >
              {saving ? 'Saving...' : 'Save & Download'}
            </button>
          </div>
        </div>
      </div>

      {/* Mapping table */}
      <div className="table-container">
        <table className="table">
          <thead className="table-header">
            <tr>
              <th className="w-1/4">Field</th>
              <th className="w-1/3">Value</th>
              <th className="w-1/6">Source</th>
              <th className="w-1/6">Confidence</th>
            </tr>
          </thead>
          <tbody className="table-body">
            {mappingEntries.map(([field, data]) => (
              <tr
                key={field}
                className={`table-row-hover ${
                  data.confidence < 0.5 ? 'bg-amber-50' : ''
                } ${!data.value ? 'bg-red-50' : ''}`}
              >
                <td>
                  <span className="font-medium text-gray-900">{field}</span>
                </td>
                <td>
                  <EditableField
                    field={field}
                    mapping={data}
                    onUpdate={handleFieldUpdate}
                  />
                </td>
                <td>
                  <span className="text-xs text-gray-500 font-mono">
                    {data.source}
                  </span>
                </td>
                <td>
                  <ConfidenceBadge confidence={data.confidence} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-6 card bg-gray-50 border-gray-200">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Legend</h3>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <span className="w-4 h-4 rounded bg-red-100 mr-2"></span>
            <span className="text-gray-600">Missing value</span>
          </div>
          <div className="flex items-center">
            <span className="w-4 h-4 rounded bg-amber-100 mr-2"></span>
            <span className="text-gray-600">Low confidence (&lt;50%)</span>
          </div>
          <div className="flex items-center">
            <span className="badge-success mr-2">High</span>
            <span className="text-gray-600">≥80% confidence</span>
          </div>
          <div className="flex items-center">
            <span className="badge-warning mr-2">Medium</span>
            <span className="text-gray-600">50-79% confidence</span>
          </div>
        </div>
      </div>
    </div>
  )
}
