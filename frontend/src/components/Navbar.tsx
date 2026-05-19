
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Database, Activity, Code2, MessageSquare, Home } from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/graph', icon: Database, label: 'Graph' },
    { path: '/architecture', icon: Code2, label: 'Architecture' },
    { path: '/process', icon: Activity, label: 'Process' },
    { path: '/status', icon: Activity, label: 'Status' },
    { path: '/query', icon: MessageSquare, label: 'Query' },
  ];

  return (
    <nav className="bg-slate-900 border-b border-slate-700 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Database className="w-8 h-8 text-cyan-400" />
          <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent">
            ArkTS Knowledge Graph
          </span>
        </div>
        <div className="flex items-center space-x-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  isActive
                    ? 'bg-cyan-900/30 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span className="hidden sm:inline">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};
