import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import './Style.css';

const treatments = [
  { name: 'Copper Sulfate', category: 'Fungicide', use: 'Powdery Mildew & Leaf Scorch', dosage: '2g/L water', notes: 'Apply early morning, avoid midday sun' },
  { name: 'Neem Oil', category: 'Organic', use: 'All diseases', dosage: '5ml/L', notes: 'Safe for beneficial insects' },
  { name: 'Sulfur', category: 'Fungicide', use: 'Powdery Mildew', dosage: '3g/L', notes: 'Weekly spray during humid weather' },
  { name: 'Mancozeb', category: 'Fungicide', use: 'Leaf Scorch', dosage: '2g/L', notes: '3 day protection interval' },
  { name: 'Carbendazim', category: 'Systemic', use: 'Broad spectrum', dosage: '1g/L', notes: 'Soil drench for root diseases' },
  { name: 'NPK 10-10-10', category: 'Fertilizer', use: 'Healthy growth', dosage: '5g/sq.m', notes: 'Monthly application during growth' },
  { name: 'Compost/Manure', category: 'Organic Fertilizer', use: 'Soil health', dosage: '5kg/plant/year', notes: 'Well decomposed only' },
];

export default function Treatments() {
  const navigate = useNavigate();
  return (
    <div className="page pink-theme">
      <div className="navbar">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          <ArrowLeft /> Back to Dashboard
        </button>
      </div>
      <div className="treatments-page">
        <h1>💊 Pesticides & Fertilizers</h1>
        <p>Recommended treatments for strawberry diseases</p>
        <div className="treatments-grid">
          {treatments.map((t, i) => (
            <div key={i} className="treatment-card">
              <h3>{t.name}</h3>
              <span className="category">{t.category}</span>
              <p><strong>For:</strong> {t.use}</p>
              <p><strong>Dosage:</strong> {t.dosage}</p>
              <small>{t.notes}</small>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

