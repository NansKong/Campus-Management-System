import api from './api';

const attendanceService = {
  async getMySections() {
    try {
      const response = await api.get('/attendance/sections/my');
      return response.data;
    } catch (error) {
      console.error('Get sections error:', error.response?.data || error.message);
      throw error;
    }
  },

  async getAvailableClassrooms() {
    try {
      const response = await api.get('/attendance/classrooms');
      return response.data;
    } catch (error) {
      console.error('Get classrooms error:', error.response?.data || error.message);
      throw error;
    }
  },

  async getSectionStudents(sectionId) {
    try {
      const response = await api.get(`/attendance/sections/${sectionId}/students`);
      return response.data;
    } catch (error) {
      console.error('Get section students error:', error.response?.data || error.message);
      throw error;
    }
  },

  async createSession(sessionData) {
    try {
      const response = await api.post('/attendance/sessions', sessionData);
      return response.data;
    } catch (error) {
      console.error('Create session error:', error.response?.data || error.message);
      throw error;
    }
  },

  async markAttendance(sessionId, attendanceRecords) {
    try {
      const response = await api.post(`/attendance/sessions/${sessionId}/mark`, {
        attendance_records: attendanceRecords,
      });
      return response.data;
    } catch (error) {
      console.error('Mark attendance error:', error.response?.data || error.message);
      throw error;
    }
  },

  async getStudentAttendance(studentId) {
    try {
      const response = await api.get(`/attendance/student/${studentId}`);
      return response.data;
    } catch (error) {
      console.error('Get student attendance error:', error.response?.data || error.message);
      throw error;
    }
  },

  async getMyAttendanceHistory() {
    try {
      const response = await api.get('/attendance/me/history');
      return response.data;
    } catch (error) {
      console.error('Get my attendance history error:', error.response?.data || error.message);
      throw error;
    }
  },
};

export default attendanceService;
