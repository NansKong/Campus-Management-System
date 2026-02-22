import api from './api';

const studentService = {
  async listStudents(params = {}) {
    try {
      const response = await api.get('/students', { params });
      return response.data;
    } catch (error) {
      console.error('List students error:', error.response?.data || error.message);
      throw error;
    }
  },

  async createStudent(payload) {
    try {
      const response = await api.post('/students', payload);
      return response.data;
    } catch (error) {
      console.error('Create student error:', error.response?.data || error.message);
      throw error;
    }
  },

  async updateStudent(studentId, payload) {
    try {
      const response = await api.put(`/students/${studentId}`, payload);
      return response.data;
    } catch (error) {
      console.error('Update student error:', error.response?.data || error.message);
      throw error;
    }
  },
};

export default studentService;
