import React from 'react';
import StatusBadge from '../shared/StatusBadge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const ResultDashboard = ({ result }) => {
  if (!result) return null;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* 1. DETECT & 2. PREDICT */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* DETECT */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <div className="bg-slate-800/50 px-6 py-4 border-b border-slate-800 flex justify-between items-center">
            <h3 className="font-bold text-white tracking-wide">1. DETECT</h3>
            <span className="text-[10px] uppercase bg-slate-800 text-slate-400 px-2 py-1 rounded border border-slate-700">ML MODEL OUTPUT</span>
          </div>
          <div className="p-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <p className="text-slate-400 text-sm mb-1">Wafer Defect Pattern</p>
                <div className="text-2xl font-bold text-white mb-2">
                  {result.wafer_analysis?.prediction || 'N/A'}
                </div>
                <div className="text-sm text-slate-500">
                  Confidence: <span className="text-slate-300">{(result.wafer_analysis?.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
              <StatusBadge status={result.wafer_analysis?.prediction === 'none' ? 'PASS' : result.wafer_analysis?.prediction} />
            </div>
            
            <div className="mt-4 p-4 bg-slate-950 rounded-lg text-xs font-mono text-slate-500 flex justify-between">
              <span>Model: WaferMap CNN</span>
              <span>{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>

        {/* PREDICT */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <div className="bg-slate-800/50 px-6 py-4 border-b border-slate-800 flex justify-between items-center">
            <h3 className="font-bold text-white tracking-wide">2. PREDICT</h3>
            <span className="text-[10px] uppercase bg-slate-800 text-slate-400 px-2 py-1 rounded border border-slate-700">ML MODEL OUTPUT</span>
          </div>
          <div className="p-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <p className="text-slate-400 text-sm mb-1">Process Risk Classification</p>
                <div className="text-2xl font-bold text-white mb-2">
                  {result.process_analysis?.prediction || 'N/A'}
                </div>
                <div className="text-sm text-slate-500">
                  Failure Probability: <span className="text-slate-300">{(result.process_analysis?.probability * 100).toFixed(1)}%</span>
                </div>
              </div>
              <StatusBadge status={result.process_analysis?.prediction} />
            </div>
            
            <div className="mt-4 p-4 bg-slate-950 rounded-lg text-xs font-mono text-slate-500 flex justify-between">
              <span>Model: SECOM Classifier</span>
              <span>{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. EXPLAIN */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="bg-slate-800/50 px-6 py-4 border-b border-slate-800 flex justify-between items-center">
          <h3 className="font-bold text-white tracking-wide">3. EXPLAIN</h3>
          <span className="text-[10px] uppercase bg-indigo-900/50 text-indigo-300 px-2 py-1 rounded border border-indigo-800">MODEL EXPLANATION</span>
        </div>
        <div className="p-6">
          <h4 className="text-slate-300 font-medium mb-6">Root Cause Analysis (SHAP Contributions)</h4>
          
          {result.root_causes && result.root_causes.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={result.root_causes} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} vertical={false} />
                  <XAxis type="number" stroke="#94a3b8" />
                  <YAxis dataKey="feature_name" type="category" stroke="#94a3b8" tick={{fill: '#e2e8f0', fontSize: 12}} width={100} />
                  <Tooltip 
                    cursor={{fill: '#1e293b'}}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }}
                  />
                  <Bar dataKey="importance" barSize={20}>
                    {result.root_causes.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.direction === 'POSITIVE' ? '#f43f5e' : '#10b981'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500 bg-slate-950 rounded-lg border border-slate-800 border-dashed">
              Root cause analysis (SHAP) is not available for this run.
            </div>
          )}
        </div>
      </div>

      {/* 4. ACT */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="bg-blue-900/20 px-6 py-4 border-b border-blue-900/30 flex justify-between items-center">
          <h3 className="font-bold text-blue-400 tracking-wide">4. ACT</h3>
          <span className="text-[10px] uppercase bg-blue-900/50 text-blue-200 px-2 py-1 rounded border border-blue-700">IBM BOB / AI-GENERATED ANALYSIS</span>
        </div>
        <div className="p-6">
          {result.ai_explanation ? (
            <div className="prose prose-invert max-w-none text-slate-300 text-sm">
              <p>{result.ai_explanation.summary}</p>
              {/* If we had structured AI explanation, map it here */}
            </div>
          ) : result.recommendations && result.recommendations.length > 0 ? (
            <div className="space-y-4">
              <h4 className="text-white font-medium mb-3">AI Engineering Recommendation</h4>
              {result.recommendations.map((rec, i) => (
                <div key={i} className="p-4 bg-slate-800/50 rounded border border-slate-700">
                  <p className="font-semibold text-blue-400 mb-1">{rec.action}</p>
                  <p className="text-slate-400 text-sm">{rec.reason}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 text-center text-slate-500 bg-slate-950 rounded-lg border border-slate-800">
              Generating AI Engineering Recommendation... (Simulated)
            </div>
          )}
        </div>
      </div>
      
    </div>
  );
};

export default ResultDashboard;
