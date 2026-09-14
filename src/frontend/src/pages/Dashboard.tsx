import { useState, useEffect } from 'react';
import type { LotSummary } from '../api/lotsApi';
import { lotsApi } from '../api/lotsApi';
import type { UpcomingBatch } from '../api/batchesApi';
import { batchesApi } from '../api/batchesApi';

import { BatchRiskTable } from '../components/BatchRiskTable';
import { LoadingState, ErrorState } from '../components/States';
import { useNavigate } from 'react-router-dom';
import { Activity, ShieldAlert, Database } from 'lucide-react';

export default function Dashboard() {
  const [lots, setLots] = useState<LotSummary[]>([]);
  const [batches, setBatches] = useState<UpcomingBatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [lotsData, batchesData] = await Promise.all([
          lotsApi.getLots(),
          batchesApi.getUpcomingBatches()
        ]);
        setLots(lotsData);
        setBatches(batchesData);
      } catch (err: any) {
        setError(err.message || 'Failed to connect to backend API.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <LoadingState message="Loading dashboard data..." />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  const completedLots = lots.filter(l => l.status === 'COMPLETE').length;
  const pendingLots = lots.filter(l => l.status === 'PENDING').length;
  
  // Note: We'd normally have a "high risk lots" calculation here. 
  // For demo, we'll mock it based on total
  const highRiskLots = Math.floor(completedLots * 0.2); 
  
  const flaggedBatches = batches.filter(b => b.status === 'FLAGGED').length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Control Room Dashboard</h2>
          <p className="text-muted-foreground text-sm mt-1">S1 Semiconductor Yield Monitoring</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-border bg-card p-6 flex items-center gap-4 shadow-sm">
          <div className="p-3 bg-primary/10 text-primary rounded-full">
            <Database className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Total Lots Analyzed</p>
            <h3 className="text-2xl font-bold">{completedLots}</h3>
          </div>
        </div>
        
        <div className="rounded-xl border border-border bg-card p-6 flex items-center gap-4 shadow-sm">
          <div className="p-3 bg-destructive/10 text-destructive rounded-full">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">High-Risk Lots</p>
            <h3 className="text-2xl font-bold">{highRiskLots}</h3>
          </div>
        </div>
        
        <div className="rounded-xl border border-border bg-card p-6 flex items-center gap-4 shadow-sm">
          <div className="p-3 bg-yellow-500/10 text-yellow-500 rounded-full">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Upcoming Batches Flagged</p>
            <h3 className="text-2xl font-bold">{flaggedBatches}</h3>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6 flex items-center gap-4 shadow-sm">
          <div className="p-3 bg-secondary text-secondary-foreground rounded-full">
            <Database className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Pending Demo Lots</p>
            <h3 className="text-2xl font-bold">{pendingLots}</h3>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold">Upcoming Batch Risk Monitor</h3>
            <button 
              onClick={() => navigate('/batches')}
              className="text-xs px-3 py-1.5 bg-primary/10 text-primary hover:bg-primary/20 rounded-md transition-colors font-medium flex items-center gap-1"
            >
              Open Full Monitor &rarr;
            </button>
          </div>
          <BatchRiskTable batches={batches.slice(0, 5)} />
        </div>
        
        <div className="flex flex-col gap-4">
          <h3 className="text-lg font-bold">Demo Lots Ready for Analysis</h3>
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="divide-y divide-border">
              {lots.filter(l => l.status === 'PENDING').map(lot => (
                <div key={lot.lot_id} className="p-4 flex items-center justify-between hover:bg-muted/30 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                    <span className="font-medium text-foreground">{lot.lot_id}</span>
                  </div>
                  <button 
                    onClick={() => navigate('/analyzer')}
                    className="text-xs px-3 py-1.5 bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-md transition-colors font-medium"
                  >
                    Load in Analyzer
                  </button>
                </div>
              ))}
              {lots.filter(l => l.status === 'PENDING').length === 0 && (
                <div className="p-4 text-sm text-muted-foreground">No pending lots.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
