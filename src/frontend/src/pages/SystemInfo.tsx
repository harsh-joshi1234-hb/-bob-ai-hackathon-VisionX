
import { Server, Shield, BrainCircuit, Database } from 'lucide-react';

export default function SystemInfo() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2 border-b border-border pb-4">
        <h2 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          System & Model Information
        </h2>
        <p className="text-muted-foreground text-sm flex items-center gap-1">
          <Server className="h-4 w-4" /> Underlying architecture and active ML models for the S1 Analyzer.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Process Risk Model */}
        <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-border bg-muted/50 flex items-center gap-2">
            <BrainCircuit className="h-5 w-5 text-primary" />
            <h3 className="font-semibold text-base">SECOM Classifier</h3>
          </div>
          <div className="p-6 space-y-4 text-sm flex-1">
            <div className="grid grid-cols-3 gap-2">
              <span className="text-muted-foreground">Type:</span>
              <span className="col-span-2 font-medium">Scikit-learn VotingClassifier</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <span className="text-muted-foreground">Purpose:</span>
              <span className="col-span-2 text-muted-foreground">Predicts overall process risk (PASS/FAIL) from 24 critical sensor parameters.</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <span className="text-muted-foreground">Output:</span>
              <span className="col-span-2 font-mono">"PASS" or "FAIL"</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <span className="text-muted-foreground">Probability:</span>
              <span className="col-span-2 text-green-500 font-medium">Available (predict_proba)</span>
            </div>
          </div>
          <div className="px-6 py-3 bg-muted/30 border-t border-border text-xs text-muted-foreground flex items-center gap-2">
            <Shield className="h-3 w-3" /> Note: Pre-trained binary file cannot be downloaded.
          </div>
        </div>

        {/* Wafer Defect Model */}
        <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-border bg-muted/50 flex items-center gap-2">
            <BrainCircuit className="h-5 w-5 text-primary" />
            <h3 className="font-semibold text-base">WaferMap CNN</h3>
          </div>
          <div className="p-6 space-y-4 text-sm flex-1">
            <div className="grid grid-cols-3 gap-2">
              <span className="text-muted-foreground">Type:</span>
              <span className="col-span-2 font-medium">PyTorch Convolutional Neural Network</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <span className="text-muted-foreground">Purpose:</span>
              <span className="col-span-2 text-muted-foreground">Classifies spatial defect patterns on 64x64 wafer maps (e.g., Center, Edge-Ring).</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <span className="text-muted-foreground">Output:</span>
              <span className="col-span-2 font-mono">Defect Class (e.g., "center")</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <span className="text-muted-foreground">Probability:</span>
              <span className="col-span-2 text-green-500 font-medium">Available (Softmax confidence)</span>
            </div>
          </div>
          <div className="px-6 py-3 bg-muted/30 border-t border-border text-xs text-muted-foreground flex items-center gap-2">
            <Shield className="h-3 w-3" /> Note: Pre-trained binary file cannot be downloaded.
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
         <h3 className="font-semibold text-base mb-4 flex items-center gap-2">
          <Database className="h-5 w-5 text-muted-foreground" />
          Data Integration Layer
        </h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          The application-level demo lots (e.g., <code>LOT-001</code>) dynamically map independent source records from the WM-811K image dataset and the SECOM tabular dataset. This mapping demonstrates our multimodal analysis pipeline working in concert without permanently joining the independent public datasets. The backend orchestrator retrieves these mapped inputs on-the-fly when an analysis is requested.
        </p>
      </div>
    </div>
  );
}
