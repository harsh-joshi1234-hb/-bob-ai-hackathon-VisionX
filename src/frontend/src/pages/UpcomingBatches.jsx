import React, { useState, useEffect } from 'react';
import { getUpcomingBatches } from '../services/api';
import { Link } from 'react-router-dom';
import StatusBadge from '../components/shared/StatusBadge';

const UpcomingBatches = () => {
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUpcomingBatches().then(res => {
      setBatches(res.data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-white mb-2">Upcoming Batch Risk Monitor</h2>
      <p className="text-slate-400 mb-8">AI analysis of pre-process signals for scheduled manufacturing batches.</p>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase font-semibold">
              <tr>
                <th className="px-6 py-4">Batch ID</th>
                <th className="px-6 py-4">Risk Probability</th>
                <th className="px-6 py-4">Risk Level</th>
                <th className="px-6 py-4">Top Signals</th>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-500">Loading upcoming batches...</td>
                </tr>
              ) : batches.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-500">No upcoming batches found.</td>
                </tr>
              ) : (
                batches.map((batch) => (
                  <tr key={batch.batch_id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-white">{batch.batch_id}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-700 rounded-full h-1.5 overflow-hidden">
                          <div 
                            className={`h-full ${batch.risk_level === 'HIGH' || batch.risk_level === 'CRITICAL' ? 'bg-rose-500' : batch.risk_level === 'WATCH' ? 'bg-amber-500' : 'bg-emerald-500'}`}
                            style={{ width: `${batch.risk_probability * 100}%` }}
                          ></div>
                        </div>
                        <span>{(batch.risk_probability * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4"><StatusBadge status={batch.risk_level} /></td>
                    <td className="px-6 py-4 text-xs font-mono text-slate-400">{batch.top_signals?.slice(0, 2).join(', ')}</td>
                    <td className="px-6 py-4 text-xs text-slate-500">{new Date(batch.scheduled_at).toLocaleDateString()}</td>
                    <td className="px-6 py-4">
                      <Link to={`/upcoming-batches/${batch.batch_id}`} className="text-blue-400 hover:text-blue-300 font-medium text-xs uppercase tracking-wider">
                        View Details →
                      </Link>
                    </td>
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

export default UpcomingBatches;
