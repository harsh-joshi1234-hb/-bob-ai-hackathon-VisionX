import React from 'react';
import Sidebar from './Sidebar';

const Layout = ({ children }) => {
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-200 font-sans">
      <Sidebar />
      <div className="flex-1 ml-64 overflow-x-hidden">
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
