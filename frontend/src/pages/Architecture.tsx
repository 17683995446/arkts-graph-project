
import React from 'react';
import { Server, Database, Eye, Code2, FileText } from 'lucide-react';

export const Architecture: React.FC = () => {
  const layers = [
    {
      icon: Eye,
      title: 'Frontend',
      description: 'React + TypeScript + Tailwind CSS',
      tech: ['React 18', 'TypeScript', 'Tailwind', 'Vite'],
    },
    {
      icon: Server,
      title: 'Backend',
      description: 'FastAPI + Python',
      tech: ['FastAPI', 'Python 3.10+', 'Uvicorn'],
    },
    {
      icon: Database,
      title: 'Database',
      description: 'SQLite3',
      tech: ['SQLite', 'SQL'],
    },
    {
      icon: FileText,
      title: 'File Monitor',
      description: 'Watchdog',
      tech: ['Watchdog', 'File System Events'],
    },
    {
      icon: Code2,
      title: 'Parser',
      description: 'ArkTS Analyzer',
      tech: ['Custom Parser', 'AST Analysis'],
    },
  ];

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-6">System Architecture</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Architecture Diagram</h2>
          <div className="bg-slate-900 rounded-lg p-8 min-h-[400px] flex flex-col items-center justify-center space-y-6">
            {layers.map((layer, i) => (
              <div
                key={i}
                className="flex items-center space-x-4 w-full max-w-md"
              >
                <div className="p-4 bg-gradient-to-br from-cyan-500/20 to-emerald-500/20 rounded-xl border border-cyan-500/30">
                  <layer.icon className="w-8 h-8 text-cyan-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-semibold">{layer.title}</h3>
                  <p className="text-slate-400 text-sm">{layer.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-6">
          {layers.map((layer, i) => (
            <div key={i} className="bg-slate-800 rounded-xl p-6">
              <div className="flex items-center space-x-4 mb-4">
                <layer.icon className="w-8 h-8 text-cyan-400" />
                <div>
                  <h3 className="text-lg font-semibold text-white">{layer.title}</h3>
                  <p className="text-slate-400 text-sm">{layer.description}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {layer.tech.map((tech, j) => (
                  <span
                    key={j}
                    className="px-3 py-1 bg-cyan-950/50 text-cyan-400 rounded-full text-sm"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
