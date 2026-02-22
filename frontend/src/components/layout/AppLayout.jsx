import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(
    localStorage.getItem('sidebar_collapsed') === '1'
  );

  useEffect(() => {
    localStorage.setItem('sidebar_collapsed', sidebarCollapsed ? '1' : '0');
  }, [sidebarCollapsed]);

  const sidebarWidth = sidebarCollapsed ? 80 : 256;

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%)' }}>
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed((value) => !value)} />

      <div
        className="flex min-h-screen flex-col transition-all duration-300"
        style={{ marginLeft: `${sidebarWidth}px` }}
      >
        <Topbar onToggleSidebar={() => setSidebarCollapsed((value) => !value)} />
        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
