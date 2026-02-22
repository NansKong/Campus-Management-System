import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import attendanceService from '../services/attendanceService';
import aiService from '../services/aiService';
import { getApiErrorMessage } from '../utils/errors';

function AttendancePage() {
  const { user } = useAuth();

  if (user?.role === 'faculty') {
    return <FacultyAttendance />;
  }
  if (user?.role === 'student') {
    return <StudentAttendance />;
  }
  return <div className="p-8">You are not authorized to access attendance workflows.</div>;
}

function FacultyAttendance() {
  const [sections, setSections] = useState([]);
  const [classrooms, setClassrooms] = useState([]);
  const [selectedSection, setSelectedSection] = useState('');
  const [selectedClassroom, setSelectedClassroom] = useState('');
  const [sessionDate, setSessionDate] = useState(new Date().toISOString().slice(0, 10));
  const [sessionId, setSessionId] = useState('');
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [notificationResults, setNotificationResults] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [aiCaptureFile, setAiCaptureFile] = useState(null);
  const [aiCaptureResult, setAiCaptureResult] = useState(null);
  const [rtspUrl, setRtspUrl] = useState('');
  const [streamRuntime, setStreamRuntime] = useState(null);
  const [streamLoading, setStreamLoading] = useState(false);

  useEffect(() => {
    const loadSetup = async () => {
      setLoading(true);
      try {
        const [sectionData, classroomData] = await Promise.all([
          attendanceService.getMySections(),
          attendanceService.getAvailableClassrooms(),
        ]);
        setSections(sectionData);
        setClassrooms(classroomData);
        try {
          const insights = await aiService.getFacultyAttendanceInsights(75);
          setAiInsights(insights);
        } catch (error) {
          console.warn('AI insights unavailable:', error);
        }
      } catch (error) {
        setStatus({
          type: 'error',
          message: getApiErrorMessage(error, 'Failed to load attendance setup'),
        });
      } finally {
        setLoading(false);
      }
    };
    loadSetup();
  }, []);

  const startAttendanceSession = async () => {
    if (!selectedSection) {
      setStatus({ type: 'error', message: 'Select a section first.' });
      return;
    }

    setLoading(true);
    try {
      const session = await attendanceService.createSession({
        section_id: selectedSection,
        classroom_id: selectedClassroom || null,
        session_date: sessionDate,
      });
      const sectionStudents = await attendanceService.getSectionStudents(selectedSection);
      setSessionId(session.session_id);
      setStudents(sectionStudents.map((student) => ({ ...student, status: 'absent' })));
      setNotificationResults(null);
      setAiCaptureResult(null);
      setStatus({ type: 'success', message: 'Attendance session created.' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to create attendance session'),
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleAttendance = (studentId) => {
    setStudents((prev) =>
      prev.map((student) =>
        student.student_id === studentId
          ? { ...student, status: student.status === 'present' ? 'absent' : 'present' }
          : student
      )
    );
  };

  const markAll = (status) => {
    setStudents((prev) => prev.map((student) => ({ ...student, status })));
  };

  const submitAttendance = async () => {
    if (!sessionId) {
      setStatus({ type: 'error', message: 'No active session to submit.' });
      return;
    }
    if (!students.length) {
      setStatus({ type: 'error', message: 'No students found in this section.' });
      return;
    }

    setLoading(true);
    try {
      const result = await attendanceService.markAttendance(
        sessionId,
        students.map((student) => ({
          student_id: student.student_id,
          status: student.status,
        }))
      );
      setNotificationResults(result.notifications || null);
      setStatus({ type: 'success', message: result.message || 'Attendance submitted successfully.' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to submit attendance'),
      });
    } finally {
      setLoading(false);
    }
  };

  const runAiCapture = async () => {
    if (!sessionId) {
      setStatus({ type: 'error', message: 'Create or select a session first.' });
      return;
    }
    if (!aiCaptureFile) {
      setStatus({ type: 'error', message: 'Upload a class photo before AI capture.' });
      return;
    }

    setLoading(true);
    try {
      const result = await aiService.captureAttendancePhoto({
        sessionId,
        file: aiCaptureFile,
        confidenceThreshold: 0.75,
        lateThresholdMinutes: 10,
      });
      setAiCaptureResult(result);
      setStatus({ type: 'success', message: result.message || 'AI attendance capture completed.' });
      try {
        const insights = await aiService.getFacultyAttendanceInsights(75);
        setAiInsights(insights);
      } catch (insightError) {
        console.warn('Failed to refresh AI insights:', insightError);
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to run AI attendance capture'),
      });
    } finally {
      setLoading(false);
    }
  };

  const presentCount = useMemo(
    () => students.filter((student) => student.status === 'present').length,
    [students]
  );
  const absentCount = useMemo(
    () => students.filter((student) => student.status === 'absent').length,
    [students]
  );

  const resetSession = () => {
    setSessionId('');
    setStudents([]);
    setNotificationResults(null);
    setStreamRuntime(null);
    setStatus({ type: '', message: '' });
  };

  const startRtspStream = async () => {
    if (!sessionId) {
      setStatus({ type: 'error', message: 'Create an attendance session before starting RTSP stream.' });
      return;
    }
    if (!rtspUrl.trim()) {
      setStatus({ type: 'error', message: 'Provide RTSP URL/source before starting stream.' });
      return;
    }

    setStreamLoading(true);
    try {
      const stream = await aiService.startAttendanceStream({
        sessionId,
        sourceUrl: rtspUrl.trim(),
        confidenceThreshold: 0.75,
        lateThresholdMinutes: 10,
      });
      setStreamRuntime(stream);
      setStatus({ type: 'success', message: 'AI RTSP stream started.' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to start attendance stream'),
      });
    } finally {
      setStreamLoading(false);
    }
  };

  const stopRtspStream = async () => {
    if (!streamRuntime?.stream_id) return;
    setStreamLoading(true);
    try {
      const stream = await aiService.stopAttendanceStream(streamRuntime.stream_id);
      setStreamRuntime(stream);
      setStatus({ type: 'success', message: 'AI RTSP stream stopped.' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to stop attendance stream'),
      });
    } finally {
      setStreamLoading(false);
    }
  };

  useEffect(() => {
    if (!streamRuntime?.stream_id) return;
    if (!['starting', 'running', 'stopping'].includes(streamRuntime.status)) {
      if (streamRuntime.last_result) {
        setAiCaptureResult(streamRuntime.last_result);
      }
      return;
    }

    const timer = setInterval(async () => {
      try {
        const updated = await aiService.getAttendanceStreamStatus(streamRuntime.stream_id);
        setStreamRuntime(updated);
        if (updated.last_result) {
          setAiCaptureResult(updated.last_result);
        }
      } catch (error) {
        console.warn('Failed to refresh stream status:', error);
      }
    }, 3000);

    return () => clearInterval(timer);
  }, [streamRuntime]);

  return (
      <div className="space-y-6">
        {aiInsights && (
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="text-lg font-semibold">AI Attendance Insights</h2>
            <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-4 text-sm">
              <div className="rounded-md border border-gray-200 p-3">
                AI Accuracy: {aiInsights.ai_attendance_accuracy_percent || 0}%
              </div>
              <div className="rounded-md border border-gray-200 p-3">
                Proxy Alerts: {aiInsights.proxy_detection_alerts || 0}
              </div>
              <div className="rounded-md border border-gray-200 p-3">
                AI Sessions: {aiInsights.ai_sessions_count || 0}
              </div>
              <div className="rounded-md border border-gray-200 p-3">
                Risk Students: {aiInsights.risk_students?.length || 0}
              </div>
            </div>
          </div>
        )}

        {status.message && (
          <div
            className={`rounded-md px-4 py-2 text-sm ${
              status.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
            }`}
          >
            {status.message}
          </div>
        )}

        {!sessionId && (
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="text-lg font-semibold">Start Attendance Session</h2>
            <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
              <select
                value={selectedSection}
                onChange={(event) => setSelectedSection(event.target.value)}
                className="rounded-md border px-3 py-2"
              >
                <option value="">Select section</option>
                {sections.map((section) => (
                  <option key={section.section_id} value={section.section_id}>
                    {section.course_code || 'COURSE'} - {section.section_name}
                  </option>
                ))}
              </select>
              <select
                value={selectedClassroom}
                onChange={(event) => setSelectedClassroom(event.target.value)}
                className="rounded-md border px-3 py-2"
              >
                <option value="">Select classroom (optional)</option>
                {classrooms.map((classroom) => (
                  <option key={classroom.classroom_id} value={classroom.classroom_id}>
                    {(classroom.block_code || 'BLK') + '-' + classroom.room_number}
                  </option>
                ))}
              </select>
              <input
                type="date"
                className="rounded-md border px-3 py-2"
                value={sessionDate}
                onChange={(event) => setSessionDate(event.target.value)}
              />
            </div>
            <button
              type="button"
              className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm text-white disabled:bg-blue-300"
              onClick={startAttendanceSession}
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Start Session'}
            </button>
          </div>
        )}

        {sessionId && (
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <div className="mb-4 flex flex-wrap gap-2">
              <button type="button" className="rounded border px-3 py-1 text-sm" onClick={() => markAll('present')}>
                Mark All Present
              </button>
              <button type="button" className="rounded border px-3 py-1 text-sm" onClick={() => markAll('absent')}>
                Mark All Absent
              </button>
            </div>

            {students.length === 0 ? (
              <p className="text-sm text-gray-600">No enrolled students found for this section.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead>
                    <tr className="text-left">
                      <th className="px-3 py-2">Registration</th>
                      <th className="px-3 py-2">Name</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {students.map((student) => (
                      <tr key={student.student_id}>
                        <td className="px-3 py-2">{student.registration_number}</td>
                        <td className="px-3 py-2">
                          {student.first_name} {student.last_name}
                        </td>
                        <td className="px-3 py-2">
                          {student.status === 'present' ? 'Present' : 'Absent'}
                        </td>
                        <td className="px-3 py-2">
                          <button
                            type="button"
                            className="rounded border px-3 py-1 text-sm"
                            onClick={() => toggleAttendance(student.student_id)}
                          >
                            Toggle
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
              <div className="rounded-md border border-gray-200 p-3 text-sm">Total: {students.length}</div>
              <div className="rounded-md border border-gray-200 p-3 text-sm">Present: {presentCount}</div>
              <div className="rounded-md border border-gray-200 p-3 text-sm">Absent: {absentCount}</div>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white disabled:bg-blue-300"
                onClick={submitAttendance}
                disabled={loading || students.length === 0}
              >
                {loading ? 'Submitting...' : 'Submit Attendance'}
              </button>
              <button type="button" className="rounded border px-4 py-2 text-sm" onClick={resetSession}>
                Reset
              </button>
            </div>
          </div>
        )}

        {sessionId && (
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="text-lg font-semibold">RTSP Stream Capture (Phase 2)</h2>
            <p className="mt-1 text-sm text-gray-600">
              Start a live source stream for one-shot AI capture from classroom camera feed.
            </p>
            <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center">
              <input
                type="text"
                value={rtspUrl}
                onChange={(event) => setRtspUrl(event.target.value)}
                placeholder="rtsp://camera.local/stream1"
                className="w-full rounded-md border px-3 py-2 text-sm md:w-[420px]"
              />
              <button
                type="button"
                onClick={startRtspStream}
                disabled={streamLoading}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm text-white disabled:bg-indigo-300"
              >
                {streamLoading ? 'Starting...' : 'Start Stream'}
              </button>
              <button
                type="button"
                onClick={stopRtspStream}
                disabled={streamLoading || !streamRuntime?.stream_id}
                className="rounded border border-indigo-300 px-4 py-2 text-sm text-indigo-700 disabled:opacity-50"
              >
                Stop Stream
              </button>
            </div>

            {streamRuntime && (
              <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-4 text-sm">
                <div className="rounded-md border border-gray-200 p-3">
                  Stream Status: {streamRuntime.status}
                </div>
                <div className="rounded-md border border-gray-200 p-3">
                  Frames: {streamRuntime.frames_processed}
                </div>
                <div className="rounded-md border border-gray-200 p-3">
                  Captures: {streamRuntime.captures_succeeded}
                </div>
                <div className="rounded-md border border-gray-200 p-3">
                  Last Error: {streamRuntime.last_error || '-'}
                </div>
              </div>
            )}
          </div>
        )}

        {sessionId && (
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="text-lg font-semibold">AI Face Capture (Photo Mode)</h2>
            <p className="mt-1 text-sm text-gray-600">
              Upload a classroom photo to auto-mark attendance from approved face profiles.
            </p>
            <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center">
              <input
                type="file"
                accept="image/*"
                onChange={(event) => setAiCaptureFile(event.target.files?.[0] || null)}
                className="rounded-md border px-3 py-2 text-sm"
              />
              <button
                type="button"
                onClick={runAiCapture}
                className="rounded-md bg-emerald-600 px-4 py-2 text-sm text-white disabled:bg-emerald-300"
                disabled={loading}
              >
                {loading ? 'Running AI...' : 'Run AI Attendance'}
              </button>
            </div>

            {aiCaptureResult && (
              <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-4 text-sm">
                <div className="rounded-md border border-gray-200 p-3">
                  Faces Detected: {aiCaptureResult.total_faces_detected}
                </div>
                <div className="rounded-md border border-gray-200 p-3">
                  Matched: {aiCaptureResult.matched_students}
                </div>
                <div className="rounded-md border border-gray-200 p-3">
                  Late Detections: {aiCaptureResult.late_detections}
                </div>
                <div className="rounded-md border border-gray-200 p-3">
                  AI Accuracy: {aiCaptureResult.ai_attendance_accuracy_percent}%
                </div>
              </div>
            )}
          </div>
        )}

        {notificationResults && (
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="text-lg font-semibold">Notification Summary</h2>
            <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-4 text-sm">
              <div className="rounded-md border border-gray-200 p-3">Student SMS: {notificationResults.student_sms || 0}</div>
              <div className="rounded-md border border-gray-200 p-3">Parent SMS: {notificationResults.parent_sms || 0}</div>
              <div className="rounded-md border border-gray-200 p-3">Student Emails: {notificationResults.student_emails || 0}</div>
              <div className="rounded-md border border-gray-200 p-3">Parent Emails: {notificationResults.parent_emails || 0}</div>
            </div>
          </div>
        )}
      </div>
  );
}

function StudentAttendance() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('');
  const [enrollFiles, setEnrollFiles] = useState([]);
  const [consentGiven, setConsentGiven] = useState(false);
  const [enrollLoading, setEnrollLoading] = useState(false);
  const [enrollStatus, setEnrollStatus] = useState('');

  useEffect(() => {
    const loadHistory = async () => {
      setLoading(true);
      try {
        const history = await attendanceService.getMyAttendanceHistory();
        setRecords(history);
      } catch (error) {
        setStatus(getApiErrorMessage(error, 'Failed to load attendance history'));
      } finally {
        setLoading(false);
      }
    };
    loadHistory();
  }, []);

  const total = records.length;
  const present = records.filter((record) => record.status === 'present').length;
  const absent = records.filter((record) => record.status === 'absent').length;
  const percentage = total ? ((present / total) * 100).toFixed(2) : '0.00';

  const handleEnrollment = async () => {
    if (enrollFiles.length < 5 || enrollFiles.length > 10) {
      setEnrollStatus('Upload between 5 and 10 face images.');
      return;
    }
    if (!consentGiven) {
      setEnrollStatus('Consent is required for biometric enrollment.');
      return;
    }

    setEnrollLoading(true);
    setEnrollStatus('');
    try {
      const result = await aiService.enrollFaceProfile({
        files: enrollFiles,
        consentGiven,
      });
      setEnrollStatus(
        `Enrollment submitted. Status: ${result.approval_status}. Samples: ${result.sample_count}.`
      );
      setEnrollFiles([]);
    } catch (error) {
      setEnrollStatus(getApiErrorMessage(error, 'Face enrollment failed'));
    } finally {
      setEnrollLoading(false);
    }
  };

  return (
      <div className="space-y-6">
        {status && <div className="rounded-md bg-red-50 px-4 py-2 text-sm text-red-700">{status}</div>}

        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold">Face Enrollment (One-Time)</h2>
          <p className="mt-1 text-sm text-gray-600">
            Upload 5-10 images for AI attendance. Enrollment requires admin approval.
          </p>
          <div className="mt-4 space-y-3">
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={(event) => setEnrollFiles(Array.from(event.target.files || []))}
              className="w-full rounded-md border px-3 py-2 text-sm"
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={consentGiven}
                onChange={(event) => setConsentGiven(event.target.checked)}
              />
              I consent to biometric enrollment for attendance automation.
            </label>
            <button
              type="button"
              onClick={handleEnrollment}
              disabled={enrollLoading}
              className="rounded-md bg-emerald-600 px-4 py-2 text-sm text-white disabled:bg-emerald-300"
            >
              {enrollLoading ? 'Submitting...' : 'Submit Enrollment'}
            </button>
            {enrollStatus && <p className="text-sm text-gray-700">{enrollStatus}</p>}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-4 text-sm">
          <div className="rounded-md border border-gray-200 bg-white p-3">Total: {total}</div>
          <div className="rounded-md border border-gray-200 bg-white p-3">Present: {present}</div>
          <div className="rounded-md border border-gray-200 bg-white p-3">Absent: {absent}</div>
          <div className="rounded-md border border-gray-200 bg-white p-3">Attendance: {percentage}%</div>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold">Attendance History</h2>
          {loading ? (
            <p className="mt-3 text-sm text-gray-600">Loading...</p>
          ) : records.length === 0 ? (
            <p className="mt-3 text-sm text-gray-600">No attendance records found.</p>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead>
                  <tr className="text-left">
                    <th className="px-3 py-2">Marked At</th>
                    <th className="px-3 py-2">Session ID</th>
                    <th className="px-3 py-2">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {records.map((record) => (
                    <tr key={record.record_id}>
                      <td className="px-3 py-2">{new Date(record.marked_at).toLocaleString()}</td>
                      <td className="px-3 py-2 font-mono">{record.session_id.slice(0, 8)}</td>
                      <td className="px-3 py-2">{record.status}</td>
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

export default AttendancePage;
