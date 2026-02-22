import React from 'react';
import Sidebar from './Sidebar';
import ThemeToggle from '../ui/ThemeToggle';
import { useAuth } from '../../context/AuthContext';

function PageLayout({ children, title, icon }) {
    const { user } = useAuth();

    return (
        <div className="flex min-h-screen" style={{ background: 'linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%)' }}>
            <Sidebar />

            <div className="flex-1 ml-16">
                {/* Header */}
                <header className="px-8 py-4 flex justify-between items-center" style={{ background: 'var(--card-bg)' }}>
                    <div className="flex items-center gap-2">
                        {icon && <span className="text-2xl">{icon}</span>}
                        <h1 className="text-xl font-bold" style={{ color: 'var(--text-color)' }}>{title}</h1>
                    </div>

                    <div className="flex items-center gap-4">
                        <ThemeToggle />
                        <div className="text-right">
                            <div className="text-sm font-semibold" style={{ color: 'var(--text-color)' }}>{user?.role}</div>
                            <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{user?.email}</div>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-400 to-red-500 flex items-center justify-center text-white font-bold">
                            {user?.email?.[0].toUpperCase()}
                        </div>
                    </div>
                </header>

                {/* Main Content */}
                <div className="p-8">
                    {children}
                </div>
            </div>
        </div>
    );
}

export default PageLayout;
