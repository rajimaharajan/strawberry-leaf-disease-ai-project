import React, { useRef, useEffect, useState, useCallback } from "react";
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { predictImage, healthCheck } from './api.js';
import { jsPDF } from "jspdf";
import "./Dashboard.css";

const REMEDIES = {
  'Healthy': {
    status: 'healthy',
    message: 'Your plant is healthy! Keep up the good work.',
    tips: ['Maintain regular watering schedule', 'Ensure proper sunlight (6-8 hours)', 'Monitor for early signs of disease'],
    feeding: ['Early spring: NPK 10-10-10', 'Pre-bloom: Calcium-rich fertilizer', 'Post-harvest: Compost or well-rotted manure']
  },
  'Leaf Scorch': {
    status: 'disease',
    message: 'Leaf scorch detected. Immediate treatment recommended.',
    remedies: ['Remove infected leaves immediately', 'Apply fungicide with copper-based compounds', 'Avoid overhead watering', 'Improve air circulation around plants', 'Use mulch to prevent soil splash'],
    feeding: ['Reduce nitrogen until recovery', 'Apply potassium sulfate to strengthen leaves', 'Resume balanced NPK after 2 weeks']
  },
  'Powdery Mildew': {
    status: 'disease',
    message: 'Powdery mildew detected. Treat immediately.',
    remedies: ['Apply sulfur-based fungicide', 'Remove severely infected plant parts', 'Increase air circulation', 'Avoid excessive nitrogen fertilization', 'Water at base of plant, not foliage'],
    feeding: ['Hold off high-nitrogen feeds', 'Use seaweed extract spray weekly', 'Reintroduce balanced feed once mildew clears']
  }
};

const MAX_MB = 5;
const MAX_BYTES = MAX_MB * 1024 * 1024;

export default function Dashboard() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const uploadAreaRef = useRef(null);
  const fileInputRef = useRef(null);
  const feedbackRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [backendStatus, setBackendStatus] = useState(null); // null = checking, true = ok, false = error

  // Normalize class names from backend to frontend keys
  const normalizeClass = (cls) => {
    const map = {
      'Strawberry___healthy': 'Healthy',
      'Strawberry___Leaf_scorch': 'Leaf Scorch',
      'powdery_mildew': 'Powdery Mildew',
      'Healthy': 'Healthy',
      'Leaf Scorch': 'Leaf Scorch',
      'Powdery Mildew': 'Powdery Mildew'
    };
    return map[cls] || cls;
  };

  const setFeedbackMsg = useCallback((msg, isError = false) => {
    setFeedback(msg);
    if (feedbackRef.current) {
      feedbackRef.current.style.color = isError ? '#c94b4b' : '#375a47';
    }
  }, []);

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setAnalyzing(true);
    setFeedbackMsg('Analyzing image...');
    try {
      const result = await predictImage(selectedFile);
      setAnalysisResult(result);
      setFeedbackMsg('Analysis complete!');
    } catch (error) {
      setFeedbackMsg(error.message || 'Analysis failed. Please try again.', true);
      console.error(error);
    }
    setAnalyzing(false);
  };

  const generatePDF = useCallback(() => {
    if (!analysisResult || !previewUrl) return;
    const doc = new jsPDF();
    const normalizedClass = normalizeClass(analysisResult.prediction);
    const remedy = REMEDIES[normalizedClass] || { status: 'unknown', message: 'Consult an expert.', tips: ['Monitor plant health'], feeding: ['Follow general strawberry guidance'] };
    const isHealthy = remedy.status === 'healthy';
    const confValue = typeof analysisResult.confidence === 'number' ? analysisResult.confidence.toFixed(1) : analysisResult.confidence;
    const today = new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' });

    // Header
    doc.setFillColor(255, 107, 120);
    doc.rect(0, 0, 210, 40, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(22);
    doc.text('StrawberryGuard', 14, 20);
    doc.setFontSize(14);
    doc.text('Diagnosis Report', 14, 30);
    doc.setFontSize(10);
    doc.text(`Date: ${today}`, 14, 38);

    let y = 50;

    // Image
    try {
      doc.addImage(previewUrl, 'JPEG', 14, y, 80, 60);
    } catch (e) {
      doc.setTextColor(100, 100, 100);
      doc.text('[Image unavailable]', 14, y + 30);
    }

    // Result box
    doc.setFillColor(247, 249, 251);
    doc.roundedRect(100, y, 96, 60, 4, 4, 'F');
    doc.setTextColor(isHealthy ? 22 : 154, isHealthy ? 101 : 52, isHealthy ? 52 : 18);
    doc.setFontSize(16);
    doc.text(normalizedClass, 104, y + 12);
    doc.setTextColor(107, 115, 122);
    doc.setFontSize(11);
    doc.text(`Confidence: ${confValue}%`, 104, y + 22);
    doc.setTextColor(isHealthy ? 22 : 154, isHealthy ? 101 : 52, isHealthy ? 52 : 18);
    doc.setFontSize(10);
    doc.text(isHealthy ? '✅ Plant is Healthy' : '⚠️ Disease Detected', 104, y + 32);
    doc.setTextColor(75, 85, 99);
    doc.setFontSize(9);
    const msgLines = doc.splitTextToSize(remedy.message, 86);
    doc.text(msgLines, 104, y + 42);

    y += 70;

    // Remedies / Care Tips
    doc.setTextColor(55, 65, 81);
    doc.setFontSize(13);
    doc.text(isHealthy ? '💚 Care Tips' : '💊 Recommended Remedies', 14, y);
    y += 8;
    doc.setFontSize(10);
    const items = remedy.remedies || remedy.tips || [];
    items.forEach((item, idx) => {
      doc.text(`${idx + 1}. ${item}`, 18, y);
      y += 6;
    });

    y += 8;

    // Feeding Schedule
    doc.setTextColor(55, 65, 81);
    doc.setFontSize(13);
    doc.text('🌾 Suggested Feeding Schedule', 14, y);
    y += 8;
    doc.setFontSize(10);
    (remedy.feeding || []).forEach((item) => {
      doc.text(`• ${item}`, 18, y);
      y += 6;
    });

    // Footer
    doc.setTextColor(150, 150, 150);
    doc.setFontSize(9);
    doc.text('Generated by StrawberryGuard AI | For agricultural guidance only.', 14, 285);

    doc.save(`StrawberryGuard_Report_${Date.now()}.pdf`);
  }, [analysisResult, previewUrl]);

  const handleFiles = useCallback((files) => {
    const f = files[0];
    if (!f) return;

    if (!/^image\/(jpeg|png|webp)$/.test(f.type)) {
      setFeedbackMsg('Unsupported file type. Use JPG, PNG or WEBP.', true);
      return;
    }
    if (f.size > MAX_BYTES) {
      setFeedbackMsg(`File too large. Max ${MAX_MB}MB allowed.`, true);
      return;
    }

    setSelectedFile(f);
    setAnalysisResult(null);
    setFeedbackMsg(`Selected: ${f.name} (${Math.round(f.size/1024)} KB)`);

    const reader = new FileReader();
    reader.onload = (ev) => {
      setPreviewUrl(ev.target.result);
    };
    reader.readAsDataURL(f);
  }, [setFeedbackMsg]);

  useEffect(() => {
    const area = uploadAreaRef.current;
    if (!area) return;

    const handleDragEnterOver = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(true);
    };

    const handleDragLeaveEndDrop = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(false);
    };

    const handleDrop = (e) => {
      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files.length) {
        handleFiles(dt.files);
      }
    };

    area.addEventListener('dragenter', handleDragEnterOver);
    area.addEventListener('dragover', handleDragEnterOver);
    area.addEventListener('dragleave', handleDragLeaveEndDrop);
    area.addEventListener('dragend', handleDragLeaveEndDrop);
    area.addEventListener('drop', handleDrop);
    area.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fileInputRef.current?.click();
      }
    });

    return () => {
      area.removeEventListener('dragenter', handleDragEnterOver);
      area.removeEventListener('dragover', handleDragEnterOver);
      area.removeEventListener('dragleave', handleDragLeaveEndDrop);
      area.removeEventListener('dragend', handleDragLeaveEndDrop);
      area.removeEventListener('drop', handleDrop);
      area.removeEventListener('keydown', () => {});
    };
  }, [handleFiles]);

  useEffect(() => {
    if (feedbackRef.current) {
      feedbackRef.current.textContent = feedback;
    }
  }, [feedback]);

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await healthCheck();
        if (data.status === 'ok' && data.model_status === 'loaded') {
          setBackendStatus(true);
        } else {
          setBackendStatus(false);
        }
      } catch (err) {
        setBackendStatus(false);
        console.error('Health check failed:', err);
      }
    };
    checkHealth();
  }, []);

  const CircularProgress = ({ value, size = 90, stroke = 8 }) => {
    const radius = (size - stroke) / 2;
    const circumference = 2 * Math.PI * radius;
    const pct = Math.min(100, Math.max(0, value));
    const offset = circumference - (pct / 100) * circumference;
    const color = pct >= 80 ? '#22c55e' : pct >= 50 ? '#f59e0b' : '#ef4444';
    return (
      <div className="circular-progress" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e5e7eb"
            strokeWidth={stroke}
            fill="none"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={stroke}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
          />
        </svg>
        <div className="circular-progress-text">
          <span className="circular-progress-value" style={{ color }}>{pct.toFixed(0)}%</span>
          <span className="circular-progress-label">Confidence</span>
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard">

      {/* ---------------- NAVBAR ---------------- */}

      <div className="navbar">

        <div className="logo-section">

          <div className="logo-box">
            🍓
          </div>

          <h1 className="logo-title">
            StrawberryGuard
          </h1>

        </div>

        <div className="status">
          <span className="dot"></span>
          Dashboard Active
        </div>

        <button className="logout-btn" onClick={logout}>
          Logout
        </button>

      </div>

      {/* ---------------- BACKEND STATUS BANNER ---------------- */}
      {backendStatus === false && (
        <div className="backend-status-banner error">
          ⚠️ Backend disconnected or model not loaded. Please ensure the Flask server is running on port 5000.
        </div>
      )}
      {backendStatus === true && (
        <div className="backend-status-banner success">
          ✅ AI Model Ready — Upload an image to analyze
        </div>
      )}

      {/* ---------------- MAIN CONTENT ---------------- */}

      <div className="dashboard-content">

        {/* ---------------- UPLOAD & ANALYSIS SECTION ---------------- */}

        <div className="upload-section-main">
          <div className="columns">
            {/* Upload Card */}
            <section ref={uploadAreaRef} className={`upload-area ${isDragOver ? 'dragover' : ''}`} id="uploadArea" tabIndex={0} aria-labelledby="uploadTitle">
              {/* File input: positioned absolute ONLY when no preview shown, otherwise hidden to avoid blocking buttons */}
              {!previewUrl && (
                <input ref={fileInputRef} type="file" id="fileInput" className="upload-input" accept="image/jpeg,image/png,image/webp" aria-label="Upload strawberry plant photo (supports JPG, PNG, WEBP)" onChange={(e) => handleFiles(e.target.files)} />
              )}
              {previewUrl ? (
                <div className="preview-wrap">
                  <img src={previewUrl} alt="Preview" className="preview-image" />
                  <div className="preview-actions">
                    <button className="change-img-btn" onClick={() => { setSelectedFile(null); setPreviewUrl(null); setAnalysisResult(null); fileInputRef.current?.click(); }}>
                      🔄 Change Image
                    </button>
                    <button className="analyze-btn" onClick={handleAnalyze} disabled={analyzing}>
                      {analyzing ? 'Analyzing...' : '🔍 Analyze'}
                    </button>
                  </div>
                  {/* Hidden input for Change Image click */}
                  <input ref={fileInputRef} type="file" className="hidden-file-input" accept="image/jpeg,image/png,image/webp" onChange={(e) => handleFiles(e.target.files)} />
                </div>
              ) : (
                <>
                  <div className="upload-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                      <path d="M12 16V6" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M8 10l4-4 4 4" strokeLinecap="round" strokeLinejoin="round"/>
                      <rect x="3.5" y="16.5" width="17" height="3" rx="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <h3 id="uploadTitle">Upload Strawberry Plant Photo</h3>
                  <p className="lead">Click to browse or drag and drop</p>
                  <span className="file-hint">Supports: JPG, PNG, WEBP</span>
                </>
              )}
              <div ref={feedbackRef} className="feedback" aria-live="polite" />
            </section>
            {/* Right column - Analysis Result */}
            <aside className="analysis-aside">
              {analysisResult ? (() => {
                const normalizedClass = normalizeClass(analysisResult.prediction);
                const remedy = REMEDIES[normalizedClass] || { status: 'unknown', message: 'Analysis complete. Consult an expert for detailed treatment.', tips: ['Monitor plant health regularly'] };
                const isHealthy = remedy.status === 'healthy';
                const confValue = analysisResult.confidence;
                return (
                  <div className="analysis-result-wrap">
                    <div className="analysis-result-header">
                      <div className="analysis-result-icon">{isHealthy ? '🌿' : '🔬'}</div>
                      <h3 className={`analysis-result-title ${isHealthy ? 'healthy' : 'disease'}`}>{normalizedClass}</h3>
                      <div className="analysis-result-confidence-row">
                        <CircularProgress value={typeof confValue === 'number' ? confValue : 0} />
                      </div>
                      <div className={`analysis-result-badge ${isHealthy ? 'healthy-badge' : 'disease-badge'}`}>
                        {isHealthy ? '✅ Plant is Healthy' : '⚠️ Disease Detected'}
                      </div>
                      <button className="pdf-export-btn" onClick={generatePDF}>
                        📄 Download PDF Report
                      </button>
                    </div>
                    
                    <div className="analysis-result-body">
                      <div className="analysis-result-section-title">
                        {isHealthy ? '💚 Care Tips' : '💊 Recommended Remedies'}
                      </div>
                      <div className="analysis-result-message">
                        {remedy.message}
                      </div>
                      <ul className="analysis-result-list">
                        {(remedy.remedies || remedy.tips || []).map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                );
              })() : (
                <div className="analysis-empty">
                  <svg width="60" height="60" viewBox="0 0 24 24" fill="none">
                    <path d="M6 6l12 12" stroke="#c1c8ce" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="12" cy="12" r="6" stroke="#c1c8ce" strokeWidth="1.4"/>
                  </svg>
                  <div className="analysis-empty-title">No Analysis Yet</div>
                  <div className="analysis-empty-sub">Upload an image to get started</div>
                </div>
              )}
            </aside>
          </div>
        </div>

        {/* ---------------- FEATURE CARDS ---------------- */}

        <div className="cards-grid">

          {/* TREATMENT VIDEOS */}
          <div className="info-card orange-theme">
            <div className="info-card-icon">▶️</div>
            <h3>Treatment Videos</h3>
            <p>Watch expert tutorials on disease management</p>
            <button className="view-btn orange-btn" onClick={() => navigate('/videos')}>
              View
            </button>
          </div>

          {/* NEARBY PATHOLOGISTS */}
          <div className="info-card purple-theme">
            <div className="info-card-icon">👥</div>
            <h3>Nearby Pathologists</h3>
            <p>Connect with plant pathologists near you</p>
            <button className="view-btn purple-btn" onClick={() => navigate('/pathologists')}>
              View
            </button>
          </div>

          {/* PESTICIDES */}
          <div className="info-card blue-theme">
            <div className="info-card-icon">🌿</div>
            <h3>Pesticides</h3>
            <p>Recommended pesticides & dosage guides</p>
            <button className="view-btn blue-btn" onClick={() => navigate('/pesticides')}>
              View
            </button>
          </div>

          {/* FERTILIZERS */}
          <div className="info-card green-theme">
            <div className="info-card-icon">🌾</div>
            <h3>Fertilizers</h3>
            <p>Best fertilizers for healthy strawberry growth</p>
            <button className="view-btn green-btn" onClick={() => navigate('/fertilizers')}>
              View
            </button>
          </div>

        </div>

        {/* ---------------- SEASONAL CALENDAR ---------------- */}

        <div className="season-card-main">

          <div className="card-header">

            <span className="card-icon orange">
              📅
            </span>

            <div>

              <h2>
                Seasonal Growing Calendar
              </h2>

              <p>
                Optimize your strawberry cultivation timeline
              </p>

            </div>

          </div>

          <div className="season-grid">

            <div className="season-card green-border">

              <div className="season-emoji">
                🌱
              </div>

              <h3>
                Planting
              </h3>

              <p>
                March - May
              </p>

            </div>

            <div className="season-card yellow-border">

              <div className="season-emoji">
                🌸
              </div>

              <h3>
                Flowering
              </h3>

              <p>
                April - June
              </p>

            </div>

            <div className="season-card orange-border">

              <div className="season-emoji">
                🍓
              </div>

              <h3>
                Harvesting
              </h3>

              <p>
                May - October
              </p>

            </div>

            <div className="season-card blue-border">

              <div className="season-emoji">
                ❄️
              </div>

              <h3>
                Dormancy
              </h3>

              <p>
                Nov - Feb
              </p>

            </div>

          </div>

        </div>

      </div>

      {/* ---------------- FOOTER ---------------- */}

      <footer className="footer">

        <h1>
          🍓 StrawberryGuard
        </h1>

        <p>
          AI Powered Disease Detection
          for Healthy Crops and
          Sustainable Farming
        </p>

        <div className="footer-links">

          <span>
            About
          </span>

          <span>
            Privacy
          </span>

          <span>
            Support
          </span>

        </div>

        <hr />

        <p>
          Developed with ❤️ by GJR
        </p>

      </footer>

    </div>
  );
}

