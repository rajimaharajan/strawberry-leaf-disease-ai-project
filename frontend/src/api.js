const API_BASE = 'http://localhost:5000';  // Flask backend port

export const healthCheck = async () => {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
};

export const predictImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const errText = await response.text().catch(() => 'Unknown error');
    throw new Error(`Prediction failed (${response.status}): ${errText}`);
  }
  return response.json();
};

export const getHistory = async () => {
  const response = await fetch(`${API_BASE}/history`);
  if (!response.ok) throw new Error('Failed to get history');
  return response.json();
};

