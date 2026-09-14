import { useEffect, useState } from 'react';
import type { LotSummary } from '../api/lotsApi';
import { lotsApi } from '../api/lotsApi';
import { LoadingState, ErrorState } from '../components/States';
import { Clock, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function History() {
  const [lots, setLots] = useState<LotSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await lotsApi.getLots();
        // Only show completed lots in history
        setLots(data.filter(l => l.status === 'COMPLETE'));
      } catch (err: any) {
        setError(err.message || 'Failed to fetch history.');
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (loading) return <LoadingState message="Loading analysis history..." />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 border-b border-border pb-4">
        <h2 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          Analysis History
        </h2>
        <p className="text-muted-foreground text-sm flex items-center gap-1">
          <Clock className="h-4 w-4" /> Previously completed lot analyses from the PostgreSQL database.
        </p>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="divide-y divide-border">
          {lots.map(lot => (
            <div key={lot.id} className="p-4 flex items-center justify-between hover:bg-muted/30 transition-colors">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded bg-secondary flex items-center justify-center text-secondary-foreground font-medium text-xs">
                  {lot.lot_id.split('-').pop()}
                </div>
                <div>
                  <h4 className="font-medium text-foreground">{lot.lot_id}</h4>
                  <p className="text-xs text-muted-foreground font-mono">Status: {lot.status}</p>
                </div>
              </div>
              <button 
                onClick={() => navigate(`/results/${lot.lot_id}`)}
                className="flex items-center gap-2 text-sm font-medium text-primary hover:underline px-3 py-1.5"
              >
                View Results <ExternalLink className="h-4 w-4" />
              </button>
            </div>
          ))}
          
          {lots.length === 0 && (
            <div className="p-8 text-center text-muted-foreground">
              No completed analyses found in history.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
