import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import { API_BASE } from './api.js';
import './LoginPage.css';  // Reuse style
const SignupPage = () => {
  const [formData, setFormData] = useState({
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
    if (!formData.email || !formData.password) {
      setError('Please fill email and password');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/auth/signup`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Signup failed');
      
      login(data.access_token);
      alert('Welcome! Account created.');
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Same UI as Login */}
      <div className="strawberry-bg">
        {/* strawberries... */}
      </div>
      <div className="login-card">
        <h1 className="app-title">StrawberryGuard</h1>
        <p>Welcome! Create your account</p>
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Email</label>
            <input type="email" name="email" value={formData.email} onChange={handleChange} className="form-input" />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} className="form-input" />
          </div>
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'Signing up...' : 'Sign Up'}
          </button>
        </form>
        <p>Have account? <a href="/" className="signup-link">Login</a></p>
      </div>
    </div>
  );
};

export default SignupPage;

