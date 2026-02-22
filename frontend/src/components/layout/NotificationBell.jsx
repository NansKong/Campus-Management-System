import { useEffect, useRef, useState } from 'react';
import { Bell } from 'lucide-react';

const notifications = [
  { id: 'attn', title: 'Attendance updated', detail: 'Attendance records were updated.' },
  { id: 'food', title: 'Food order ready', detail: 'A recent order is marked ready for pickup.' },
  { id: 'warn', title: 'Low attendance alert', detail: 'Some students dropped below attendance threshold.' },
];

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (rootRef.current && !rootRef.current.contains(event.target)) {
        setOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={rootRef}>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="relative rounded-lg border px-2 py-2 transition hover:opacity-90"
        style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg)' }}
        aria-label="Open notifications"
        title="Notifications"
      >
        <Bell size={18} style={{ color: 'var(--text-color)' }} />
        <span className="absolute -right-1 -top-1 rounded-full bg-red-500 px-1.5 text-[10px] text-white">
          {notifications.length}
        </span>
      </button>

      {open && (
        <div
          className="absolute right-0 z-50 mt-2 w-72 rounded-xl border p-3 shadow-lg"
          style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg)' }}
        >
          <p className="mb-2 text-sm font-semibold" style={{ color: 'var(--text-color)' }}>
            Notifications
          </p>
          <div className="space-y-2">
            {notifications.map((item) => (
              <div
                key={item.id}
                className="rounded-lg border p-2"
                style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg-pink)' }}
              >
                <p className="text-sm font-medium" style={{ color: 'var(--text-color)' }}>
                  {item.title}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  {item.detail}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
