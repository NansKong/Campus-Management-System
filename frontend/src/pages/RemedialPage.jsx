import React, { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import attendanceService from '../services/attendanceService';
import remedialService from '../services/remedialService';
import { getApiErrorMessage } from '../utils/errors';

const initialCreateForm = {
  section_id: '',
  classroom_id: '',
  scheduled_date: '',
  start_time: '',
  end_time: '',
  reason: '',
};

function RemedialPage() {
  const { user } = useAuth();
  const role = user?.role;

  if (role === 'student') {
    return <StudentRemedial />;
  }

  if (role === 'faculty' || role === 'admin') {
    return <ManagementRemedial role={role} />;
  }

  return <div className="p-6">You are not authorized to access remedial workflows.</div>;
}

function ManagementRemedial({ role }) {
  const canCreate = role === 'faculty';
  const [classes, setClasses] = useState([]);
  const [sections, setSections] = useState([]);
  const [classrooms, setClassrooms] = useState([]);
  const [createForm, setCreateForm] = useState(initialCreateForm);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });

  const loadClasses = useCallback(async () => {
    setLoading(true);
    try {
      const tasks = [remedialService.listClasses()];
      if (canCreate) {
        tasks.push(attendanceService.getMySections(), attendanceService.getAvailableClassrooms());
      }
      const results = await Promise.all(tasks);
      const data = results[0];
      setClasses(data);
      if (canCreate) {
        setSections(results[1] || []);
        setClassrooms(results[2] || []);
      }
      setStatus({ type: '', message: '' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to fetch remedial classes'),
      });
    } finally {
      setLoading(false);
    }
  }, [canCreate]);

  useEffect(() => {
    loadClasses();
  }, [loadClasses]);

  const handleCreateChange = (key, value) => {
    setCreateForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    if (!canCreate) return;

    setSubmitting(true);
    try {
      await remedialService.createClass(createForm);
      setCreateForm(initialCreateForm);
      setStatus({ type: 'success', message: 'Remedial class created successfully.' });
      await loadClasses();
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to create remedial class'),
      });
    } finally {
      setSubmitting(false);
    }
  };

  const beginEdit = (remedialClass) => {
    setEditingId(remedialClass.remedial_id);
    setEditForm({
      scheduled_date: remedialClass.scheduled_date || '',
      start_time: remedialClass.start_time || '',
      end_time: remedialClass.end_time || '',
      reason: remedialClass.reason || '',
      is_active: remedialClass.is_active,
    });
  };

  const handleEditChange = (key, value) => {
    setEditForm((prev) => ({ ...prev, [key]: value }));
  };

  const normalizeUpdatePayload = () => {
    const payload = {};
    Object.entries(editForm).forEach(([key, value]) => {
      if (value === '' || value === null || typeof value === 'undefined') return;
      payload[key] = value;
    });
    return payload;
  };

  const handleUpdate = async (remedialId) => {
    const payload = normalizeUpdatePayload();
    if (Object.keys(payload).length === 0) {
      setStatus({ type: 'error', message: 'No update fields provided.' });
      return;
    }

    setSubmitting(true);
    try {
      await remedialService.updateClass(remedialId, payload);
      setEditingId(null);
      setEditForm({});
      setStatus({ type: 'success', message: 'Remedial class updated successfully.' });
      await loadClasses();
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to update remedial class'),
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h1 className="text-2xl font-semibold">Remedial Management</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage remedial class schedules and active status.
        </p>

        {!canCreate && (
          <p className="mt-3 rounded-md bg-blue-50 px-3 py-2 text-sm text-blue-700">
            Admin users can review and update classes. Only faculty can create new classes.
          </p>
        )}

        {status.message && (
          <div
            className={`mt-4 rounded-md px-4 py-2 text-sm ${
              status.type === 'error'
                ? 'bg-red-50 text-red-700'
                : 'bg-green-50 text-green-700'
            }`}
          >
            {status.message}
          </div>
        )}
      </div>

      {canCreate && (
        <form className="rounded-xl border border-gray-200 bg-white p-6" onSubmit={handleCreate}>
          <h2 className="text-lg font-semibold">Schedule Remedial Class</h2>
          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
            <select
              className="rounded-md border px-3 py-2"
              value={createForm.section_id}
              onChange={(event) => handleCreateChange('section_id', event.target.value)}
              required
            >
              <option value="">Select section</option>
              {sections.map((section) => (
                <option key={section.section_id} value={section.section_id}>
                  {section.course_code || 'COURSE'} - {section.section_name}
                </option>
              ))}
            </select>
            <select
              className="rounded-md border px-3 py-2"
              value={createForm.classroom_id}
              onChange={(event) => handleCreateChange('classroom_id', event.target.value)}
              required
            >
              <option value="">Select classroom</option>
              {classrooms.map((classroom) => (
                <option key={classroom.classroom_id} value={classroom.classroom_id}>
                  {(classroom.block_code || 'BLK') + '-' + classroom.room_number}
                </option>
              ))}
            </select>
            <input
              type="date"
              className="rounded-md border px-3 py-2"
              value={createForm.scheduled_date}
              onChange={(event) => handleCreateChange('scheduled_date', event.target.value)}
              required
            />
            <input
              type="time"
              className="rounded-md border px-3 py-2"
              value={createForm.start_time}
              onChange={(event) => handleCreateChange('start_time', event.target.value)}
              required
            />
            <input
              type="time"
              className="rounded-md border px-3 py-2"
              value={createForm.end_time}
              onChange={(event) => handleCreateChange('end_time', event.target.value)}
              required
            />
            <input
              className="rounded-md border px-3 py-2"
              placeholder="Reason"
              value={createForm.reason}
              onChange={(event) => handleCreateChange('reason', event.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:bg-blue-300"
          >
            {submitting ? 'Saving...' : 'Create Remedial Class'}
          </button>
        </form>
      )}

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="text-lg font-semibold">Scheduled Classes</h2>
        {loading ? (
          <p className="mt-3 text-sm text-gray-600">Loading classes...</p>
        ) : classes.length === 0 ? (
          <p className="mt-3 text-sm text-gray-600">No remedial classes found.</p>
        ) : (
          <div className="mt-4 space-y-3">
            {classes.map((remedialClass) => (
              <div key={remedialClass.remedial_id} className="rounded-lg border border-gray-200 p-4">
                <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-medium">
                      Code: <span className="font-mono">{remedialClass.remedial_code}</span>
                    </p>
                    <p className="text-sm text-gray-600">
                      Date {remedialClass.scheduled_date} | Time {remedialClass.start_time} -{' '}
                      {remedialClass.end_time}
                    </p>
                    <p className="text-sm text-gray-600">
                      Section {remedialClass.section_id} | Classroom {remedialClass.classroom_id}
                    </p>
                    {remedialClass.reason && (
                      <p className="text-sm text-gray-600">Reason: {remedialClass.reason}</p>
                    )}
                    <p className="text-sm text-gray-600">
                      Status: {remedialClass.is_active ? 'Active' : 'Inactive'}
                    </p>
                  </div>

                  {editingId === remedialClass.remedial_id ? (
                    <div className="space-y-2">
                      <input
                        type="date"
                        className="w-full rounded-md border px-2 py-1 text-sm"
                        value={editForm.scheduled_date || ''}
                        onChange={(event) => handleEditChange('scheduled_date', event.target.value)}
                      />
                      <div className="flex gap-2">
                        <input
                          type="time"
                          className="w-full rounded-md border px-2 py-1 text-sm"
                          value={editForm.start_time || ''}
                          onChange={(event) => handleEditChange('start_time', event.target.value)}
                        />
                        <input
                          type="time"
                          className="w-full rounded-md border px-2 py-1 text-sm"
                          value={editForm.end_time || ''}
                          onChange={(event) => handleEditChange('end_time', event.target.value)}
                        />
                      </div>
                      <input
                        className="w-full rounded-md border px-2 py-1 text-sm"
                        placeholder="Reason"
                        value={editForm.reason || ''}
                        onChange={(event) => handleEditChange('reason', event.target.value)}
                      />
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={Boolean(editForm.is_active)}
                          onChange={(event) => handleEditChange('is_active', event.target.checked)}
                        />
                        Active
                      </label>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          className="rounded bg-blue-600 px-3 py-1 text-sm text-white"
                          onClick={() => handleUpdate(remedialClass.remedial_id)}
                          disabled={submitting}
                        >
                          Save
                        </button>
                        <button
                          type="button"
                          className="rounded border px-3 py-1 text-sm"
                          onClick={() => {
                            setEditingId(null);
                            setEditForm({});
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      type="button"
                      className="rounded border px-3 py-1 text-sm"
                      onClick={() => beginEdit(remedialClass)}
                    >
                      Edit
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StudentRemedial() {
  const [remedialCode, setRemedialCode] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });

  const loadHistory = async () => {
    try {
      const data = await remedialService.getMyAttendanceHistory();
      setHistory(data);
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to load remedial attendance history'),
      });
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleMarkAttendance = async () => {
    if (!remedialCode.trim()) {
      setStatus({ type: 'error', message: 'Remedial code is required.' });
      return;
    }

    setLoading(true);
    try {
      await remedialService.markAttendance(remedialCode.trim().toUpperCase());
      await loadHistory();
      setRemedialCode('');
      setStatus({ type: 'success', message: 'Attendance marked successfully.' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to mark attendance'),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h1 className="text-2xl font-semibold">Remedial Attendance</h1>
        <p className="mt-1 text-sm text-gray-600">
          Enter the remedial code provided by faculty.
        </p>

        {status.message && (
          <div
            className={`mt-4 rounded-md px-4 py-2 text-sm ${
              status.type === 'error'
                ? 'bg-red-50 text-red-700'
                : 'bg-green-50 text-green-700'
            }`}
          >
            {status.message}
          </div>
        )}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <div className="flex flex-col gap-3 md:flex-row">
          <input
            className="w-full rounded-md border px-3 py-2 md:w-96"
            placeholder="Enter remedial code"
            value={remedialCode}
            onChange={(event) => setRemedialCode(event.target.value)}
            maxLength={10}
          />
          <button
            type="button"
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:bg-blue-300"
            disabled={loading}
            onClick={handleMarkAttendance}
          >
            {loading ? 'Submitting...' : 'Mark Attendance'}
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="text-lg font-semibold">Recent Local Activity</h2>
        {history.length === 0 ? (
          <p className="mt-3 text-sm text-gray-600">No attendance submissions yet.</p>
        ) : (
          <ul className="mt-3 space-y-2 text-sm">
            {history.map((entry, index) => (
              <li key={`${entry.remedial_attendance_id}-${index}`} className="rounded-md border border-gray-200 px-3 py-2">
                Remedial {String(entry.remedial_id).slice(0, 8)} | Code {entry.code_used || '-'} |
                Submitted {new Date(entry.marked_at).toLocaleString()}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default RemedialPage;
