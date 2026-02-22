import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const loadUser = async () => {
      if (!authService.isAuthenticated()) {
        if (mounted) {
          setUser(null);
          setLoading(false);
        }
        return;
      }

      try {
        const userData = await authService.getCurrentUser();
        if (mounted) {
          setUser(userData);
        }
      } catch (error) {
        const status = error?.response?.status;
        const detail = String(error?.response?.data?.detail || '').toLowerCase();
        const missingProfile =
          status === 404 ||
          (status === 401 &&
            (detail.includes('register first') || detail.includes('profile not found')));

        if (missingProfile) {
          if (mounted) {
            setUser(null);
          }
          return;
        }

        console.error('Failed to load user:', error);
        await authService.logout();
        if (mounted) {
          setUser(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    const unsubscribe = authService.onAuthStateChanged(async () => {
      if (authService.isFirebaseAuthEnabled()) {
        setLoading(true);
      }
      await loadUser();
    });

    loadUser();

    return () => {
      mounted = false;
      unsubscribe();
    };
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    const userData = await authService.getCurrentUser();
    setUser(userData);
    return data;
  };

  const loginWithGoogle = async (role = 'student') => {
    const data = await authService.loginWithGoogle();
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
      return data;
    } catch (error) {
      const status = error?.response?.status;
      const detail = String(error?.response?.data?.detail || '').toLowerCase();
      const missingProfile =
        status === 404 || (status === 401 && detail.includes('register first'));

      if (!missingProfile) {
        throw error;
      }

      await authService.registerCurrentUserProfile(role);
      const userData = await authService.getCurrentUser();
      setUser(userData);
      return data;
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const value = {
    user,
    login,
    loginWithGoogle,
    logout,
    loading,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
