import api from './api';

const remedialService = {
  async listClasses(params = {}) {
    try {
      const response = await api.get('/remedial/classes', { params });
      return response.data;
    } catch (error) {
      console.error('List remedial classes error:', error.response?.data || error.message);
      throw error;
    }
  },

  async createClass(payload) {
    try {
      const response = await api.post('/remedial/classes', payload);
      return response.data;
    } catch (error) {
      console.error('Create remedial class error:', error.response?.data || error.message);
      throw error;
    }
  },

  async updateClass(remedialId, payload) {
    try {
      const response = await api.put(`/remedial/classes/${remedialId}`, payload);
      return response.data;
    } catch (error) {
      console.error('Update remedial class error:', error.response?.data || error.message);
      throw error;
    }
  },

  async markAttendance(remedialCode) {
    try {
      const response = await api.post('/remedial/attendance/mark', {
        remedial_code: remedialCode,
      });
      return response.data;
    } catch (error) {
      console.error('Mark remedial attendance error:', error.response?.data || error.message);
      throw error;
    }
  },

  async getMyAttendanceHistory() {
    try {
      const response = await api.get('/remedial/attendance/my-history');
      return response.data;
    } catch (error) {
      console.error('Get remedial attendance history error:', error.response?.data || error.message);
      throw error;
    }
  },
};

export default remedialService;
