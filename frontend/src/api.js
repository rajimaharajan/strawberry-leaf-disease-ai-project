const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:3000';

// ==============================
// AUTH API
// ==============================

export const register = async (username, email, password) => {
  const response = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Registration failed');
  }
  return data;
};

export const login = async (email, password) => {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Login failed');
  }
  return data;
};

export const getProfile = async (token) => {
  const response = await fetch(`${API_BASE}/api/auth/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Failed to get profile');
  }
  return data;
};

// ==============================
// ML PREDICTION API
// ==============================

export const predictImage = async (file, token) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/api/predict`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Prediction failed');
  }
  return data;
};

export const getHistory = async (token) => {
  const response = await fetch(`${API_BASE}/api/history`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Failed to get history');
  }
  return data;
};

export const deleteHistory = async (id, token) => {
  const response = await fetch(`${API_BASE}/api/history/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Failed to delete');
  }
  return data;
};

// ==============================
// HEALTH CHECK
// ==============================

export const healthCheck = async () => {
  const response = await fetch(`${API_BASE}/api/health`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Health check failed');
  }
  return data;
};
