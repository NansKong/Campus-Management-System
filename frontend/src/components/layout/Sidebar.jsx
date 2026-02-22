import React from 'react';
import { ChevronLeft, ChevronRight, LogOut } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function Sidebar({ collapsed, onToggle }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const navigationByRole = {
    student: [
      { path: '/dashboard', icon: 'DB', label: 'Dashboard' },
      { path: '/attendance', icon: 'AT', label: 'My Attendance' },
      { path: '/food', icon: 'FD', label: 'Food Orders' },
      { path: '/remedial', icon: 'RM', label: 'Remedial' },
      { path: '/resources', icon: 'RS', label: 'Resources' },
      { path: '/profile', icon: 'PF', label: 'Profile' },
    ],
    faculty: [
      { path: '/dashboard', icon: 'DB', label: 'Dashboard' },
      { path: '/attendance', icon: 'AT', label: 'Attendance' },
      { path: '/remedial', icon: 'RM', label: 'Remedial' },
      { path: '/students', icon: 'ST', label: 'Students' },
      { path: '/resources', icon: 'RS', label: 'Resources' },
      { path: '/profile', icon: 'PF', label: 'Profile' },
    ],
    vendor: [
      { path: '/dashboard', icon: 'DB', label: 'Dashboard' },
      { path: '/food', icon: 'FD', label: 'Order Panel' },
      { path: '/food-analytics', icon: 'AN', label: 'Analytics' },
      { path: '/profile', icon: 'PF', label: 'Profile' },
    ],
    admin: [
      { path: '/dashboard', icon: 'DB', label: 'Dashboard' },
      { path: '/attendance', icon: 'AT', label: 'Attendance' },
      { path: '/food', icon: 'FD', label: 'Food Ops' },
      { path: '/food-analytics', icon: 'AN', label: 'Analytics' },
      { path: '/remedial', icon: 'RM', label: 'Remedial' },
      { path: '/students', icon: 'ST', label: 'Users' },
      { path: '/resources', icon: 'RS', label: 'Resources' },
      { path: '/profile', icon: 'PF', label: 'Profile' },
    ],
  };

  const filteredItems = navigationByRole[user?.role] || [];

  const sidebarWidth = collapsed ? 80 : 256;

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <aside
      className="fixed left-0 top-0 z-40 flex h-screen flex-col border-r shadow-lg transition-all duration-300"
      style={{ width: `${sidebarWidth}px`, background: 'var(--card-bg)', borderColor: 'var(--border-color)' }}
    >
      <div className="flex items-center justify-between border-b px-3 py-3" style={{ borderColor: 'var(--border-color)' }}>
        <button
          type="button"
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 rounded-md px-2 py-1 text-sm font-semibold"
          style={{ color: 'var(--text-color)' }}
          title="Go to dashboard"
        >
          <span className="rounded bg-red-500 px-2 py-1 text-xs text-white">SC</span>
          {!collapsed && <span>Smart Campus</span>}
        </button>
        <button
          type="button"
          onClick={onToggle}
          className="rounded-md border p-1.5"
          style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg-pink)' }}
          aria-label="Toggle sidebar"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      <nav className="flex flex-1 flex-col gap-2 p-3">
        {filteredItems.map((item) => {
          const isActive = location.pathname === item.path;

          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`flex h-10 items-center rounded-lg px-3 text-sm font-medium transition ${
                isActive ? 'text-white' : ''
              }`}
              style={
                isActive
                  ? { background: 'linear-gradient(135deg, #f87171 0%, #ef4444 100%)' }
                  : { color: 'var(--text-color)', background: 'transparent' }
              }
              title={item.label}
            >
              <span className="w-8 text-left text-xs font-bold">{item.icon}</span>
              {!collapsed && <span className="truncate">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="border-t p-3" style={{ borderColor: 'var(--border-color)' }}>
        <button
          type="button"
          onClick={handleLogout}
          className="flex h-10 w-full items-center rounded-lg px-3 text-sm font-medium transition hover:bg-red-100"
          style={{ color: 'var(--text-color)' }}
          title="Logout"
        >
          <LogOut size={16} />
          {!collapsed && <span className="ml-2">Logout</span>}
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
