import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Play, X } from 'lucide-react';
import './Style.css';

const VIDEOS = [
  {
    id: 1,
    title: 'Stop Powdery Mildew Fast',
    description: 'Learn how to identify and treat powdery mildew on your strawberry plants quickly and effectively.',
    src: '/videos/Stop Powdery Mildew Fast Here\'s How.mp4',
    tag: 'Disease Control'
  },
  {
    id: 2,
    title: '4 Ways to Grow Strawberries',
    description: 'Discover the key methods to maximize your strawberry yield with expert gardening tips.',
    src: '/videos/4 Ways to Grow Strawberries & the Key to Growing a Lot.mp4',
    tag: 'Growing Tips'
  },
  {
    id: 3,
    title: '7 Tips to Grow More Strawberries',
    description: 'Simple and practical tips to boost your strawberry production season after season.',
    src: '/videos/7 Tips to Grow a Lot of Strawberries.mp4',
    tag: 'Yield Boost'
  },
  {
    id: 4,
    title: 'Grow Strawberries Like a Pro',
    description: 'Professional gardening tips for healthy, high-quality strawberry cultivation.',
    src: '/videos/Grow STRAWBERRIES Like a Pro (Gardening Tips).mp4',
    tag: 'Pro Guide'
  },
  {
    id: 5,
    title: 'Strawberry Fertilizing Tips',
    description: 'Organic fertilizing schedule and tips for strawberries through the growing season.',
    src: '/videos/Strawberry fertilizing tip. I fertilize my strawberries 3 times through the season. #organicgarden.mp4',
    tag: 'Fertilizing'
  }
];

function getVideoSrc(path) {
  // Split path at last '/' to encode only the filename portion
  const lastSlash = path.lastIndexOf('/');
  if (lastSlash === -1) return encodeURIComponent(path);
  const dir = path.slice(0, lastSlash + 1);
  const file = path.slice(lastSlash + 1);
  return dir + encodeURIComponent(file);
}

export default function Videos() {
  const navigate = useNavigate();
  const [activeVideo, setActiveVideo] = useState(null);
  const videoRef = useRef(null);

  const openVideo = (video) => {
    setActiveVideo(video);
    document.body.style.overflow = 'hidden';
  };

  const closeVideo = () => {
    if (videoRef.current) {
      videoRef.current.pause();
    }
    setActiveVideo(null);
    document.body.style.overflow = 'auto';
  };

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') closeVideo();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  // Programmatically play video when modal mounts
  useEffect(() => {
    if (activeVideo && videoRef.current) {
      videoRef.current.play().catch((err) => {
        // Auto-play may be blocked by browser policy; user can click play
        console.log('Auto-play blocked:', err);
      });
    }
  }, [activeVideo]);

  return (
    <div className="page pink-theme">
      <div className="navbar">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          <ArrowLeft /> Back to Dashboard
        </button>
      </div>
      <div className="videos-page">
        <h1>▶️ Educational Videos</h1>
        <p>Learn the best practices for strawberry disease prevention, care, and high-yield growing</p>
        <div className="videos-grid">
          {VIDEOS.map((video) => (
            <div className="video-card" key={video.id}>
              <div className="video-placeholder" onClick={() => openVideo(video)}>
                <div className="video-play-overlay">
                  <Play size={48} />
                </div>
              </div>
              <span className="category">{video.tag}</span>
              <h3>{video.title}</h3>
              <p>{video.description}</p>
              <button className="btn btn-play" onClick={() => openVideo(video)}>
                ▶ Play Video
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Video Modal */}
      {activeVideo && (
        <div className="video-modal-overlay" onClick={closeVideo}>
          <div className="video-modal" onClick={(e) => e.stopPropagation()}>
            <button className="video-modal-close" onClick={closeVideo}>
              <X size={24} />
            </button>
            <h3 className="video-modal-title">{activeVideo.title}</h3>
            <video
              key={activeVideo.id}
              ref={videoRef}
              src={getVideoSrc(activeVideo.src)}
              controls
              autoPlay
              muted
              playsInline
              className="video-player"
            />
            <p className="video-modal-desc">{activeVideo.description}</p>
          </div>
        </div>
      )}
    </div>
  );
}
