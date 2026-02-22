import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const isDark = theme === 'dark';

  const toggleTheme = () => {
    setTheme(isDark ? 'light' : 'dark');
  };

  return (
    <button
      onClick={toggleTheme}
      className="relative h-7 w-14 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:ring-offset-2"
      style={{
        background: isDark
          ? 'linear-gradient(135deg, #4a2f5a 0%, #2d1b3d 100%)'
          : 'linear-gradient(135deg, #ffb8c1 0%, #ff6b7a 100%)',
      }}
      aria-label="Toggle theme"
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      <div
        className={`absolute left-1 top-1 flex h-5 w-5 transform items-center justify-center rounded-full bg-white shadow-md transition-all duration-300 ${
          isDark ? 'translate-x-7' : 'translate-x-0'
        }`}
      >
        {isDark ? <Moon size={12} className="text-slate-700" /> : <Sun size={12} className="text-orange-500" />}
      </div>
    </button>
  );
}

export default ThemeToggle;
