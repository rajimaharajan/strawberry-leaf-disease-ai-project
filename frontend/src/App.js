import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import LoginPage from './LoginPage';
import SignupPage from './SignupPage';
import Dashboard from "./Dashboard";
import Videos from './Videos';
import Pathologists from './Pathologists';
import Pesticides from './Pesticides';
import Fertilizers from './Fertilizers';
import { useAuth } from './AuthContext';

function ProtectedRoute({ children }) {
  const { isLoggedIn } = useAuth();
  if (!isLoggedIn) {
    return <Navigate to="/" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
<Route path="/" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/videos" element={<ProtectedRoute><Videos /></ProtectedRoute>} />
      <Route path="/pathologists" element={<ProtectedRoute><Pathologists /></ProtectedRoute>} />
      <Route path="/pesticides" element={<ProtectedRoute><Pesticides /></ProtectedRoute>} />
      <Route path="/fertilizers" element={<ProtectedRoute><Fertilizers /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
