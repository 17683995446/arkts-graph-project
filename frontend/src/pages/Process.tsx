
import React from 'react';
import { Clock, RefreshCw, Database, Code2, Zap, CheckCircle2 } from 'lucide-react';

export const Process: React.FC = () => {
  const steps = [
    {
      icon: Clock,
      title: '1. Debounce Window',
      description: 'Wait 200ms after last file change to avoid excessive processing',
      time: '200ms',
    },
    {
      icon: RefreshCw,
      title: '2. Batch Changes',
      description: 'Collect all changed files and process them together',
      time: 'N/A',
    },
    {
      icon: Code2,
      title: '3. Parse ArkTS',
      description: 'Analyze source code to extract classes, methods, and calls',
      time: '~10-100ms/file',
    },
    {
      icon: Database,
      title: '4. Delete & Insert',
      description: 'Remove old entries for changed files and insert new ones',
      time: '~1-10ms/file',
    },
    {
      icon: Zap,
      title: '5. WebSocket Notify',
      description: 'Broadcast update to all connected clients',
      time: '~1ms',
    },
    {
      icon: CheckCircle2,
      title: '6. Complete',
      description: 'Graph visualization updated in real-time',
      time: 'Complete!',
    },
  ];

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-6">Update Process Flow</h1>
      <div className="bg-slate-800 rounded-xl p-8">
        <div className="space-y-6">
          {steps.map((step, i) => (
            <div
              key={i}
              className="flex items-start space-x-6"
            >
              <div className="flex flex-col items-center">
                <div className="p-4 bg-gradient-to-br from-cyan-500/20 to-emerald-500/20 rounded-full border border-cyan-500/30">
                  <step.icon className="w-8 h-8 text-cyan-400" />
                </div>
                {i < steps.length - 1 && (
                  <div className="w-0.5 h-12 bg-gradient-to-b from-cyan-500/50 to-emerald-500/50 mt-4" />
                )}
              </div>
              <div className="flex-1 py-2">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xl font-semibold text-white">{step.title}</h3>
                  <span className="px-3 py-1 bg-emerald-950/50 text-emerald-400 rounded-full text-sm">
                    {step.time}
                  </span>
                </div>
                <p className="text-slate-400">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
