import type { UpcomingBatch } from '../api/batchesApi';
import { cn } from './RiskCard';
import { useNavigate } from 'react-router-dom';

export function BatchRiskTable({ batches, onAnalyzeClick }: { batches: UpcomingBatch[], onAnalyzeClick?: (id: string) => void }) {
  const navigate = useNavigate();

  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-muted-foreground uppercase bg-muted/50 border-b border-border">
            <tr>
              <th className="px-6 py-3 font-medium">Batch ID</th>
              <th className="px-6 py-3 font-medium">Scheduled</th>
              <th className="px-6 py-3 font-medium">Status</th>
              <th className="px-6 py-3 font-medium">Risk Level</th>
              <th className="px-6 py-3 font-medium">Risk Score</th>
              <th className="px-6 py-3 font-medium text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {batches.map((batch) => {
              const riskLevel = batch.risk_level?.toUpperCase();
              
              return (
                <tr key={batch.batch_id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4 font-medium text-foreground">{batch.batch_id}</td>
                  <td className="px-6 py-4 text-muted-foreground">{new Date(batch.scheduled_at).toLocaleDateString()}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-secondary text-secondary-foreground">
                      {batch.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {riskLevel ? (
                      <span className={cn(
                        "inline-flex items-center px-2 py-1 rounded-md text-xs font-bold",
                        riskLevel === 'HIGH' ? "bg-destructive/10 text-destructive" :
                        riskLevel === 'MEDIUM' ? "bg-yellow-500/10 text-yellow-500" :
                        "bg-green-500/10 text-green-500"
                      )}>
                        {riskLevel}
                      </span>
                    ) : (
                      <span className="text-muted-foreground text-xs">PENDING</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    {batch.predicted_risk !== undefined ? (
                      <span className="font-mono">{(batch.predicted_risk * 100).toFixed(1)}%</span>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {onAnalyzeClick ? (
                      <button 
                        onClick={() => onAnalyzeClick(batch.batch_id)}
                        className="text-xs font-medium text-primary hover:underline"
                      >
                        Run Analysis
                      </button>
                    ) : (
                      <button 
                        onClick={() => navigate(`/batches`)}
                        className="text-xs font-medium text-primary hover:underline"
                      >
                        View Details
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
            
            {batches.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-muted-foreground">
                  No batches found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
