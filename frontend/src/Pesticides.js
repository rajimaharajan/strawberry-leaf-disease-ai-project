import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import './Style.css';

const organicPestControl = [
  { name: 'Neem Oil', use: 'Aphids, mites, and whiteflies', notes: 'Natural insecticide and fungicide' },
  { name: 'Garlic-Chili Spray', use: 'General insect repellent', notes: 'Natural deterrent for soft-bodied insects' },
  { name: 'Soap Water Spray', use: 'Soft-bodied insects', notes: 'Use mild liquid soap mixed with water' },
];

const chemicalInsecticides = [
  { name: 'Imidacloprid', use: 'Aphids and sucking pests', notes: 'Systemic insecticide for soil or foliar application' },
  { name: 'Spinosad', use: 'Thrips and caterpillars', notes: 'Derived from natural soil bacteria' },
  { name: 'Abamectin', use: 'Mites', notes: 'Effective against spider mites and leafminers' },
];

const chemicalFungicides = [
  { name: 'Mancozeb', use: 'Leaf spot and fungal protection', notes: 'Broad-spectrum contact fungicide' },
  { name: 'Copper Oxychloride', use: 'Fungal disease control', notes: 'Protectant fungicide and bactericide' },
  { name: 'Carbendazim', use: 'Root rot and fungal infections', notes: 'Systemic fungicide for soil and foliar use' },
];

const tips = [
  'Avoid overusing nitrogen; too much gives leaves but fewer fruits.',
  'Spray pesticides in the early morning or evening.',
  'Do not spray during flowering when bees are active.',
  'Maintain proper spacing to avoid fungal diseases.',
  'Use drip irrigation if possible to prevent leaf wetness.',
];

export default function Pesticides() {
  const navigate = useNavigate();
  return (
    <div className="page pink-theme">
      <div className="navbar">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          <ArrowLeft /> Back to Dashboard
        </button>
      </div>
      <div className="treatments-page">
        <h1>💊 Pesticides Guide</h1>
        <p>Recommended pesticides for strawberry disease management</p>

        <h2>🌿 Organic Pest Control</h2>
        <div className="treatments-grid">
          {organicPestControl.map((t, i) => (
            <div key={i} className="treatment-card">
              <h3>{t.name}</h3>
              <span className="category">Organic</span>
              <p><strong>For:</strong> {t.use}</p>
              <small>{t.notes}</small>
            </div>
          ))}
        </div>

        <h2>🐛 Chemical Pesticides — Insects</h2>
        <div className="treatments-grid">
          {chemicalInsecticides.map((t, i) => (
            <div key={i} className="treatment-card">
              <h3>{t.name}</h3>
              <span className="category">Insecticide</span>
              <p><strong>For:</strong> {t.use}</p>
              <small>{t.notes}</small>
            </div>
          ))}
        </div>

        <h2>🍄 Chemical Pesticides — Fungal Diseases</h2>
        <div className="treatments-grid">
          {chemicalFungicides.map((t, i) => (
            <div key={i} className="treatment-card">
              <h3>{t.name}</h3>
              <span className="category">Fungicide</span>
              <p><strong>For:</strong> {t.use}</p>
              <small>{t.notes}</small>
            </div>
          ))}
        </div>

        <h2>💡 Important Tips</h2>
        <ul className="tips-list">
          {tips.map((tip, i) => (
            <li key={i}>{tip}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

