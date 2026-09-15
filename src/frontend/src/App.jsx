import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import LotAnalyzer from './pages/LotAnalyzer';
import UpcomingBatches from './pages/UpcomingBatches';
import History from './pages/History';
import ModelInfo from './pages/ModelInfo';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<LotAnalyzer />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upcoming-batches" element={<UpcomingBatches />} />
          {/* <Route path="/upcoming-batches/:id" element={<BatchDetail />} /> */}
          <Route path="/history" element={<History />} />
          <Route path="/models" element={<ModelInfo />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
