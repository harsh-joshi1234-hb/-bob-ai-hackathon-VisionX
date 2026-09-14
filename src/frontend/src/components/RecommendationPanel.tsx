import type { AIExplanation, Recommendation } from '../api/lotsApi';
import { Bot, Lightbulb, CheckSquare, ShieldAlert } from 'lucide-react';

export function RecommendationPanel({
  aiExplanation,
  recommendations
}: {
  aiExplanation?: AIExplanation;
  recommendations: Recommendation[];
}) {
  return (
    <div className="space-y-6">
      {/* Model Predictions (Deterministic) */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="bg-muted px-4 py-3 border-b border-border flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-primary" />
          <h3 className="font-semibold text-sm">Deterministic Model Recommendations</h3>
        </div>
        <div className="p-4 space-y-4">
          {recommendations.length > 0 ? (
            recommendations.map((rec, i) => (
              <div key={i} className="flex flex-col gap-1 border-l-2 border-primary pl-3">
                <span className="font-medium text-foreground">{rec.action}</span>
                <span className="text-sm text-muted-foreground">{rec.reason}</span>
              </div>
            ))
          ) : (
            <div className="text-sm text-muted-foreground">No critical model recommendations.</div>
          )}
        </div>
      </div>

      {/* AI Explanation (Generative) */}
      <div className="rounded-xl border border-blue-500/20 bg-card overflow-hidden shadow-[0_0_15px_rgba(59,130,246,0.05)]">
        <div className="bg-blue-500/10 px-4 py-3 border-b border-blue-500/20 flex items-center gap-2">
          <Bot className="h-4 w-4 text-blue-500" />
          <h3 className="font-semibold text-sm text-blue-500">IBM Bob Intelligence Layer</h3>
        </div>
        
        {aiExplanation?.status === 'success' ? (
          <div className="p-4 space-y-6">
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1">
                <Lightbulb className="h-3 w-3" /> Executive Summary
              </h4>
              <p className="text-sm">{aiExplanation.summary}</p>
            </div>
            
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1">
                <CheckSquare className="h-3 w-3" /> Suggested Actions
              </h4>
              <ul className="list-disc pl-4 space-y-1 text-sm">
                {aiExplanation.corrective_actions.map((act, i) => (
                  <li key={i}>{act}</li>
                ))}
              </ul>
            </div>
            
            <div className="bg-muted/50 p-3 rounded-md border border-border">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">Limitations</h4>
              <ul className="list-disc pl-4 text-xs text-muted-foreground">
                {aiExplanation.limitations.map((lim, i) => (
                  <li key={i}>{lim}</li>
                ))}
              </ul>
            </div>
          </div>
        ) : (
          <div className="p-4 text-sm text-muted-foreground italic">
            {aiExplanation?.message || "AI Explanation service is currently unavailable."}
          </div>
        )}
      </div>
    </div>
  );
}
