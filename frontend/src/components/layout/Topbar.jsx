import React from 'react';
import { PanelLeft } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import NotificationBell from './NotificationBell';
import ThemeToggle from '../ui/ThemeToggle';

const routeTitles = {
  '/dashboard': 'Dashboard',
  '/attendance': 'Attendance',
  '/food': 'Food',
  '/food-analytics': 'Food Analytics',
  '/remedial': 'Remedial',
  '/students': 'Student Management',
  '/resources': 'Resources',
  '/profile': 'Profile',
};

function Topbar({ onToggleSidebar }) {
  const location = useLocation();
  const { user } = useAuth();
  const title = routeTitles[location.pathname] || 'Smart Campus';

  return (
    <header
      className="sticky top-0 z-30 flex h-16 items-center justify-between border-b px-4 md:px-6"
      style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg)' }}
    >
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleSidebar}
          className="rounded-lg border p-2 transition hover:opacity-90"
          style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg-pink)' }}
          aria-label="Toggle sidebar"
          title="Toggle sidebar"
        >
          <PanelLeft size={18} style={{ color: 'var(--text-color)' }} />
        </button>
        <h1 className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
          {title}
        </h1>
      </div>

      <div className="flex items-center gap-3">
        <ThemeToggle />
        <NotificationBell />
        <div className="hidden text-right md:block">
          <div className="text-sm font-semibold" style={{ color: 'var(--text-color)' }}>
            {user?.role || 'User'}
          </div>
          <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            {user?.email || ''}
          </div>
        </div>
      </div>
    </header>
  );
}

export default Topbar;
