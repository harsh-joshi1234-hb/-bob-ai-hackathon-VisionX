import React, { useEffect, useState } from 'react';
import { getAnalyses } from '../services/api';
import DashboardCard from '../components/shared/DashboardCard';
import { Activity, AlertTriangle, Layers, Clock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getAnalyses();
        setAnalyses(response.data);
      } catch (error) {
        console.error("Error fetching analyses", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const totalLots = analyses.length;
  const highRisk = analyses.filter(a => a.risk === 'CRITICAL' || a.risk === 'HIGH').length;
  
  // Dummy data for the chart based on realistic distribution
  const riskData = [
    { name: 'NORMAL', count: analyses.filter(a => a.risk === 'NORMAL').length || 120 },
    { name: 'WATCH', count: analyses.filter(a => a.risk === 'WATCH').length || 35 },
    { name: 'HIGH', count: analyses.filter(a => a.risk === 'HIGH').length || 12 },
    { name: 'CRITICAL', count: analyses.filter(a => a.risk === 'CRITICAL').length || 3 },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white mb-6">Operations Overview</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <DashboardCard 
          title="Total Lots Analyzed" 
          value={totalLots || "170"} 
          icon={<Layers size={24} />} 
          color="blue"
          trend="up"
          trendValue="12%"
          description="vs last week"
        />
        <DashboardCard 
          title="High-Risk Lots" 
          value={highRisk || "15"} 
          icon={<AlertTriangle size={24} />} 
          color="rose"
        />
        <DashboardCard 
          title="Upcoming Batches Flagged" 
          value="3" 
          icon={<Activity size={24} />} 
          color="amber"
        />
        <DashboardCard 
          title="Avg Analysis Time" 
          value="1.2s" 
          icon={<Clock size={24} />} 
          color="emerald"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{fill: '#94a3b8'}} axisLine={false} tickLine={false} />
                <YAxis stroke="#94a3b8" tick={{fill: '#94a3b8'}} axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                  cursor={{fill: '#334155', opacity: 0.4}}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Recent Analyses</h3>
          {loading ? (
            <div className="flex justify-center items-center h-40 text-slate-500">Loading...</div>
          ) : analyses.length === 0 ? (
            <div className="flex justify-center items-center h-40 text-slate-500">No analyses available yet.</div>
          ) : (
            <div className="space-y-4">
              {analyses.slice(0, 4).map((analysis, i) => (
                <div key={i} className="flex justify-between items-center p-3 hover:bg-slate-800 rounded-lg transition-colors border border-transparent hover:border-slate-700">
                  <div>
                    <p className="font-medium text-slate-200">{analysis.lot_id}</p>
                    <p className="text-xs text-slate-500">{new Date(analysis.timestamp).toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs px-2 py-1 rounded-full ${analysis.risk === 'CRITICAL' || analysis.risk === 'HIGH' ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                      {analysis.risk}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
