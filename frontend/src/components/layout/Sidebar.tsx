import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Network, PlaySquare, MessageSquare, UploadCloud, Cpu } from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();
  const currentPath = location.pathname;

  const menuItems = [
    { name: 'Knowledge Graph', path: '/graph', icon: Network },
    { name: 'Simulations', path: '/simulate', icon: PlaySquare },
    { name: 'RAG Chatbot', path: '/chat', icon: MessageSquare },
    { name: 'Ingestion Portal', path: '/ingest', icon: UploadCloud },
  ];

  return (
    <div className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col min-h-screen">
      {/* Header / Brand logo */}
      <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
        <div className="bg-indigo-600 p-2 rounded-lg text-white">
          <Cpu className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h1 className="font-bold text-lg text-slate-100 tracking-wide">NEXUS</h1>
          <p className="text-xs text-slate-400 font-mono">Platform v1.0</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPath === item.path || (item.path === '/graph' && currentPath === '/');
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 group ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/10'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
              }`}
            >
              <Icon className={`w-5 h-5 transition-transform duration-200 group-hover:scale-105 ${
                isActive ? 'text-white' : 'text-slate-400 group-hover:text-indigo-400'
              }`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer Branding */}
      <div className="p-4 border-t border-slate-800 text-center">
        <p className="text-[10px] text-slate-500 font-mono">Unified Intelligence Platform</p>
      </div>
    </div>
  );
}
