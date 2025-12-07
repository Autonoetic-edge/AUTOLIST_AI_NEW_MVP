import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { exportAPI, mappingAPI } from '../services/api'

// Sample jobs for demo
const SAMPLE_JOBS = [
  {
    job_id: 'job_123',
    product_id: 'prod_1',
    product_title: 'Premium Cotton T-Shirt - Blue',
    template_schema_id: 'amazon_shirt_v1',
    status: 'ready',
    auto_fill_rate: 0.87,
    created_at: '2024-01-15T10:30:00Z',
  },
  {
    job_id: 'job_124',
    product_id: 'prod_2',
    product_title: 'Traditional Silk Kurta - Maroon',
    template_schema_id: 'amazon_kurta_v1',
    status: 'ready',
    auto_fill_rate: 0.82,
    created_at: '2024-01-15T10:35:00Z',
  },
]

export default function Download() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState(SAMPLE_JOBS)
  const [selectedJobs, setSelectedJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    setLoading(true)
    try {
      // const response = await mappingAPI.getJobs({ status: 'ready' })
      // setJobs(response.data)
    } catch (err) {
      console.error('Failed to load jobs:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleJob = (jobId) => {
    setSelectedJobs((prev) =>
      prev.includes(jobId)
        ? prev.filter((id) => id !== jobId)
        : [...prev, jobId]
    )
  }

  const selectAll = () => {
    if (selectedJobs.length === jobs.length) {
      setSelectedJobs([])
    } else {
      setSelectedJobs(jobs.map((j) => j.job_id))
    }
  }

  const handleDownload = async (jobId = null) => {
    setDownloading(true)
    try {
      const idsToDownload = jobId ? [jobId] : selectedJobs

      if (idsToDownload.length === 1) {
        // Single file download
        // const response = await exportAPI.downloadXlsx(idsToDownload[0])
        // downloadBlob(response.data, `mapping_${idsToDownload[0]}.xlsx`)

        // Demo: show success message
        alert(`Downloading mapping for job: ${idsToDownload[0]}`)
      } else {
        // Batch download
        // const response = await exportAPI.downloadBatch(idsToDownload)
        // downloadBlob(response.data, 'batch_export.xlsx')

        // Demo: show success message
        alert(`Downloading ${idsToDownload.length} mappings as batch export`)
      }
    } catch (err) {
      console.error('Download failed:', err)
    } finally {
      setDownloading(false)
    }
  }

  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
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

  const readyJobs = jobs.filter((j) => j.status === 'ready' || j.status === 'completed')

  return (
    <div>
      {/* Page header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Download Templates</h1>
          <p className="text-gray-600 mt-1">
            Export completed mappings as Excel files
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">
            {selectedJobs.length} of {readyJobs.length} selected
          </p>
        </div>
      </div>

      {/* Batch actions */}
      {selectedJobs.length > 0 && (
        <div className="card mb-6 bg-indigo-50 border-indigo-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-indigo-600 mr-2">📦</span>
              <span className="text-indigo-700 font-medium">
                {selectedJobs.length} item{selectedJobs.length > 1 ? 's' : ''} selected
              </span>
            </div>
            <button
              onClick={() => handleDownload()}
              disabled={downloading}
              className="btn-primary"
            >
              {downloading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Preparing...
                </span>
              ) : (
                `Download ${selectedJobs.length > 1 ? 'Batch' : 'Selected'}`
              )}
            </button>
          </div>
        </div>
      )}

      {/* Jobs table */}
      {readyJobs.length > 0 ? (
        <div className="table-container">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="w-12">
                  <input
                    type="checkbox"
                    checked={selectedJobs.length === readyJobs.length}
                    onChange={selectAll}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                </th>
                <th>Product</th>
                <th>Template</th>
                <th>Auto-Fill Rate</th>
                <th>Status</th>
                <th>Created</th>
                <th className="w-32">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {readyJobs.map((job) => (
                <tr
                  key={job.job_id}
                  className={`table-row-hover ${
                    selectedJobs.includes(job.job_id) ? 'bg-indigo-50' : ''
                  }`}
                >
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedJobs.includes(job.job_id)}
                      onChange={() => toggleJob(job.job_id)}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                  </td>
                  <td>
                    <div className="text-sm font-medium text-gray-900">
                      {job.product_title}
                    </div>
                    <div className="text-xs text-gray-500">
                      ID: {job.product_id}
                    </div>
                  </td>
                  <td>
                    <span className="badge-gray">{job.template_schema_id}</span>
                  </td>
                  <td>
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-emerald-500 h-2 rounded-full"
                          style={{ width: `${job.auto_fill_rate * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">
                        {(job.auto_fill_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td>{getStatusBadge(job.status)}</td>
                  <td className="text-sm text-gray-500">
                    {formatDate(job.created_at)}
                  </td>
                  <td>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => navigate(`/mapping/${job.job_id}`)}
                        className="text-indigo-600 hover:text-indigo-700 text-sm"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDownload(job.job_id)}
                        className="text-emerald-600 hover:text-emerald-700 text-sm"
                      >
                        Download
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-12 card">
          <div className="text-4xl mb-4">📥</div>
          <h3 className="text-lg font-medium text-gray-900">No exports ready</h3>
          <p className="text-gray-500 mt-1">
            Complete product mappings to see them here
          </p>
          <button
            onClick={() => navigate('/products')}
            className="btn-primary mt-4"
          >
            Start Mapping
          </button>
        </div>
      )}

      {/* Info section */}
      <div className="mt-8 card bg-gray-50 border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Export Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
          <div>
            <p className="font-medium text-gray-700">Single Export</p>
            <p>Downloads one XLSX file with the mapped data for a single product.</p>
          </div>
          <div>
            <p className="font-medium text-gray-700">Batch Export</p>
            <p>Combines multiple products into a single XLSX file with proper row ordering.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
