// LoginPage.jsx
import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import { login as apiLogin } from './api';
import './LoginPage.css';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!formData.email || !formData.password) {
      setError('Please fill email and password');
      return;
    }

    setLoading(true);
    try {
      const data = await apiLogin(formData.email, formData.password);
      login(data.token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Floating Strawberries Background */}
      <div className="strawberry-bg">
        <div className="strawberry s1">🍓</div>
        <div className="strawberry s2">🍓</div>
        <div className="strawberry s3">🍓</div>
        <div className="strawberry s4">🍓</div>
        <div className="strawberry s5">🍓</div>
        <div className="strawberry s6">🍓</div>
        <div className="strawberry s7">🍓</div>
        <div className="strawberry s8">🍓</div>
      </div>

      {/* Login Card */}
      <div className="login-card">
        {/* Logo */}
        <div className="logo-container">
          <div className="logo-circle">
            <span className="logo-strawberry">🍓</span>
          </div>
        </div>

        {/* Title */}
        <h1 className="app-title">StrawberryGuard</h1>
        <p className="app-subtitle">Disease Detection & Management</p>

{/* Login Form */}
        <form onSubmit={handleSubmit} className="login-form">
          {/* Error Message */}
          {error && (
            <div className="error-message" style={{ color: '#c94b4b', marginBottom: '15px', textAlign: 'center' }}>
              {error}
            </div>
          )}

          {/* Email */}
          <div className="form-group">
            <label className="form-label">
              <svg className="label-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
              </svg>
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your@email.com"
              className="form-input"
              required
            />
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label">
              <svg className="label-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              className="form-input"
              required
            />
          </div>

          {/* Submit Button */}
          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Logging in...' : 'Login to Dashboard'}
          </button>
        </form>

        {/* Sign Up Link */}
        <p className="signup-text">
          Don't have an account? <a href="/signup" className="signup-link">Sign up</a>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;

