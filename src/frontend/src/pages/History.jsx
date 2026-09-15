import React, { useState, useEffect } from 'react';
import { getAnalyses } from '../services/api';
import StatusBadge from '../components/shared/StatusBadge';
import { FileSearch } from 'lucide-react';

const History = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyses().then(res => {
      setAnalyses(res.data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Analysis History</h2>
          <p className="text-slate-400">Past lot and wafer analyses performed by the models.</p>
        </div>
        <button className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg text-sm transition-colors border border-slate-700">
          <FileSearch size={16} /> Filter
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase font-semibold">
              <tr>
                <th className="px-6 py-4">Lot ID</th>
                <th className="px-6 py-4">Analysis Type</th>
                <th className="px-6 py-4">Prediction</th>
                <th className="px-6 py-4">Risk</th>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-500">Loading history...</td>
                </tr>
              ) : analyses.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-500">No analysis history found.</td>
                </tr>
              ) : (
                analyses.map((analysis) => (
                  <tr key={analysis.id} className="hover:bg-slate-800/50 transition-colors cursor-pointer">
                    <td className="px-6 py-4 font-medium text-white">{analysis.lot_id}</td>
                    <td className="px-6 py-4">{analysis.type}</td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-400">{analysis.prediction}</td>
                    <td className="px-6 py-4"><StatusBadge status={analysis.risk} /></td>
                    <td className="px-6 py-4 text-xs text-slate-500">{new Date(analysis.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-4"><StatusBadge status={analysis.status} /></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default History;
