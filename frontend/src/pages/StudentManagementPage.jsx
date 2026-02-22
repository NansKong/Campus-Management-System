import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import aiService from '../services/aiService';
import studentService from '../services/studentService';
import { getApiErrorMessage } from '../utils/errors';

const initialCreateState = {
  registration_number: '',
  first_name: '',
  last_name: '',
  email: '',
  firebase_uid: '',
  enrollment_year: new Date().getFullYear(),
  section: '',
  semester: '',
  phone: '',
  parent_email: '',
  parent_phone: '',
  program: '',
};

const initialFilters = {
  search: '',
  section: '',
  semester: '',
};

function StudentManagementPage() {
  const { user } = useAuth();
  const role = user?.role;
  const canManage = role === 'admin' || role === 'faculty';

  const [students, setStudents] = useState([]);
  const [filters, setFilters] = useState(initialFilters);
  const [createForm, setCreateForm] = useState(initialCreateState);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [pendingEnrollments, setPendingEnrollments] = useState([]);

  const queryParams = useMemo(() => {
    const params = {};
    if (filters.search.trim()) params.search = filters.search.trim();
    if (filters.section.trim()) params.section = filters.section.trim();
    if (filters.semester) params.semester = Number(filters.semester);
    return params;
  }, [filters]);

  const loadStudents = useCallback(async () => {
    if (!canManage) return;

    setLoading(true);
    try {
      const data = await studentService.listStudents(queryParams);
      setStudents(data);
      if (role === 'admin') {
        try {
          const pending = await aiService.getPendingEnrollments();
          setPendingEnrollments(pending);
        } catch (enrollmentError) {
          console.warn('Pending face enrollments unavailable:', enrollmentError);
        }
      }
      setStatus({ type: '', message: '' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to fetch students'),
      });
    } finally {
      setLoading(false);
    }
  }, [canManage, queryParams, role]);

  useEffect(() => {
    loadStudents();
  }, [loadStudents]);

  if (!canManage) {
    return <div className="p-6">You are not authorized to access student management.</div>;
  }

  const onCreateChange = (key, value) => {
    setCreateForm((prev) => ({ ...prev, [key]: value }));
  };

  const onEditChange = (key, value) => {
    setEditForm((prev) => ({ ...prev, [key]: value }));
  };

  const normalizeCreatePayload = () => ({
    ...createForm,
    enrollment_year: Number(createForm.enrollment_year),
    semester: createForm.semester ? Number(createForm.semester) : null,
    section: createForm.section || null,
    phone: createForm.phone || null,
    parent_email: createForm.parent_email || null,
    parent_phone: createForm.parent_phone || null,
    program: createForm.program || null,
    firebase_uid: createForm.firebase_uid || null,
  });

  const normalizeEditPayload = () => {
    const payload = {};
    Object.entries(editForm).forEach(([key, value]) => {
      if (value === '' || value === null || typeof value === 'undefined') return;
      payload[key] = value;
    });
    if (payload.semester) payload.semester = Number(payload.semester);
    if (payload.enrollment_year) payload.enrollment_year = Number(payload.enrollment_year);
    return payload;
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await studentService.createStudent(normalizeCreatePayload());
      setCreateForm(initialCreateState);
      setStatus({ type: 'success', message: 'Student created successfully.' });
      await loadStudents();
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to create student'),
      });
    } finally {
      setSubmitting(false);
    }
  };

  const beginEdit = (student) => {
    setEditingId(student.student_id);
    setEditForm({
      first_name: student.first_name || '',
      last_name: student.last_name || '',
      email: student.email || '',
      section: student.section || '',
      semester: student.semester || '',
      enrollment_year: student.enrollment_year || '',
      phone: student.phone || '',
      parent_email: student.parent_email || '',
      parent_phone: student.parent_phone || '',
      program: student.program || '',
    });
  };

  const handleUpdate = async (studentId) => {
    const payload = normalizeEditPayload();
    if (Object.keys(payload).length === 0) {
      setStatus({ type: 'error', message: 'No update fields provided.' });
      return;
    }

    setSubmitting(true);
    try {
      await studentService.updateStudent(studentId, payload);
      setEditingId(null);
      setEditForm({});
      setStatus({ type: 'success', message: 'Student updated successfully.' });
      await loadStudents();
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to update student'),
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleEnrollmentReview = async (studentId, action) => {
    try {
      await aiService.reviewEnrollment(studentId, action);
      setStatus({
        type: 'success',
        message: `Enrollment ${action === 'approve' ? 'approved' : 'rejected'} successfully.`,
      });
      await loadStudents();
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to review enrollment'),
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h1 className="text-2xl font-semibold">Student Management</h1>
        <p className="mt-1 text-sm text-gray-600">
          Create, search, and update student records.
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

      <form className="rounded-xl border border-gray-200 bg-white p-6" onSubmit={handleCreate}>
        <h2 className="text-lg font-semibold">Create Student</h2>
        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Registration number"
            value={createForm.registration_number}
            onChange={(event) => onCreateChange('registration_number', event.target.value)}
            required
          />
          <input
            className="rounded-md border px-3 py-2"
            placeholder="First name"
            value={createForm.first_name}
            onChange={(event) => onCreateChange('first_name', event.target.value)}
            required
          />
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Last name"
            value={createForm.last_name}
            onChange={(event) => onCreateChange('last_name', event.target.value)}
            required
          />
          <input
            type="email"
            className="rounded-md border px-3 py-2"
            placeholder="Email"
            value={createForm.email}
            onChange={(event) => onCreateChange('email', event.target.value)}
            required
          />
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Firebase UID (optional)"
            value={createForm.firebase_uid}
            onChange={(event) => onCreateChange('firebase_uid', event.target.value)}
          />
          <input
            type="number"
            className="rounded-md border px-3 py-2"
            placeholder="Enrollment year"
            value={createForm.enrollment_year}
            onChange={(event) => onCreateChange('enrollment_year', event.target.value)}
            required
          />
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Section"
            value={createForm.section}
            onChange={(event) => onCreateChange('section', event.target.value)}
          />
          <input
            type="number"
            min="1"
            max="12"
            className="rounded-md border px-3 py-2"
            placeholder="Semester"
            value={createForm.semester}
            onChange={(event) => onCreateChange('semester', event.target.value)}
          />
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Program"
            value={createForm.program}
            onChange={(event) => onCreateChange('program', event.target.value)}
          />
        </div>

        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Student phone"
            value={createForm.phone}
            onChange={(event) => onCreateChange('phone', event.target.value)}
          />
          <input
            type="email"
            className="rounded-md border px-3 py-2"
            placeholder="Parent email"
            value={createForm.parent_email}
            onChange={(event) => onCreateChange('parent_email', event.target.value)}
          />
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Parent phone"
            value={createForm.parent_phone}
            onChange={(event) => onCreateChange('parent_phone', event.target.value)}
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:bg-blue-300"
        >
          {submitting ? 'Saving...' : 'Create Student'}
        </button>
      </form>

      {role === 'admin' && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold">Face Enrollment Approvals</h2>
          {pendingEnrollments.length === 0 ? (
            <p className="mt-3 text-sm text-gray-600">No pending enrollments.</p>
          ) : (
            <div className="mt-4 space-y-2">
              {pendingEnrollments.map((entry) => (
                <div
                  key={entry.student_id}
                  className="flex flex-col gap-2 rounded-md border border-gray-200 p-3 md:flex-row md:items-center md:justify-between"
                >
                  <div className="text-sm">
                    <p className="font-medium">
                      {entry.student_name} ({entry.registration_number})
                    </p>
                    <p className="text-gray-600">
                      Samples: {entry.sample_count} | Model: {entry.model_name}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      className="rounded bg-emerald-600 px-3 py-1 text-sm text-white"
                      onClick={() => handleEnrollmentReview(entry.student_id, 'approve')}
                    >
                      Approve
                    </button>
                    <button
                      type="button"
                      className="rounded border border-red-300 px-3 py-1 text-sm text-red-700"
                      onClick={() => handleEnrollmentReview(entry.student_id, 'reject')}
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <div className="mb-4 flex flex-col gap-3 md:flex-row">
          <input
            className="rounded-md border px-3 py-2 md:w-96"
            placeholder="Search by name, registration number, or email"
            value={filters.search}
            onChange={(event) => setFilters((prev) => ({ ...prev, search: event.target.value }))}
          />
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Section"
            value={filters.section}
            onChange={(event) => setFilters((prev) => ({ ...prev, section: event.target.value }))}
          />
          <input
            type="number"
            min="1"
            max="12"
            className="rounded-md border px-3 py-2"
            placeholder="Semester"
            value={filters.semester}
            onChange={(event) => setFilters((prev) => ({ ...prev, semester: event.target.value }))}
          />
        </div>

        {loading ? (
          <p className="text-sm text-gray-600">Loading students...</p>
        ) : students.length === 0 ? (
          <p className="text-sm text-gray-600">No students found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead>
                <tr className="text-left">
                  <th className="px-3 py-2">Registration</th>
                  <th className="px-3 py-2">Name</th>
                  <th className="px-3 py-2">Email</th>
                  <th className="px-3 py-2">Section</th>
                  <th className="px-3 py-2">Semester</th>
                  <th className="px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {students.map((student) => (
                  <tr key={student.student_id}>
                    <td className="px-3 py-2">{student.registration_number}</td>
                    <td className="px-3 py-2">
                      {student.first_name} {student.last_name}
                    </td>
                    <td className="px-3 py-2">{student.email}</td>
                    <td className="px-3 py-2">{student.section || '-'}</td>
                    <td className="px-3 py-2">{student.semester || '-'}</td>
                    <td className="px-3 py-2">
                      {editingId === student.student_id ? (
                        <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                          <input
                            className="rounded-md border px-2 py-1"
                            placeholder="First name"
                            value={editForm.first_name || ''}
                            onChange={(event) => onEditChange('first_name', event.target.value)}
                          />
                          <input
                            className="rounded-md border px-2 py-1"
                            placeholder="Last name"
                            value={editForm.last_name || ''}
                            onChange={(event) => onEditChange('last_name', event.target.value)}
                          />
                          <input
                            className="rounded-md border px-2 py-1"
                            placeholder="Email"
                            value={editForm.email || ''}
                            onChange={(event) => onEditChange('email', event.target.value)}
                          />
                          <input
                            className="rounded-md border px-2 py-1"
                            placeholder="Section"
                            value={editForm.section || ''}
                            onChange={(event) => onEditChange('section', event.target.value)}
                          />
                          <div className="col-span-full flex gap-2">
                            <button
                              type="button"
                              className="rounded bg-blue-600 px-3 py-1 text-white"
                              onClick={() => handleUpdate(student.student_id)}
                              disabled={submitting}
                            >
                              Save
                            </button>
                            <button
                              type="button"
                              className="rounded border px-3 py-1"
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
                          className="rounded border px-3 py-1"
                          onClick={() => beginEdit(student)}
                        >
                          Edit
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default StudentManagementPage;
