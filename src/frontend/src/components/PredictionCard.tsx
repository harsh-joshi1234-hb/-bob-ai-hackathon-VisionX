import { cn } from './RiskCard';
import { Activity, Target } from 'lucide-react';

interface PredictionCardProps {
  title: string;
  prediction: string;
  probability?: number;
  confidence?: number;
  type: 'wafer' | 'process';
}

export function PredictionCard({ title, prediction, probability, confidence, type }: PredictionCardProps) {
  const Icon = type === 'wafer' ? Target : Activity;
  const isFailed = prediction.toUpperCase() === 'FAIL' || (prediction !== 'none' && type === 'wafer');
  const isNormal = prediction.toUpperCase() === 'PASS' || prediction === 'none';
  
  return (
    <div className="rounded-xl border border-border bg-card text-card-foreground shadow-sm overflow-hidden flex flex-col">
      <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
        <h3 className="tracking-tight text-sm font-medium">{title}</h3>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="p-6 pt-0 flex-1 flex flex-col">
        <div className={cn(
          "text-2xl font-bold uppercase",
          isFailed ? "text-destructive" : isNormal ? "text-green-500" : "text-yellow-500"
        )}>
          {prediction}
        </div>
        
        {probability !== undefined && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-muted-foreground">Failure Probability</span>
              <span className="font-medium">{(probability * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-1.5">
              <div 
                className={cn(
                  "h-1.5 rounded-full",
                  probability > 0.7 ? "bg-destructive" : probability > 0.3 ? "bg-yellow-500" : "bg-green-500"
                )} 
                style={{ width: `${Math.min(100, Math.max(0, probability * 100))}%` }}
              ></div>
            </div>
          </div>
        )}
        
        {confidence !== undefined && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-muted-foreground">Model Confidence</span>
              <span className="font-medium">{(confidence * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-1.5">
              <div 
                className="bg-primary h-1.5 rounded-full"
                style={{ width: `${Math.min(100, Math.max(0, confidence * 100))}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
