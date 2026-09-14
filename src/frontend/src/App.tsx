import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, Layers, BarChart2, ShieldAlert, Clock, Server } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import LotAnalyzer from './pages/LotAnalyzer';
import Results from './pages/Results';
import Batches from './pages/Batches';
import History from './pages/History';
import SystemInfo from './pages/SystemInfo';

function Navigation() {
  const location = useLocation();
  const navItems = [
    { path: '/', label: 'Dashboard', icon: BarChart2 },
    { path: '/analyzer', label: 'Lot Analyzer', icon: Activity },
    { path: '/batches', label: 'Upcoming Batches', icon: ShieldAlert },
    { path: '/history', label: 'History', icon: Clock },
    { path: '/system', label: 'System / Models', icon: Server },
  ];

  return (
    <nav className="w-64 bg-card border-r border-border h-screen sticky top-0 flex flex-col">
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3 text-primary">
          <Layers className="h-6 w-6 text-blue-500" />
          <h1 className="font-bold text-lg tracking-tight">S1 Analyzer</h1>
        </div>
        <p className="text-xs text-muted-foreground mt-1 uppercase tracking-widest font-semibold">VisionX Control Room</p>
      </div>
      
      <div className="flex-1 py-4 flex flex-col gap-1 px-3">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                isActive 
                  ? 'bg-secondary text-primary' 
                  : 'text-muted-foreground hover:bg-secondary/50 hover:text-primary'
              }`}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </div>
      <div className="p-4 border-t border-border text-xs text-muted-foreground text-center">
        IBM Hackathon 2026
      </div>
    </nav>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex bg-background text-foreground">
      <Navigation />
      <main className="flex-1 overflow-x-hidden">
        <div className="max-w-7xl mx-auto w-full p-8">
          {children}
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analyzer" element={<LotAnalyzer />} />
          <Route path="/results/:lotId" element={<Results />} />
          <Route path="/batches" element={<Batches />} />
          <Route path="/history" element={<History />} />
          <Route path="/system" element={<SystemInfo />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
