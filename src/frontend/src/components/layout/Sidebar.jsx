import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FlaskConical, History, Database, Cpu } from 'lucide-react';

const Sidebar = () => {
  return (
    <div className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col h-screen fixed left-0 top-0">
      <div className="p-6">
        <h1 className="text-xl font-bold text-white tracking-wider flex items-center gap-2">
          <Cpu className="text-blue-500" /> S1 ANALYZER
        </h1>
        <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest">Semiconductor AI</p>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-4">
        <NavLink 
          to="/dashboard" 
          className={({isActive}) => `flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${isActive ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'hover:bg-slate-800 hover:text-white'}`}
        >
          <LayoutDashboard size={18} /> Dashboard
        </NavLink>
        
        <NavLink 
          to="/" 
          className={({isActive}) => `flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${isActive ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'hover:bg-slate-800 hover:text-white'}`}
        >
          <FlaskConical size={18} /> Lot Analyzer
        </NavLink>
        
        <NavLink 
          to="/upcoming-batches" 
          className={({isActive}) => `flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${isActive ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'hover:bg-slate-800 hover:text-white'}`}
        >
          <Database size={18} /> Batch Risk Monitor
        </NavLink>
        
        <NavLink 
          to="/history" 
          className={({isActive}) => `flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${isActive ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'hover:bg-slate-800 hover:text-white'}`}
        >
          <History size={18} /> Analysis History
        </NavLink>
        
        <NavLink 
          to="/models" 
          className={({isActive}) => `flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${isActive ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'hover:bg-slate-800 hover:text-white'}`}
        >
          <Cpu size={18} /> Models Info
        </NavLink>
      </nav>
      
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
          Systems Online
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
