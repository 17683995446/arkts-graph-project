
import React, { useState } from 'react';
import { useApi } from '../api';
import { Send, Database, AlertCircle, CheckCircle2 } from 'lucide-react';

export const Query: React.FC = () => {
  const { sendQuery } = useApi();
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const exampleQueries = [
    'Show all files',
    'Show all classes',
    'Count methods per class',
    'Show all method calls',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await sendQuery(question);
      setResult(response);
    } catch (err) {
      setError('Query failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-6">Natural Language Query</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800 rounded-xl p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">
                  Ask a question about your codebase
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g., 'Show all classes'"
                    className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                  />
                  <button
                    type="submit"
                    disabled={loading || !question.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                  >
                    <Send className="w-5 h-5 text-white" />
                  </button>
                </div>
              </div>
            </form>
            <div className="mt-6">
              <p className="text-sm text-slate-400 mb-3">Try these examples:</p>
              <div className="flex flex-wrap gap-2">
                {exampleQueries.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setQuestion(q)}
                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
          {error && (
            <div className="bg-red-950/50 border border-red-500/50 rounded-xl p-6 flex items-start space-x-3">
              <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-400">{error}</p>
            </div>
          )}
          {result && (
            <div className="bg-slate-800 rounded-xl p-6">
              <div className="flex items-center space-x-3 mb-4">
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                <h3 className="text-xl font-semibold text-white">Result</h3>
              </div>
              {result.sql && (
                <div className="mb-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Database className="w-4 h-4 text-cyan-400" />
                    <span className="text-slate-400 text-sm">Generated SQL</span>
                  </div>
                  <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm text-cyan-300">
                    {result.sql}
                  </div>
                </div>
              )}
              {result.error ? (
                <div className="bg-red-950/30 border border-red-500/30 rounded-lg p-4">
                  <p className="text-red-400">{result.error}</p>
                </div>
              ) : (
                <div>
                  <div className="bg-slate-900 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-slate-800">
                          <tr>
                            {result.result.length > 0 &&
                              Object.keys(result.result[0]).map((key) => (
                                <th key={key} className="px-4 py-3 text-left text-slate-400 font-medium">
                                  {key}
                                </th>
                              ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                          {result.result.map((row: any, i: number) => (
                            <tr key={i} className="hover:bg-slate-800/50">
                              {Object.values(row).map((value, j) => (
                                <td key={j} className="px-4 py-3 text-slate-300">
                                  {String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="bg-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Database Schema</h3>
          <div className="space-y-4">
            <div>
              <h4 className="text-cyan-400 font-medium mb-2">files</h4>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>id (INTEGER)</li>
                <li>path (TEXT)</li>
                <li>hash (TEXT)</li>
                <li>created_at (DATETIME)</li>
                <li>updated_at (DATETIME)</li>
              </ul>
            </div>
            <div>
              <h4 className="text-emerald-400 font-medium mb-2">classes</h4>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>id (INTEGER)</li>
                <li>file_id (INTEGER)</li>
                <li>name (TEXT)</li>
                <li>flags (INTEGER)</li>
              </ul>
            </div>
            <div>
              <h4 className="text-violet-400 font-medium mb-2">methods</h4>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>id (INTEGER)</li>
                <li>class_id (INTEGER)</li>
                <li>name (TEXT)</li>
              </ul>
            </div>
            <div>
              <h4 className="text-amber-400 font-medium mb-2">calls</h4>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>caller_id (INTEGER)</li>
                <li>callee_id (INTEGER)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
