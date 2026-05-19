
import React, { useMemo } from 'react';
import { useApi } from '../api';

export const Graph: React.FC = () => {
  const { files, classes, methods, calls } = useApi();

  const nodes = useMemo(() => {
    const allNodes: any[] = [];

    files.forEach((file) => {
      allNodes.push({
        id: `file-${file.id}`,
        label: file.path.split('/').pop(),
        type: 'file',
        color: '#22d3ee',
      });
    });

    classes.forEach((cls) => {
      allNodes.push({
        id: `class-${cls.id}`,
        label: cls.name,
        type: 'class',
        color: '#34d399',
      });
    });

    methods.forEach((method) => {
      allNodes.push({
        id: `method-${method.id}`,
        label: method.name,
        type: 'method',
        color: '#a78bfa',
      });
    });

    return allNodes;
  }, [files, classes, methods]);


  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-6">Knowledge Graph</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Visualization</h2>
          <div className="bg-slate-900 rounded-lg p-4 min-h-[400px] flex items-center justify-center">
            <p className="text-slate-400">
              Interactive graph visualization would be here (using d3.js, cytoscape.js, or vis.js)
            </p>
          </div>
        </div>
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Statistics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Files</span>
                <span className="text-cyan-400 font-semibold">{files.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Classes</span>
                <span className="text-emerald-400 font-semibold">{classes.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Methods</span>
                <span className="text-violet-400 font-semibold">{methods.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Calls</span>
                <span className="text-amber-400 font-semibold">{calls.length}</span>
              </div>
            </div>
          </div>
          <div className="bg-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Nodes</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {nodes.map((node) => (
                <div
                  key={node.id}
                  className="flex items-center space-x-2 px-3 py-2 bg-slate-700 rounded-lg"
                >
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: node.color }}
                  />
                  <span className="text-slate-300 text-sm">{node.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
