
import React, { useState, useEffect } from 'react';
import { useApi } from '../api';
import { Activity, Database, FileText, Clock, CheckCircle2, AlertCircle } from 'lucide-react';

export const Status: React.FC = () => {
  const { status, files } = useApi();
  const [history, setHistory] = useState<{ time: string; message: string; type: string }[]>([]);

  useEffect(() => {
    if (status) {
      const time = new Date().toLocaleTimeString();
      let message = '';
      let type = 'info';

      switch (status.type) {
        case 'file_changed':
          message = `File changed: ${status.payload.path}`;
          type = 'info';
          break;
        case 'sync_complete':
          message = 'Sync complete';
          type = 'success';
          break;
        case 'sync_start':
          message = 'Starting sync...';
          type = 'info';
          break;
        default:
          message = JSON.stringify(status);
          type = 'info';
      }

      setHistory((prev) => [
        { time, message, type },
        ...prev.slice(0, 49),
      ]);
    }
  }, [status]);

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return CheckCircle2;
      case 'error':
        return AlertCircle;
      default:
        return Activity;
    }
  };

  const getColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-emerald-400 bg-emerald-950/30';
      case 'error':
        return 'text-red-400 bg-red-950/30';
      default:
        return 'text-cyan-400 bg-cyan-950/30';
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-6">System Status</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Activity className="w-6 h-6 text-cyan-400" />
              <h2 className="text-xl font-semibold text-white">Live Updates</h2>
            </div>
            <div className="bg-slate-900 rounded-lg p-4 max-h-[500px] overflow-y-auto space-y-2">
              {history.length === 0 ? (
                <p className="text-slate-500 text-center py-8">Waiting for updates...</p>
              ) : (
                history.map((item, i) => {
                  const Icon = getIcon(item.type);
                  return (
                    <div
                      key={i}
                      className="flex items-center space-x-3 px-4 py-3 bg-slate-800/50 rounded-lg"
                    >
                      <Icon className={`w-5 h-5 ${getColor(item.type).split(' ')[0]}`} />
                      <span className="text-slate-400 text-sm w-20">{item.time}</span>
                      <span className="text-slate-300">{item.message}</span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Database className="w-6 h-6 text-emerald-400" />
              <h2 className="text-xl font-semibold text-white">Stats</h2>
            </div>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  <span className="text-slate-400">Files</span>
                </div>
                <span className="text-white font-semibold">{files.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-violet-400" />
                  <span className="text-slate-400">Uptime</span>
                </div>
                <span className="text-white font-semibold">Active</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Files</h3>
            <div className="space-y-2">
              {files.slice(0, 5).map((file) => (
                <div
                  key={file.id}
                  className="flex items-center space-x-2 px-3 py-2 bg-slate-700 rounded-lg"
                >
                  <FileText className="w-4 h-4 text-cyan-400" />
                  <span className="text-slate-300 text-sm truncate">
                    {file.path.split('/').pop()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
