import { useEffect, useState } from 'react';
import type { UpcomingBatch } from '../api/batchesApi';
import { batchesApi } from '../api/batchesApi';
import { BatchRiskTable } from '../components/BatchRiskTable';
import { LoadingState, ErrorState } from '../components/States';
import { ShieldAlert, Info } from 'lucide-react';

export default function Batches() {
  const [batches, setBatches] = useState<UpcomingBatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchBatches = async () => {
    try {
      setLoading(true);
      const data = await batchesApi.getUpcomingBatches();
      setBatches(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch upcoming batches.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBatches();
  }, []);

  const handleAnalyzeClick = async (batchId: string) => {
    setAnalyzingId(batchId);
    try {
      await batchesApi.analyzeBatch(batchId);
      // Refresh the table to show updated risk levels
      await fetchBatches();
    } catch (err: any) {
      alert(`Analysis failed: ${err.message}`);
    } finally {
      setAnalyzingId(null);
    }
  };

  if (loading && !analyzingId) return <LoadingState message="Loading batch monitor..." />;
  if (error) return <ErrorState message={error} onRetry={fetchBatches} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 border-b border-border pb-4">
        <h2 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          Upcoming Batch Monitor
        </h2>
        <p className="text-muted-foreground text-sm flex items-center gap-1">
          <Info className="h-4 w-4" /> Pre-screen scheduled lots before manufacturing execution.
        </p>
      </div>

      {analyzingId && (
        <div className="p-4 bg-primary/10 border border-primary/20 text-primary rounded-md flex items-center gap-3 text-sm font-medium">
          <div className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
          Running inference on batch {analyzingId}...
        </div>
      )}

      <BatchRiskTable batches={batches} onAnalyzeClick={handleAnalyzeClick} />

      <div className="mt-8 rounded-xl border border-border bg-card p-6">
        <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-muted-foreground" />
          Risk Thresholds
        </h4>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="p-3 bg-destructive/5 border border-destructive/20 rounded-md">
            <span className="font-bold text-destructive block mb-1">HIGH RISK</span>
            <span className="text-muted-foreground">Failure Probability {'>'} 70%</span>
          </div>
          <div className="p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-md">
            <span className="font-bold text-yellow-500 block mb-1">MEDIUM RISK</span>
            <span className="text-muted-foreground">Failure Probability 40% - 70%</span>
          </div>
          <div className="p-3 bg-green-500/5 border border-green-500/20 rounded-md">
            <span className="font-bold text-green-500 block mb-1">LOW RISK</span>
            <span className="text-muted-foreground">Failure Probability {'<'} 40%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
