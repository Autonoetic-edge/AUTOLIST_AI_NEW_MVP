import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'

export default function Login() {
  const navigate = useNavigate()
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (isLogin) {
        const response = await authAPI.login(formData.email, formData.password)
        localStorage.setItem('access_token', response.data.access_token)
      } else {
        await authAPI.register(formData.email, formData.password, formData.name)
        const loginResponse = await authAPI.login(formData.email, formData.password)
        localStorage.setItem('access_token', loginResponse.data.access_token)
      }
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  // Demo login for quick testing
  const handleDemoLogin = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await authAPI.login('demo@autolist.ai', 'password123')
      localStorage.setItem('access_token', response.data.access_token)
      navigate('/dashboard')
    } catch (err) {
      setError('Demo login failed. Please try manual login.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo and title */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">🚀</div>
          <h1 className="text-3xl font-bold text-gray-900">AutoList AI</h1>
          <p className="text-gray-600 mt-2">
            Intelligent product mapping for e-commerce
          </p>
        </div>

        {/* Login/Register card */}
        <div className="card">
          <div className="flex border-b border-gray-200 mb-6">
            <button
              className={`flex-1 pb-3 text-sm font-medium border-b-2 transition-colors ${
                isLogin
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setIsLogin(true)}
            >
              Sign In
            </button>
            <button
              className={`flex-1 pb-3 text-sm font-medium border-b-2 transition-colors ${
                !isLogin
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setIsLogin(false)}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="input"
                  placeholder="John Doe"
                />
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="input"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="input"
                placeholder="••••••••"
                required
                minLength={8}
              />
            </div>

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
                  Processing...
                </span>
              ) : (
                isLogin ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <button
              onClick={handleDemoLogin}
              disabled={loading}
              className="btn-secondary w-full"
            >
              Try Demo Account
            </button>
            <p className="text-xs text-gray-500 text-center mt-2">
              No registration required for demo
            </p>
          </div>
        </div>

        {/* Features preview */}
        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          <div className="p-3">
            <div className="text-2xl mb-1">🔗</div>
            <p className="text-xs text-gray-600">Connect Shopify</p>
          </div>
          <div className="p-3">
            <div className="text-2xl mb-1">🤖</div>
            <p className="text-xs text-gray-600">AI Mapping</p>
          </div>
          <div className="p-3">
            <div className="text-2xl mb-1">📥</div>
            <p className="text-xs text-gray-600">Export Templates</p>
          </div>
        </div>
      </div>
    </div>
  )
}
