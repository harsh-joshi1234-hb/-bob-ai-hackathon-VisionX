import React, { useState, useEffect } from 'react';
import { analyzeLot, getLots, analyzeWafer, analyzeProcess, analyzeNewLot } from '../services/api';
import ResultDashboard from '../components/shared/ResultDashboard';
import { WaferUploader, ProcessCsvUploader } from '../components/shared/Uploaders';

const LotAnalyzer = () => {
  const [activeTab, setActiveTab] = useState('demo');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Demo Lot State
  const [lots, setLots] = useState([]);
  const [selectedLot, setSelectedLot] = useState('');

  // Upload States
  const [waferFile, setWaferFile] = useState(null);
  const [csvFile, setCsvFile] = useState(null);

  useEffect(() => {
    getLots().then(res => {
      setLots(res.data);
      if (res.data.length > 0) setSelectedLot(res.data[0].lot_id);
    }).catch(err => console.error("Failed to load lots", err));
  }, []);

  const handleAnalyzeDemo = async () => {
    if (!selectedLot) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyzeLot(selectedLot);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred during analysis.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeWafer = async () => {
    if (!waferFile) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyzeWafer(waferFile);
      setResult({
        wafer_analysis: res.data,
        process_analysis: null,
        root_causes: [],
        overall_risk: { level: 'N/A', score: 0 },
        recommendations: []
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Wafer analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeProcess = async () => {
    if (!csvFile) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyzeProcess(csvFile);
      setResult({
        wafer_analysis: null,
        process_analysis: res.data,
        root_causes: [],
        overall_risk: { level: 'N/A', score: 0 },
        recommendations: []
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Process data analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeCombined = async () => {
    if (!waferFile && !csvFile) {
      setError("Please upload at least one file.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyzeNewLot("NEW-" + Math.floor(Math.random() * 1000), waferFile, csvFile);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Combined analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white">S1 Analyzer Console</h2>
        <p className="text-slate-400 mt-1">Select an analysis mode below.</p>
      </div>

      <div className="flex space-x-1 bg-slate-900/50 p-1 rounded-lg border border-slate-800 w-full lg:w-fit">
        {[
          { id: 'demo', label: '1. Demo Lot' },
          { id: 'wafer', label: '2. Wafer Image' },
          { id: 'csv', label: '3. Process CSV' },
          { id: 'combined', label: '4. New Lot (Combined)' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => { setActiveTab(tab.id); setResult(null); setError(null); }}
            className={`px-6 py-2.5 rounded-md text-sm font-medium transition-all ${
              activeTab === tab.id 
                ? 'bg-blue-600 text-white shadow-md' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 lg:p-8">
        {activeTab === 'demo' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-4">Demo Lot Analyzer</h3>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Select Demo Lot</label>
              <select 
                className="w-full lg:w-1/3 bg-slate-950 border border-slate-700 rounded-lg p-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                value={selectedLot}
                onChange={(e) => setSelectedLot(e.target.value)}
              >
                {lots.map(l => (
                  <option key={l.lot_id} value={l.lot_id}>{l.lot_id}</option>
                ))}
              </select>
            </div>
            <button 
              onClick={handleAnalyzeDemo}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Analyze Lot'}
            </button>
          </div>
        )}

        {activeTab === 'wafer' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-4">Wafer Image Analysis</h3>
            <div className="max-w-xl">
              <WaferUploader onFileSelected={setWaferFile} />
            </div>
            <button 
              onClick={handleAnalyzeWafer}
              disabled={loading || !waferFile}
              className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Analyzing Wafer...' : 'Analyze Wafer'}
            </button>
          </div>
        )}

        {activeTab === 'csv' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-4">Process Data Analysis</h3>
            <div className="max-w-xl">
              <ProcessCsvUploader onFileSelected={setCsvFile} />
            </div>
            <button 
              onClick={handleAnalyzeProcess}
              disabled={loading || !csvFile}
              className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Analyzing Data...' : 'Analyze Process Data'}
            </button>
          </div>
        )}

        {activeTab === 'combined' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-4">New Lot Analysis (Combined)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <WaferUploader onFileSelected={setWaferFile} />
              <ProcessCsvUploader onFileSelected={setCsvFile} />
            </div>
            <button 
              onClick={handleAnalyzeCombined}
              disabled={loading || (!waferFile && !csvFile)}
              className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Running Full Pipeline...' : 'Analyze New Lot'}
            </button>
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400">
            <p className="font-semibold">Analysis Failed</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}
      </div>

      {result && (
        <div className="mt-8">
          <ResultDashboard result={result} />
        </div>
      )}
    </div>
  );
};

export default LotAnalyzer;
