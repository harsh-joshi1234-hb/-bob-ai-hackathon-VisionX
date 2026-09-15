import React, { useState } from 'react';
import { UploadCloud, CheckCircle, AlertCircle, FileText } from 'lucide-react';

export const WaferUploader = ({ onFileSelected }) => {
  const [file, setFile] = useState(null);
  
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      onFileSelected(selected);
    }
  };

  return (
    <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:border-blue-500 transition-colors bg-slate-900/50">
      <input 
        type="file" 
        id="wafer-upload" 
        className="hidden" 
        accept="image/png, image/jpeg, image/jpg"
        onChange={handleFileChange}
      />
      <label htmlFor="wafer-upload" className="cursor-pointer flex flex-col items-center justify-center h-full">
        {file ? (
          <>
            <CheckCircle className="text-emerald-500 mb-3" size={40} />
            <p className="text-slate-200 font-medium mb-1">{file.name}</p>
            <p className="text-slate-500 text-sm">{(file.size / 1024).toFixed(1)} KB</p>
          </>
        ) : (
          <>
            <UploadCloud className="text-slate-400 mb-3" size={40} />
            <p className="text-slate-300 font-medium mb-1">Upload Wafer Map Image</p>
            <p className="text-slate-500 text-sm">Drag & drop or click to browse (PNG, JPG)</p>
          </>
        )}
      </label>
    </div>
  );
};

export const ProcessCsvUploader = ({ onFileSelected }) => {
  const [file, setFile] = useState(null);
  
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      onFileSelected(selected);
    }
  };

  return (
    <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:border-blue-500 transition-colors bg-slate-900/50">
      <input 
        type="file" 
        id="csv-upload" 
        className="hidden" 
        accept=".csv"
        onChange={handleFileChange}
      />
      <label htmlFor="csv-upload" className="cursor-pointer flex flex-col items-center justify-center h-full">
        {file ? (
          <>
            <CheckCircle className="text-emerald-500 mb-3" size={40} />
            <p className="text-slate-200 font-medium mb-1">{file.name}</p>
            <p className="text-slate-500 text-sm">{(file.size / 1024).toFixed(1)} KB</p>
          </>
        ) : (
          <>
            <FileText className="text-slate-400 mb-3" size={40} />
            <p className="text-slate-300 font-medium mb-1">Upload Process Data (CSV)</p>
            <p className="text-slate-500 text-sm">Must contain 24 expected sensor features</p>
          </>
        )}
      </label>
    </div>
  );
};
