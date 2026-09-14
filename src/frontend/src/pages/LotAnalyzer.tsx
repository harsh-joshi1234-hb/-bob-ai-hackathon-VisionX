import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { LotSummary } from '../api/lotsApi';
import { lotsApi } from '../api/lotsApi';
import { LoadingState, ErrorState } from '../components/States';
import { Cpu, Server, Activity } from 'lucide-react';

export default function LotAnalyzer() {
  const [lots, setLots] = useState<LotSummary[]>([]);
  const [selectedLotId, setSelectedLotId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLots = async () => {
      try {
        const data = await lotsApi.getLots();
        setLots(data);
        if (data.length > 0) {
          setSelectedLotId(data[0].lot_id);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load demo lots.');
      } finally {
        setLoading(false);
      }
    };
    fetchLots();
  }, []);

  const handleAnalyze = async () => {
    if (!selectedLotId) return;
    
    setAnalyzing(true);
    setError(null);
    try {
      // We will actually just navigate to the results page, 
      // and let the results page do the POST analysis if it hasn't been analyzed,
      // or we can do it here. Let's do it here so we show a loading state on the analyzer page.
      const response = await lotsApi.analyzeLot(selectedLotId);
      
      // Navigate to results page, passing the data through state or context.
      // Alternatively, just navigate to results page, and it can fetch history or run analysis.
      // But we just ran it, so let's pass it via state.
      navigate(`/results/${selectedLotId}`, { state: { analysisResult: response } });
      
    } catch (err: any) {
      setError(err.message || 'Analysis failed.');
      setAnalyzing(false);
    }
  };

  if (loading) return <LoadingState message="Connecting to orchestration service..." />;
  if (error && !analyzing) return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  
  if (analyzing) {
    return <LoadingState message={`Running Multimodal Analysis on ${selectedLotId}...`} />;
  }

  const selectedLot = lots.find(l => l.lot_id === selectedLotId);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Lot Analyzer</h2>
        <p className="text-muted-foreground text-sm">
          Select an application-level demo lot to run multimodal inference across independent datasets.
        </p>
      </div>

      <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
        <div className="space-y-4">
          <label className="text-sm font-medium text-foreground flex items-center gap-2">
            Demo Lot Selector:
          </label>
          <select 
            className="w-full md:w-1/2 flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            value={selectedLotId}
            onChange={(e) => setSelectedLotId(e.target.value)}
          >
            {lots.map(lot => (
              <option key={lot.lot_id} value={lot.lot_id}>
                {lot.lot_id} {lot.status === 'COMPLETE' ? '(Previously Analyzed)' : '(Pending)'}
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedLot && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm flex flex-col">
            <div className="px-6 py-4 border-b border-border bg-muted/50 flex items-center gap-2">
              <Cpu className="h-4 w-4 text-muted-foreground" />
              <h3 className="font-semibold text-sm">Wafer Map Input</h3>
            </div>
            <div className="p-6 flex-1 flex flex-col items-center justify-center min-h-[250px] bg-background/50">
              <div className="w-48 h-48 rounded-full border-2 border-border/50 border-dashed flex items-center justify-center bg-secondary/30 relative">
                <span className="text-xs text-muted-foreground font-medium uppercase tracking-widest absolute">Raw .npy Scan</span>
                {/* We don't have the image blob in the frontend easily without an endpoint, so we show a stylized placeholder */}
                <div className="w-full h-full rounded-full bg-blue-500/5 blur-xl"></div>
              </div>
              <p className="text-xs text-muted-foreground mt-6 font-mono bg-muted px-2 py-1 rounded">
                Source: {selectedLot.wafer_image_path.split(/[\\/]/).pop()}
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm flex flex-col">
            <div className="px-6 py-4 border-b border-border bg-muted/50 flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <h3 className="font-semibold text-sm">Process Parameter Vector</h3>
            </div>
            <div className="p-6 flex-1 flex flex-col min-h-[250px]">
              <div className="grid grid-cols-4 gap-2 text-[10px] font-mono text-muted-foreground mt-4">
                {Array.from({ length: 24 }).map((_, i) => (
                  <div key={i} className="bg-secondary/50 p-2 rounded text-center border border-border/50">
                    F_{i.toString().padStart(2, '0')}
                    <div className="text-foreground mt-1 font-bold">...</div>
                  </div>
                ))}
              </div>
              <div className="mt-auto pt-6 flex justify-center">
                <p className="text-xs text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
                  Shape: [1, 24] (SECOM Format)
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-destructive/10 border border-destructive/20 text-destructive text-sm rounded-md">
          {error}
        </div>
      )}

      <div className="flex justify-end pt-4">
        <button 
          onClick={handleAnalyze}
          disabled={!selectedLotId || analyzing}
          className="px-8 py-3 bg-primary text-primary-foreground hover:bg-primary/90 rounded-md text-sm font-bold tracking-wide transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <Server className="h-4 w-4" />
          EXECUTE MULTIMODAL ANALYSIS
        </button>
      </div>
    </div>
  );
}
