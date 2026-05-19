
import React from 'react';
import { Link } from 'react-router-dom';
import { Database, Code2, Activity, MessageSquare, Zap, GitBranch, Clock } from 'lucide-react';
import { useApi } from '../api';

export const Home: React.FC = () => {
  const { files, classes, methods } = useApi();

  const features = [
    {
      icon: Database,
      title: 'Knowledge Graph',
      description: 'Visualize ArkTS code structure with interactive graphs',
      path: '/graph',
      color: 'text-cyan-400',
    },
    {
      icon: Code2,
      title: 'System Architecture',
      description: 'View the overall system design and architecture',
      path: '/architecture',
      color: 'text-emerald-400',
    },
    {
      icon: Activity,
      title: 'Process Flow',
      description: 'See dynamic update processes and timelines',
      path: '/process',
      color: 'text-violet-400',
    },
    {
      icon: MessageSquare,
      title: 'Natural Language Query',
      description: 'Query your codebase using natural language',
      path: '/query',
      color: 'text-amber-400',
    },
  ];

  const stats = [
    { label: 'Files', value: files.length, icon: Zap },
    { label: 'Classes', value: classes.length, icon: GitBranch },
    { label: 'Methods', value: methods.length, icon: Clock },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-cyan-400 via-emerald-400 to-violet-400 bg-clip-text text-transparent">
            Dynamic ArkTS Knowledge Graph
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Real-time code analysis and visualization for HarmonyOS ArkTS applications.
            Watch your code structure evolve as you develop.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6 hover:border-cyan-500/30 transition-all"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-cyan-950/50 rounded-xl">
                  <stat.icon className="w-8 h-8 text-cyan-400" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white">{stat.value}</p>
                  <p className="text-slate-400">{stat.label}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Link
              key={index}
              to={feature.path}
              className="group bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6 hover:border-slate-600 transition-all hover:transform hover:-translate-y-1"
            >
              <feature.icon className={`w-12 h-12 ${feature.color} mb-4 group-hover:scale-110 transition-transform`} />
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-slate-400">{feature.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};
