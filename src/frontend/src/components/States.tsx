import { Loader2 } from 'lucide-react';

export function LoadingState({ message = "Analyzing..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 min-h-[400px] border border-border border-dashed rounded-lg bg-card/50">
      <Loader2 className="h-10 w-10 text-primary animate-spin mb-4" />
      <h3 className="text-lg font-medium text-foreground">{message}</h3>
      <p className="text-sm text-muted-foreground mt-2 text-center max-w-sm">
        Running deterministic ML models and querying IBM watsonx.ai for insights. Please wait.
      </p>
    </div>
  );
}

import { AlertTriangle } from 'lucide-react';

export function ErrorState({ message, onRetry }: { message: string, onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 min-h-[400px] border border-destructive/20 rounded-lg bg-destructive/5">
      <AlertTriangle className="h-10 w-10 text-destructive mb-4" />
      <h3 className="text-lg font-medium text-foreground">Analysis Failed</h3>
      <p className="text-sm text-muted-foreground mt-2 text-center max-w-sm">
        {message}
      </p>
      {onRetry && (
        <button 
          onClick={onRetry}
          className="mt-6 px-4 py-2 bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-md text-sm font-medium transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
