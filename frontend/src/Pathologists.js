import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import './Style.css';

const botanists = [
  { name: 'Dr. K. Angappan', title: 'Professor and Head', department: 'Biological Control', email: 'kangappan34@gmail.com' },
  { name: 'Dr. M. Devanathan', title: 'Professor (Plant Pathology)', department: 'Biological Control of Plant Diseases, Integrated Disease Management', email: 'devanathanmuthuram@gmail.com' },
  { name: 'Dr. C. Gopalakrishnan', title: 'Professor (Plant Pathology)', department: 'Biological Control', email: 'pcgopalagri@gmail.com' },
  { name: 'Dr. R. Kannan', title: 'Professor', department: 'Biocontrol, Phyto derived formulations, Post harvest diseases', email: 'kannanar2004@gmail.com' },
  { name: 'Dr. V.K. Parthiban', title: 'Professor', department: 'Post harvest pathology and Food Safety', email: 'vkparthiban@yahoo.com' },
  { name: 'Dr. S. Vanitha', title: 'Professor (Plant Pathology)', department: 'Biological Control', email: 'vanitha1969@yahoo.com' },
  { name: 'Dr. G. Karthikeyan', title: 'Professor', department: 'Plant Virology', email: 'agrikarthi2003@gmail.com' },
  { name: 'Dr. V. Paranidharan', title: 'Professor', department: 'Mycotoxin and Metabolomics', email: 'agriparani@yahoo.com' },
  { name: 'Dr. A. Kamalakannan', title: 'Professor (Plant Pathology)', department: 'Mycology, Aerobiology', email: 'kamals2k@yahoo.co.in' },
  { name: 'Dr. P. Muthulakshmi', title: 'Professor (Plant Pathology)', department: 'Horticulture Pathology', email: 'muthupathology@gmail.com' },
  { name: 'Dr. B. Meena', title: 'Professor (Plant Pathology)', department: 'Biological Control of Plant Diseases, Integrated Disease Management', email: 'meepath@gmail.com' },
  { name: 'Dr. E. Rajeshwari', title: 'Professor (Plant Pathology)', department: 'Cotton Pathology - Biocontrol', email: 'agrirajeswari@gmail.com' },
  { name: 'Dr. P. Renukadevi', title: 'Professor (Plant Pathology)', department: 'Plant Virology, Molecular Pathology', email: 'renucbe88@gmail.com' },
  { name: 'Dr. G. Thiribhuvanamala', title: 'Professor', department: 'Mushroom Science - Biomolecules', email: 'ragumala2000@gmail.com' },
  { name: 'Dr. S.K. Manoranjitham', title: 'Professor (Plant Pathology)', department: 'Plant Virology', email: 'manoranjitham.k@gmail.com' },
  { name: 'Dr. C. Ushamalini', title: 'Professor (Plant Pathology)', department: 'Biological Control of Plant Diseases, Integrated Disease Management', email: 'ushacbe87@gmail.com' },
  { name: 'Dr. Johnson. I.', title: 'Associate Professor (Plant Pathology)', department: 'Bio-control, Mycology', email: 'johnsonpath@gmail.com' },
  { name: 'Dr. M. Karthikeyan', title: 'Associate Professor (Plant Pathology)', department: 'Mycology, Molecular Biology', email: 'karthikeyan.m@tnau.ac.in' },
  { name: 'Dr. S. Harish', title: 'Associate Professor (Plant Pathology)', department: 'Biological Control, Plant Virology', email: 'harish.s@tnau.ac.in' },
  { name: 'Dr. T. Anand', title: 'Associate Professor (Plant Pathology)', department: 'Biocontrol and Molecular Biology', email: 'anandpath10@yahoo.com' },
  { name: 'Dr. A. Sudha', title: 'Associate Professor (Plant Pathology)', department: 'Mycology & Biological Control', email: 'sudhaa1981@gmail.com' },
];

export default function Pathologists() {
  const navigate = useNavigate();
  return (
    <div className="page pink-theme">
      <div className="navbar">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          <ArrowLeft /> Back to Dashboard
        </button>
      </div>
      <div className="pathologists-page">
        <h1>👥 Plant Pathologists</h1>
        <p>Centre for Plant Protection Studies, Tamil Nadu Agricultural University</p>
        <div className="pathologists-grid">
          {botanists.map((b, i) => (
            <div key={i} className="pathologist-card">
              <h3>{b.name}</h3>
              <p><strong>{b.title}</strong></p>
              <p>{b.department}</p>
              <p style={{ color: '#ec4899', fontSize: '0.9rem' }}>{b.email}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
