import api from './api';

const aiService = {
  async enrollFaceProfile({ files, consentGiven = true, studentId = null }) {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    formData.append('consent_given', String(consentGiven));
    if (studentId) {
      formData.append('student_id', String(studentId));
    }

    const response = await api.post('/ai/attendance/enroll', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async getPendingEnrollments() {
    const response = await api.get('/ai/attendance/enrollments/pending');
    return response.data;
  },

  async reviewEnrollment(studentId, action) {
    const response = await api.post(`/ai/attendance/enrollments/${studentId}/review`, { action });
    return response.data;
  },

  async captureAttendancePhoto({
    sessionId,
    file,
    confidenceThreshold = 0.75,
    lateThresholdMinutes = 10,
  }) {
    const formData = new FormData();
    formData.append('image_file', file);
    formData.append('confidence_threshold', String(confidenceThreshold));
    formData.append('late_threshold_minutes', String(lateThresholdMinutes));

    const response = await api.post(`/ai/attendance/sessions/${sessionId}/capture-photo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async startAttendanceStream({
    sessionId,
    sourceUrl,
    confidenceThreshold = 0.75,
    lateThresholdMinutes = 10,
  }) {
    const response = await api.post('/ai/attendance/stream/start', {
      session_id: sessionId,
      source_url: sourceUrl,
      confidence_threshold: confidenceThreshold,
      late_threshold_minutes: lateThresholdMinutes,
    });
    return response.data;
  },

  async getAttendanceStreamStatus(streamId) {
    const response = await api.get(`/ai/attendance/stream/${streamId}`);
    return response.data;
  },

  async stopAttendanceStream(streamId) {
    const response = await api.post(`/ai/attendance/stream/${streamId}/stop`);
    return response.data;
  },

  async getFacultyAttendanceInsights(threshold = 75) {
    const response = await api.get('/ai/attendance/faculty-insights', {
      params: { threshold },
    });
    return response.data;
  },

  async getFoodRush(vendorId = null) {
    const response = await api.get('/ai/food/rush', {
      params: vendorId ? { vendor_id: vendorId } : undefined,
    });
    return response.data;
  },
};

export default aiService;
