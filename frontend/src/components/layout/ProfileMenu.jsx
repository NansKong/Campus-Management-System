import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useNavigate } from 'react-router-dom';

function ProfileMenu() {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();

  return (
    <div className="space-y-3">
      <div className="text-sm">
        <p className="font-semibold">{user?.email}</p>
        <p className="opacity-60">{user?.role}</p>
      </div>

      <select
        value={theme}
        onChange={(e) => setTheme(e.target.value)}
        className="w-full px-2 py-1 rounded bg-[var(--bg-color)] border border-[var(--border-color)]"
      >
        <option value="light">🌞 Light</option>
        <option value="dark">🌙 Dark</option>
        <option value="system">🖥 System</option>
      </select>

      <button
        onClick={() => navigate('/profile')}
        className="w-full text-left text-sm hover:underline"
      >
        View Profile
      </button>

      <button
        onClick={logout}
        className="w-full text-left text-sm text-red-500 hover:underline"
      >
        Logout
      </button>
    </div>
  );
}

export default ProfileMenu;