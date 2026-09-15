import React, { useState, useEffect } from 'react';
import { getModels } from '../services/api';
import { Server, Zap, GitCommit, Settings, CheckCircle2 } from 'lucide-react';

const ModelInfo = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModels().then(res => {
      setModels(res.data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-2">Model Registry</h2>
        <p className="text-slate-400">Metadata and capabilities of currently loaded machine learning models.</p>
      </div>

      {loading ? (
        <div className="text-slate-500">Loading models...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {models.map((model, idx) => (
            <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg flex flex-col">
              <div className="bg-slate-800/50 px-6 py-4 border-b border-slate-800 flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <Server className="text-blue-500" size={20} />
                  <h3 className="font-bold text-white tracking-wide">{model.name}</h3>
                </div>
                <span className="text-[10px] uppercase bg-emerald-900/30 text-emerald-400 px-2 py-1 rounded border border-emerald-800 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                  LOADED
                </span>
              </div>
              
              <div className="p-6 flex-1 flex flex-col space-y-6">
                
                <div>
                  <h4 className="text-xs uppercase text-slate-500 font-semibold mb-2">Purpose</h4>
                  <p className="text-slate-300 text-sm leading-relaxed">{model.purpose}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 border-t border-slate-800/50 pt-4">
                  <div>
                    <h4 className="text-xs uppercase text-slate-500 font-semibold mb-1 flex items-center gap-1"><Zap size={14} /> Type</h4>
                    <p className="text-slate-200 text-sm">{model.type}</p>
                  </div>
                  <div>
                    <h4 className="text-xs uppercase text-slate-500 font-semibold mb-1 flex items-center gap-1"><GitCommit size={14} /> Expected Input</h4>
                    <p className="text-slate-200 text-sm">{model.expected_input}</p>
                  </div>
                </div>
                
                <div className="border-t border-slate-800/50 pt-4">
                  <h4 className="text-xs uppercase text-slate-500 font-semibold mb-3 flex items-center gap-1"><Settings size={14} /> Capabilities</h4>
                  <div className="flex flex-wrap gap-2">
                    {model.supported_methods.map(m => (
                      <span key={m} className="text-xs bg-slate-800 text-slate-300 px-2 py-1 rounded border border-slate-700">Method: {m}()</span>
                    ))}
                    {model.probability_support && (
                      <span className="text-xs bg-blue-900/20 text-blue-300 px-2 py-1 rounded border border-blue-800 flex items-center gap-1">
                        <CheckCircle2 size={12} /> Probabilities Supported
                      </span>
                    )}
                  </div>
                </div>

                <div className="mt-auto border-t border-slate-800/50 pt-4">
                  <h4 className="text-xs uppercase text-slate-500 font-semibold mb-2">Preprocessing Engine</h4>
                  <p className="text-slate-400 text-xs font-mono bg-slate-950 p-3 rounded-md border border-slate-800">
                    {model.preprocessing}
                  </p>
                </div>
                
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ModelInfo;
