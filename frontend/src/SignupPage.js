import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import { register, login as apiLogin } from './api';
import './LoginPage.css';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.email || !formData.password) {
      setError('Please fill all fields');
      return;
    }

    setLoading(true);
    try {
      // Register the user
      await register(formData.username, formData.email, formData.password);
      
      // Auto-login after registration
      const data = await apiLogin(formData.email, formData.password);
      login(data.token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Signup failed. Please try again.');
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

      {/* Signup Card */}
      <div className="login-card">
        {/* Logo */}
        <div className="logo-container">
          <div className="logo-circle">
            <span className="logo-strawberry">🍓</span>
          </div>
        </div>

        {/* Title */}
        <h1 className="app-title">StrawberryGuard</h1>
        <p className="app-subtitle">Create Your Account</p>

        {/* Signup Form */}
        <form onSubmit={handleSubmit} className="login-form">
          {/* Error Message */}
          {error && (
            <div className="error-message" style={{ color: '#c94b4b', marginBottom: '15px', textAlign: 'center' }}>
              {error}
            </div>
          )}

          {/* Username */}
          <div className="form-group">
            <label className="form-label">
              <svg className="label-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter your username"
              className="form-input"
              required
            />
          </div>

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
              placeholder="Create a password"
              className="form-input"
              required
            />
          </div>

          {/* Submit Button */}
          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>

        {/* Login Link */}
        <p className="signup-text">
          Have an account? <a href="/" className="signup-link">Login</a>
        </p>
      </div>
    </div>
  );
};

export default SignupPage;
