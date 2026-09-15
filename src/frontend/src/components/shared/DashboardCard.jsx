import React from 'react';

const DashboardCard = ({ title, value, icon, description, trend, trendValue, color = "blue" }) => {
  const colorMap = {
    blue: "text-blue-500 bg-blue-500/10 border-blue-500/20",
    emerald: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
    rose: "text-rose-500 bg-rose-500/10 border-rose-500/20",
    amber: "text-amber-500 bg-amber-500/10 border-amber-500/20",
    slate: "text-slate-400 bg-slate-800 border-slate-700",
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-slate-400 text-sm font-medium">{title}</p>
          <h3 className="text-3xl font-bold text-white mt-2">{value}</h3>
        </div>
        <div className={`p-3 rounded-lg border ${colorMap[color]}`}>
          {icon}
        </div>
      </div>
      
      {(description || trend) && (
        <div className="mt-4 flex items-center text-sm">
          {trend && (
            <span className={`font-medium mr-2 ${trend === 'up' ? 'text-emerald-400' : 'text-rose-400'}`}>
              {trend === 'up' ? '↑' : '↓'} {trendValue}
            </span>
          )}
          <span className="text-slate-500">{description}</span>
        </div>
      )}
    </div>
  );
};

export default DashboardCard;
