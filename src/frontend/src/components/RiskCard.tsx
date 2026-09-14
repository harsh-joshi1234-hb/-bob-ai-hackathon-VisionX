
import { ShieldAlert, CheckCircle, AlertTriangle } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

interface RiskCardProps {
  title: string;
  level: string; // HIGH, MEDIUM, LOW
  score?: number;
  description?: string;
  className?: string;
}

export function RiskCard({ title, level, score, description, className }: RiskCardProps) {
  const isHigh = level.toUpperCase() === 'HIGH';
  const isMedium = level.toUpperCase() === 'MEDIUM';
  
  return (
    <div className={cn("rounded-xl border border-border bg-card text-card-foreground shadow-sm overflow-hidden", className)}>
      <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
        <h3 className="tracking-tight text-sm font-medium">{title}</h3>
        {isHigh ? (
          <ShieldAlert className="h-5 w-5 text-destructive" />
        ) : isMedium ? (
          <AlertTriangle className="h-5 w-5 text-yellow-500" />
        ) : (
          <CheckCircle className="h-5 w-5 text-green-500" />
        )}
      </div>
      <div className="p-6 pt-0">
        <div className="flex items-baseline gap-2">
          <div className={cn(
            "text-2xl font-bold uppercase",
            isHigh ? "text-destructive" : isMedium ? "text-yellow-500" : "text-green-500"
          )}>
            {level} RISK
          </div>
          {score !== undefined && (
            <span className="text-sm text-muted-foreground">
              Score: {score.toFixed(2)}
            </span>
          )}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground mt-2">{description}</p>
        )}
      </div>
    </div>
  );
}
