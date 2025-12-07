import { useState, useEffect } from 'react'
import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'

// Pages
import Login from './pages/Login'
import ShopifyConnect from './pages/ShopifyConnect'
import Products from './pages/Products'
import MappingPreview from './pages/MappingPreview'
import Download from './pages/Download'
import Dashboard from './pages/Dashboard'

// Auth context
const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    setIsAuthenticated(!!token)
    setLoading(false)
  }, [])

  const login = (token) => {
    localStorage.setItem('access_token', token)
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setIsAuthenticated(false)
  }

  return { isAuthenticated, loading, login, logout }
}

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

// Navigation component
const Navigation = () => {
  const location = useLocation()
  const { logout } = useAuth()

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/connect', label: 'Connect', icon: '🔗' },
    { path: '/products', label: 'Products', icon: '📦' },
    { path: '/mapping', label: 'Mapping', icon: '🗺️' },
    { path: '/download', label: 'Download', icon: '📥' },
  ]

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <span className="text-2xl">🚀</span>
              <span className="text-xl font-bold text-indigo-600">AutoList AI</span>
            </Link>
          </div>

          {/* Navigation links */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  location.pathname === item.path
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <span className="mr-1">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>

          {/* User menu */}
          <div className="flex items-center">
            <button
              onClick={logout}
              className="text-sm text-gray-600 hover:text-gray-900 px-4 py-2"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

// Layout wrapper for authenticated pages
const AppLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/connect"
        element={
          <ProtectedRoute>
            <AppLayout>
              <ShopifyConnect />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/products"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Products />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mapping"
        element={
          <ProtectedRoute>
            <AppLayout>
              <MappingPreview />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mapping/:jobId"
        element={
          <ProtectedRoute>
            <AppLayout>
              <MappingPreview />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/download"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Download />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      {/* Redirects */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
