import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import './Style.css';

const organicFertilizers = [
  { name: 'Compost', use: 'Soil fertility and moisture retention', notes: 'Improves overall soil structure and health' },
  { name: 'Well-rotted Cow Manure', use: 'Natural nitrogen for leaf growth', notes: 'Must be well decomposed before use' },
  { name: 'Vermicompost', use: 'Boosts microbial activity and root health', notes: 'Rich in beneficial microbes and enzymes' },
  { name: 'Bone Meal', use: 'Flowering and root development', notes: 'Rich in phosphorus for strong roots' },
  { name: 'Neem Cake', use: 'Fertilizer and pest repellent', notes: 'Acts as both nutrient source and natural pest control' },
];

const chemicalFertilizers = [
  { name: 'NPK Fertilizer (19:19:19)', use: 'Balanced growth', notes: 'N→leaf growth, P→root/flower, K→fruit quality' },
  { name: 'Urea', use: 'Vegetative growth', notes: 'Provides nitrogen for lush green leaves' },
  { name: 'DAP (Diammonium Phosphate)', use: 'Root growth and flowering', notes: 'High phosphorus content for early stages' },
  { name: 'Potash', use: 'Fruit size and color', notes: 'Improves fruit quality and sweetness' },
  { name: 'Calcium Nitrate', use: 'Prevents weak fruits', notes: 'Improves fruit firmness and prevents disorders' },
];

const feedingSchedule = [
  { stage: 'Before planting', fertilizer: 'Compost + Neem Cake' },
  { stage: 'Vegetative growth', fertilizer: 'NPK Fertilizer' },
  { stage: 'Flowering stage', fertilizer: 'Phosphorus + Potassium' },
  { stage: 'Fruiting stage', fertilizer: 'Potash + Calcium Nitrate' },
];

const tips = [
  'Avoid overusing nitrogen; too much gives leaves but fewer fruits.',
  'Spray fertilizers in the early morning or evening.',
  'Do not spray during flowering when bees are active.',
  'Maintain proper spacing to avoid fungal diseases.',
  'Use drip irrigation if possible to prevent leaf wetness.',
];

export default function Fertilizers() {
  const navigate = useNavigate();
  return (
    <div className="page pink-theme">
      <div className="navbar">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          <ArrowLeft /> Back to Dashboard
        </button>
      </div>
      <div className="treatments-page">
        <h1>🌾 Fertilizers Guide</h1>
        <p>Recommended fertilizers for healthy strawberry growth</p>

        <h2>🌿 Organic Fertilizers</h2>
        <div className="treatments-grid">
          {organicFertilizers.map((t, i) => (
            <div key={i} className="treatment-card">
              <h3>{t.name}</h3>
              <span className="category">Organic</span>
              <p><strong>For:</strong> {t.use}</p>
              <small>{t.notes}</small>
            </div>
          ))}
        </div>

        <h2>🧪 Chemical Fertilizers</h2>
        <div className="treatments-grid">
          {chemicalFertilizers.map((t, i) => (
            <div key={i} className="treatment-card">
              <h3>{t.name}</h3>
              <span className="category">Chemical</span>
              <p><strong>For:</strong> {t.use}</p>
              <small>{t.notes}</small>
            </div>
          ))}
        </div>

        <h2>📅 Simple Feeding Schedule</h2>
        <div className="schedule-table-wrapper">
          <table className="schedule-table">
            <thead>
              <tr>
                <th>Stage</th>
                <th>Fertilizer</th>
              </tr>
            </thead>
            <tbody>
              {feedingSchedule.map((row, i) => (
                <tr key={i}>
                  <td>{row.stage}</td>
                  <td>{row.fertilizer}</td>
                </tr>
              ))}
            </tbody>
          </table>
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

