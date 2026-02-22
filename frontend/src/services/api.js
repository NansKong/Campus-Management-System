import axios from 'axios';
import { ensureFirebaseAuth, isFirebaseConfigured } from './firebase';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  async (config) => {
    let token = null;
    if (isFirebaseConfigured) {
      const firebaseAuth = ensureFirebaseAuth();
      if (firebaseAuth?.currentUser) {
        token = await firebaseAuth.currentUser.getIdToken();
        localStorage.setItem('token', token);
      }
    }
    if (!token) token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
