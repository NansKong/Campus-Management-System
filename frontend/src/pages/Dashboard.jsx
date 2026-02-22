import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const roleNames = {
  student: 'Student',
  faculty: 'Faculty',
  vendor: 'Vendor',
  admin: 'Admin',
};

const roleDashboardConfig = {
  student: {
    title: 'Student Workspace',
    subtitle: 'Track attendance, classes, food orders, and remedial tasks from one place.',
    metrics: [
      { label: 'My Attendance %', value: '82.4%', tone: 'primary' },
      { label: "Today's Classes", value: '4', tone: 'neutral' },
      { label: 'My Food Orders (Today)', value: '2', tone: 'neutral' },
      { label: 'Pending Remedial / Makeup', value: '1', tone: 'warning' },
      { label: 'Personal Notifications', value: '3', tone: 'warning' },
    ],
    quickActions: [
      { label: 'View Attendance', path: '/attendance' },
      { label: 'Order Food', path: '/food' },
      { label: 'Remedial Classes', path: '/remedial' },
      { label: 'Book Resources', path: '/resources' },
    ],
    feedTitle: 'Upcoming Exams / Events',
    feed: [
      { title: 'Database Midterm', body: 'Monday, 10:00 AM - Block AB1, Room 203' },
      { title: 'Attendance Alert', body: 'Operating Systems attendance is at 74%. Take remedial support.' },
      { title: 'Food Pickup', body: 'Order #A9F2 is ready for pickup at North Canteen.' },
    ],
    sideTitle: 'Personal Notifications',
    side: [
      'Remedial request approved for DBMS.',
      'Library room booking confirmed for 4:00 PM.',
      'Exam timetable revised for Semester 5.',
    ],
  },
  faculty: {
    title: 'Faculty Operations',
    subtitle: 'Monitor class health, attendance actions, and remedial demand.',
    metrics: [
      { label: 'Total Students', value: '178', tone: 'primary' },
      { label: 'Present Today', value: '151', tone: 'success' },
      { label: 'Absent Today', value: '19', tone: 'warning' },
      { label: 'Late Arrivals', value: '8', tone: 'warning' },
      { label: 'Classes Scheduled Today', value: '5', tone: 'neutral' },
      { label: 'Pending Remedial Requests', value: '4', tone: 'warning' },
      { label: 'AI Attendance Accuracy %', value: '92.6%', tone: 'success' },
      { label: 'Proxy Detection Alerts', value: '2', tone: 'warning' },
    ],
    quickActions: [
      { label: 'Mark Attendance', path: '/attendance' },
      { label: 'Manage Remedial', path: '/remedial' },
      { label: 'Student Management', path: '/students' },
      { label: 'Resource Availability', path: '/resources' },
    ],
    feedTitle: 'Attendance Trend Graph (Recent)',
    feed: [
      { title: 'Mon', body: 'Present Rate: 84%' },
      { title: 'Tue', body: 'Present Rate: 82%' },
      { title: 'Wed', body: 'Present Rate: 79%' },
    ],
    sideTitle: 'Risk Students List',
    side: [
      'REG1021 - Attendance 71% (High Risk)',
      'REG1094 - Attendance 69% (High Risk)',
      'REG1128 - Attendance 73% (Moderate Risk)',
    ],
  },
  vendor: {
    title: 'Vendor Control Panel',
    subtitle: 'Handle incoming orders, status updates, and daily performance.',
    metrics: [
      { label: "Today's Orders", value: '58', tone: 'primary' },
      { label: 'Total Orders Today', value: '58', tone: 'neutral' },
      { label: 'Revenue Today', value: 'INR 12,450', tone: 'success' },
      { label: 'Pending Orders', value: '11', tone: 'warning' },
      { label: 'Completed Orders', value: '39', tone: 'success' },
      { label: 'Predicted Next 1 Hour Demand', value: '46', tone: 'warning' },
      { label: 'Expected Peak Window', value: '13:00-13:30', tone: 'neutral' },
      { label: 'Suggested Prep Quantity', value: '52', tone: 'primary' },
    ],
    quickActions: [
      { label: 'Manage Orders', path: '/food' },
      { label: 'Update Menu', path: '/food' },
      { label: 'Food Analytics', path: '/food-analytics' },
      { label: 'Profile', path: '/profile' },
    ],
    feedTitle: 'Order Queue Highlights',
    feed: [
      { title: 'Rush Window', body: 'Peak demand expected 1:00 PM - 1:30 PM.' },
      { title: 'Top Item', body: 'Veg Roll has 16 active orders.' },
      { title: 'Preparation Alert', body: '5 orders pending in "Preparing" for over 10 minutes.' },
    ],
    sideTitle: 'Operational Notes',
    side: [
      'Update unavailable items before noon rush.',
      'Export daily sales report before logout.',
      'Payment reconciliation pending for 2 orders.',
    ],
  },
  admin: {
    title: 'Admin Command Center',
    subtitle: 'System-wide monitoring for users, operations, and service quality.',
    metrics: [
      { label: 'Total Students', value: '1,248', tone: 'primary' },
      { label: 'Total Faculty', value: '87', tone: 'neutral' },
      { label: 'Total Vendors', value: '14', tone: 'neutral' },
      { label: 'Attendance Average', value: '81.7%', tone: 'success' },
      { label: 'Food Revenue Overview', value: 'INR 2.41L', tone: 'success' },
      { label: 'Resource Utilization %', value: '68.5%', tone: 'warning' },
    ],
    quickActions: [
      { label: 'User Management', path: '/students' },
      { label: 'Attendance Monitoring', path: '/attendance' },
      { label: 'Vendor Analytics', path: '/food-analytics' },
      { label: 'Resource Configuration', path: '/resources' },
    ],
    feedTitle: 'System Activity Logs',
    feed: [
      { title: 'New Vendor Request', body: 'Vendor onboarding request submitted by GreenBite Foods.' },
      { title: 'Policy Trigger', body: '14 students crossed low-attendance threshold in CSE department.' },
      { title: 'Resource Spike', body: 'Lab Block utilization crossed 90% in last 24 hours.' },
    ],
    sideTitle: 'Admin Notifications',
    side: [
      '2 faculty accounts pending approval.',
      'Food payment reconciliation mismatch detected.',
      'Attendance threshold updated to 75%.',
    ],
  },
};

function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const role = user?.role || 'student';
  const config = roleDashboardConfig[role] || roleDashboardConfig.student;

  const dateLabel = useMemo(
    () =>
      now.toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      }),
    [now]
  );

  const timeLabel = useMemo(
    () =>
      now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      }),
    [now]
  );

  return (
    <div className="space-y-6">
      <section
        className="rounded-xl border p-5"
        style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg)' }}
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold" style={{ color: 'var(--text-color)' }}>
              {config.title}
            </h2>
            <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
              {config.subtitle}
            </p>
            <p className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
              {dateLabel} | {timeLabel}
            </p>
          </div>
          <div
            className="rounded-full border px-3 py-1 text-xs font-semibold uppercase"
            style={{ borderColor: 'var(--border-color)', color: 'var(--text-color)' }}
          >
            {roleNames[role] || 'User'}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {config.metrics.map((metric) => (
          <MetricCard key={metric.label} metric={metric} />
        ))}
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div
          className="rounded-xl border p-5 xl:col-span-1"
          style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg)' }}
        >
          <h3 className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
            Quick Actions
          </h3>
          <div className="mt-4 grid grid-cols-1 gap-3">
            {config.quickActions.map((action) => (
              <button
                key={action.label}
                type="button"
                onClick={() => navigate(action.path)}
                className="rounded-lg border px-4 py-3 text-left text-sm font-semibold transition hover:opacity-90"
                style={{
                  borderColor: 'var(--border-color)',
                  background: 'var(--card-bg-pink)',
                  color: 'var(--text-color)',
                }}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>

        <div
          className="rounded-xl border p-5 xl:col-span-2"
          style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg)' }}
        >
          <h3 className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
            {config.feedTitle}
          </h3>
          <ul className="mt-4 space-y-3">
            {config.feed.map((entry) => (
              <li
                key={entry.title}
                className="rounded-lg border p-3"
                style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg-pink)' }}
              >
                <p className="text-sm font-semibold" style={{ color: 'var(--text-color)' }}>
                  {entry.title}
                </p>
                <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
                  {entry.body}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section
        className="rounded-xl border p-5"
        style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg)' }}
      >
        <h3 className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
          {config.sideTitle}
        </h3>
        <ul className="mt-3 space-y-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          {config.side.map((note) => (
            <li key={note} className="rounded-md border px-3 py-2" style={{ borderColor: 'var(--border-color)' }}>
              {note}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function MetricCard({ metric }) {
  let accent = 'var(--text-color)';
  if (metric.tone === 'success') accent = '#166534';
  if (metric.tone === 'warning') accent = '#b45309';
  if (metric.tone === 'primary') accent = '#c2410c';

  return (
    <div
      className="rounded-xl border p-5"
      style={{ borderColor: 'var(--border-color)', background: 'var(--card-bg)' }}
    >
      <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
        {metric.label}
      </p>
      <p className="mt-2 text-2xl font-bold" style={{ color: accent }}>
        {metric.value}
      </p>
    </div>
  );
}

export default Dashboard;
