import React from 'react';

const StatusBadge = ({ status }) => {
  let colorClass = "bg-slate-800 text-slate-300 border-slate-700";
  
  switch (status?.toUpperCase()) {
    case 'NORMAL':
    case 'PASS':
    case 'COMPLETE':
      colorClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      break;
    case 'WATCH':
    case 'PENDING':
    case 'PROCESSING':
      colorClass = "bg-amber-500/10 text-amber-400 border-amber-500/20";
      break;
    case 'HIGH':
    case 'FAIL':
    case 'FAILED':
      colorClass = "bg-rose-500/10 text-rose-400 border-rose-500/20";
      break;
    case 'CRITICAL':
      colorClass = "bg-red-600 text-white border-red-500 font-bold animate-pulse";
      break;
    case 'NONE':
      colorClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      break;
    default:
      if (status && status !== 'Unknown') {
          // generic defect classes
          colorClass = "bg-rose-500/10 text-rose-400 border-rose-500/20";
      }
      break;
  }

  return (
    <span className={`px-2.5 py-1 rounded-md text-xs font-semibold border uppercase tracking-wider ${colorClass}`}>
      {status || 'UNKNOWN'}
    </span>
  );
};

export default StatusBadge;
