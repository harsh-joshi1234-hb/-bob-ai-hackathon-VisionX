import { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import type { AnalysisResponse } from '../api/lotsApi';
import { lotsApi } from '../api/lotsApi';
import { LoadingState, ErrorState } from '../components/States';
import { RootCauseChart } from '../components/RootCauseChart';
import { RecommendationPanel } from '../components/RecommendationPanel';
import { ArrowLeft, GitCommit, Search, ShieldAlert, Cpu, Activity, Lightbulb, Server, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '../components/RiskCard';

export default function Results() {
  const { lotId } = useParams<{ lotId: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [result, setResult] = useState<AnalysisResponse | null>(location.state?.analysisResult || null);
  const [lotDetails, setLotDetails] = useState<any>(null);
  const [loading, setLoading] = useState(!result);
  const [error, setError] = useState<string | null>(null);
  const [showRawEvidence, setShowRawEvidence] = useState(false);

  useEffect(() => {
    if (lotId) {
      const fetchData = async () => {
        try {
          // Fetch raw lot details for the "Raw Evidence" section
          const details = await lotsApi.getLot(lotId);
          setLotDetails(details);
          
          if (!result) {
            // If we landed here without state, run analysis
            const data = await lotsApi.analyzeLot(lotId);
            setResult(data);
          }
        } catch (err: any) {
          setError(err.message || 'Failed to fetch analysis results.');
        } finally {
          setLoading(false);
        }
      };
      fetchData();
    }
  }, [lotId, result]);

  if (loading) return <LoadingState message={`Running multimodal analysis for ${lotId}...`} />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  if (!result) return <ErrorState message="No results found." />;

  // Translate overall risk level to specific top-level status
  const getStatusDisplay = (level: string) => {
    const l = level.toUpperCase();
    if (l === 'HIGH' || l === 'CRITICAL') return { text: l === 'HIGH' ? 'HIGH RISK' : 'CRITICAL', color: 'text-destructive', bg: 'bg-destructive/10', border: 'border-destructive/20' };
    if (l === 'MEDIUM') return { text: 'WATCH', color: 'text-yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' };
    return { text: 'NORMAL', color: 'text-green-500', bg: 'bg-green-500/10', border: 'border-green-500/20' };
  };
  
  const statusInfo = getStatusDisplay(result.overall_risk.level);
  
  const waferIsFailed = result.wafer_analysis.prediction !== 'none';
  const processIsFailed = result.process_analysis.prediction === 'FAIL';

  return (
    <div className="space-y-8 pb-12 max-w-6xl mx-auto">
      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-6">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-md transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
              Analysis Results <span className="text-muted-foreground font-light">/ {result.lot_id}</span>
            </h2>
            <div className="flex items-center gap-4 mt-2">
              <p className="text-muted-foreground text-xs font-mono flex items-center gap-1 bg-secondary px-2 py-1 rounded">
                <GitCommit className="h-3 w-3" /> {new Date(result.analysis_timestamp).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        
        <div className={cn("px-6 py-2 rounded-lg border-2 flex items-center gap-3", statusInfo.bg, statusInfo.border)}>
          <ShieldAlert className={cn("h-6 w-6", statusInfo.color)} />
          <div className="flex flex-col">
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Top-Level Status</span>
            <span className={cn("text-xl font-black uppercase tracking-tight", statusInfo.color)}>{statusInfo.text}</span>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        
        {/* 1. DETECT */}
        <section className="rounded-xl border border-border bg-card shadow-sm overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-border bg-muted/40 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-primary/20 p-1.5 rounded-md">
                <Search className="h-4 w-4 text-primary" />
              </div>
              <h3 className="font-bold text-base tracking-wide uppercase">1. Detect</h3>
            </div>
            <span className="text-[10px] font-bold tracking-widest uppercase bg-secondary/50 text-muted-foreground px-2 py-1 rounded border border-border/50">
              Evidence: WaferMap CNN
            </span>
          </div>
          
          <div className="p-6 flex gap-6 items-center">
            <div className="w-32 h-32 rounded-full border-2 border-border/50 border-dashed flex items-center justify-center bg-secondary/30 relative shrink-0">
              <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-widest absolute">Raw Scan</span>
              <div className={cn(
                "w-full h-full rounded-full blur-xl opacity-30",
                waferIsFailed ? "bg-destructive" : "bg-green-500"
              )}></div>
            </div>
            <div className="flex-1 space-y-4">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold mb-1">Predicted Defect</p>
                <p className={cn("text-2xl font-black uppercase", waferIsFailed ? "text-destructive" : "text-green-500")}>
                  {result.wafer_analysis.prediction}
                </p>
              </div>
              <div>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-muted-foreground font-medium uppercase">Model Confidence</span>
                  <span className="font-bold font-mono">{(result.wafer_analysis.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full"
                    style={{ width: `${Math.min(100, Math.max(0, result.wafer_analysis.confidence * 100))}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 2. PREDICT */}
        <section className="rounded-xl border border-border bg-card shadow-sm overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-border bg-muted/40 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-primary/20 p-1.5 rounded-md">
                <Activity className="h-4 w-4 text-primary" />
              </div>
              <h3 className="font-bold text-base tracking-wide uppercase">2. Predict</h3>
            </div>
            <span className="text-[10px] font-bold tracking-widest uppercase bg-secondary/50 text-muted-foreground px-2 py-1 rounded border border-border/50">
              Evidence: SECOM Model
            </span>
          </div>
          
          <div className="p-6 flex flex-col justify-center flex-1 space-y-6">
            <div className="flex items-end justify-between border-b border-border/50 pb-4">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold mb-1">Process Risk Prediction</p>
                <p className={cn("text-3xl font-black uppercase", processIsFailed ? "text-destructive" : "text-green-500")}>
                  {result.process_analysis.prediction}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold mb-1">Overall Level</p>
                <p className="text-lg font-bold uppercase">{result.overall_risk.level}</p>
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-muted-foreground font-medium uppercase">Failure Probability</span>
                <span className="font-bold font-mono">{(result.process_analysis.probability * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2">
                <div 
                  className={cn(
                    "h-2 rounded-full",
                    result.process_analysis.probability > 0.7 ? "bg-destructive" : result.process_analysis.probability > 0.3 ? "bg-yellow-500" : "bg-green-500"
                  )} 
                  style={{ width: `${Math.min(100, Math.max(0, result.process_analysis.probability * 100))}%` }}
                ></div>
              </div>
            </div>
          </div>
        </section>

        {/* 3. EXPLAIN */}
        <section className="rounded-xl border border-border bg-card shadow-sm overflow-hidden flex flex-col lg:col-span-2">
          <div className="px-6 py-4 border-b border-border bg-muted/40 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-primary/20 p-1.5 rounded-md">
                <Cpu className="h-4 w-4 text-primary" />
              </div>
              <h3 className="font-bold text-base tracking-wide uppercase">3. Explain</h3>
            </div>
            <span className="text-[10px] font-bold tracking-widest uppercase bg-secondary/50 text-muted-foreground px-2 py-1 rounded border border-border/50">
              Evidence: SHAP Explainer
            </span>
          </div>
          
          <div className="p-6">
            <p className="text-sm text-muted-foreground mb-4">
              Top contributing process signals driving the SECOM model prediction. 
              <span className="text-destructive font-medium ml-1">Red indicates increased risk of failure.</span>
            </p>
            <div className="rounded-lg border border-border/50 bg-background p-4">
              <RootCauseChart data={result.root_causes.map((rc, idx) => ({ feature: rc.feature_name, contribution: rc.importance, direction: rc.direction as any, rank: idx }))} />
            </div>
          </div>
        </section>

        {/* 4. ACT */}
        <section className="rounded-xl border border-border bg-card shadow-sm overflow-hidden flex flex-col lg:col-span-2">
           <div className="px-6 py-4 border-b border-border bg-muted/40 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-primary/20 p-1.5 rounded-md">
                <Lightbulb className="h-4 w-4 text-primary" />
              </div>
              <h3 className="font-bold text-base tracking-wide uppercase">4. Act</h3>
            </div>
            <span className="text-[10px] font-bold tracking-widest uppercase bg-secondary/50 text-muted-foreground px-2 py-1 rounded border border-border/50">
              Evidence: Generative AI & Orchestrator
            </span>
          </div>
          
          <div className="p-6 bg-blue-500/5">
             <RecommendationPanel 
              recommendations={result.recommendations}
              aiExplanation={result.ai_explanation}
            />
          </div>
        </section>
      </div>
      
      {/* RAW EVIDENCE SECTION */}
      {lotDetails && (
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <button 
            onClick={() => setShowRawEvidence(!showRawEvidence)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Server className="h-4 w-4 text-muted-foreground" />
              <h4 className="font-semibold text-sm">View Raw Evidence (Process Database)</h4>
            </div>
            {showRawEvidence ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          
          {showRawEvidence && (
            <div className="p-6 border-t border-border bg-background font-mono text-[10px] text-muted-foreground overflow-x-auto">
              <p className="text-xs mb-3 text-foreground font-sans font-medium">Underlying Process Vectors for {lotId}:</p>
              {lotDetails.process_records?.map((pr: any, i: number) => (
                <div key={i} className="mb-4 last:mb-0">
                  <div className="mb-1">Record ID: {pr.source_record_id || pr.id}</div>
                  <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
                    {pr.features.map((val: number | null, idx: number) => (
                      <div key={idx} className="bg-secondary/50 p-1.5 rounded border border-border/50 flex flex-col">
                        <span className="text-[9px] opacity-70">F_{idx.toString().padStart(2, '0')}</span>
                        <span className="text-foreground font-semibold mt-0.5">{val !== null ? val.toPrecision(4) : 'NULL'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
              {(!lotDetails.process_records || lotDetails.process_records.length === 0) && (
                <div>No process records found for this lot.</div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
