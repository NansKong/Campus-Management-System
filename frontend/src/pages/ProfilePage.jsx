import React from 'react';
import { useAuth } from '../context/AuthContext';

function ProfilePage() {
  const { user } = useAuth();

  return (
    <div className="max-w-xl mx-auto bg-[var(--card-bg)] p-6 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">👤 Profile</h2>

      <div className="space-y-3">
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Role:</strong> {user.role}</p>
      </div>
    </div>
  );
}

export default ProfilePage;
