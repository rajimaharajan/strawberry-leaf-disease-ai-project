// LoginPage.jsx
import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    role: '',
    phoneNumber: '',
    email: '',
    password: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.role || !formData.phoneNumber || !formData.password) {
      alert('Please fill role, phone, and password');
      return;
    }
    const token = btoa(JSON.stringify({ role: formData.role, phone: formData.phoneNumber, sub: Date.now() }));
    login(token);
    // Production: Remove console.log
    navigate('/dashboard');
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
          {/* Role Select */}
          <div className="form-group">
            <label className="form-label">
              <svg className="label-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              Login as
            </label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="form-input form-select"
            >
              <option value="">Select your role</option>
              <option value="farmer">Farmer</option>
              <option value="agronomist">Agronomist</option>
              <option value="researcher">Researcher</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          {/* Phone Number */}
          <div className="form-group">
            <label className="form-label">
              <svg className="label-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
              </svg>
              Phone Number
            </label>
            <input
              type="tel"
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleChange}
              placeholder="+91 00000 00000"
              className="form-input"
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
              <span className="optional-text">(optional)</span>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your@email.com"
              className="form-input"
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
            />
          </div>

          {/* Submit Button */}
          <button type="submit" className="login-button">
            Login to Dashboard
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

