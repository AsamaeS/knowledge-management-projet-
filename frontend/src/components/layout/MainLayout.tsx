import React from 'react';
import Sidebar from './Sidebar';

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex bg-slate-950 min-h-screen text-slate-100 overflow-hidden">
      {/* Permanent Sidebar Left */}
      <Sidebar />

      {/* Main Panel Content Scrollable Right */}
      <main className="flex-1 flex flex-col min-h-screen overflow-hidden bg-slate-950">
        <div className="flex-1 relative flex flex-col overflow-y-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
