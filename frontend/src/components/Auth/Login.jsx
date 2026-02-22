import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import authService from '../../services/authService';
import ThemeToggle from '../ui/ThemeToggle';

function Login() {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState('student');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const toErrorMessage = (err, fallback) => {
    const detail = err?.response?.data?.detail;
    if (
      mode === 'login' &&
      err?.response?.status === 404 &&
      typeof detail === 'string' &&
      detail.toLowerCase().includes('user profile not found')
    ) {
      return 'No campus profile found for this account. Please register first.';
    }
    return detail || err?.message || fallback;
  };

  const handleLogin = async () => {
    await login(email, password);
    navigate('/dashboard');
  };

  const handleRegister = async () => {
    if (password !== confirmPassword) {
      throw new Error('Passwords do not match');
    }
    await authService.register({
      email,
      password,
      role,
    });
    await handleLogin();
  };

  const handleGoogle = async () => {
    await loginWithGoogle(role);
    navigate('/dashboard');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (mode === 'register') {
        await handleRegister();
      } else {
        await handleLogin();
      }
    } catch (err) {
      setError(
        toErrorMessage(
          err,
          mode === 'register' ? 'Registration failed' : 'Invalid email or password'
        )
      );
      console.error(`${mode} error:`, err);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleClick = async () => {
    setError('');
    setLoading(true);
    try {
      await handleGoogle();
    } catch (err) {
      setError(toErrorMessage(err, 'Google sign in failed'));
      console.error('google login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setError('');
    setMode((current) => (current === 'login' ? 'register' : 'login'));
  };

  return (
    <div
      className="relative flex min-h-screen items-center justify-center"
      style={{ background: 'linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%)' }}
    >
      <div className="absolute right-6 top-6 z-50">
        <ThemeToggle />
      </div>

      <div
        className="mx-4 flex h-auto w-full max-w-5xl overflow-hidden rounded-2xl shadow-2xl md:h-[620px]"
        style={{ background: 'var(--card-bg)' }}
      >
        <div
          className="hidden w-1/2 items-center justify-center p-12 md:flex"
          style={{ background: 'linear-gradient(135deg, #ffe5e5 0%, #ffd4d4 100%)' }}
        >
          <div className="text-center">
            <h1 className="mb-4 text-4xl font-bold text-[#1a1a1a]">
              Smart Campus
              <br />
              Attendance
              <br />
              System
            </h1>
            <p className="text-sm text-[#333]">Secure login and role-based access</p>
          </div>
        </div>

        <div className="flex w-full flex-col justify-center p-10 md:w-1/2">
          <h2 className="mb-2 text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
            {mode === 'register' ? 'Create Account' : 'Sign In'}
          </h2>
          <p className="mb-6 text-sm" style={{ color: 'var(--text-secondary)' }}>
            {mode === 'register'
              ? 'Register as a new user and continue to dashboard.'
              : 'Sign in with your Firebase account.'}
          </p>

          {error && (
            <div className="mb-4 whitespace-pre-line rounded-lg border border-red-500 bg-red-100 p-3 text-sm text-red-900">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="mb-1 block text-sm font-semibold" style={{ color: 'var(--text-color)' }}>
                  Role
                </label>
                <select
                  value={role}
                  onChange={(event) => setRole(event.target.value)}
                  className="w-full rounded-lg border px-3 py-2"
                  style={{ background: 'var(--card-bg-pink)', borderColor: 'var(--border-color)' }}
                >
                  <option value="student">Student</option>
                  <option value="faculty">Faculty</option>
                  <option value="vendor">Vendor</option>
                </select>
              </div>
            )}

            <div>
              <label className="mb-1 block text-sm font-semibold" style={{ color: 'var(--text-color)' }}>
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="name@example.com"
                required
                className="w-full rounded-lg border px-3 py-2"
                style={{ background: 'var(--card-bg-pink)', borderColor: 'var(--border-color)' }}
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-semibold" style={{ color: 'var(--text-color)' }}>
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter password"
                required
                className="w-full rounded-lg border px-3 py-2"
                style={{ background: 'var(--card-bg-pink)', borderColor: 'var(--border-color)' }}
              />
            </div>

            {mode === 'register' && (
              <div>
                <label className="mb-1 block text-sm font-semibold" style={{ color: 'var(--text-color)' }}>
                  Confirm Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="Confirm password"
                  required
                  className="w-full rounded-lg border px-3 py-2"
                  style={{ background: 'var(--card-bg-pink)', borderColor: 'var(--border-color)' }}
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg py-3 font-semibold text-white transition-all hover:shadow-lg disabled:opacity-50"
              style={{ background: loading ? '#999' : 'var(--primary-color)' }}
            >
              {loading
                ? mode === 'register'
                  ? 'Creating account...'
                  : 'Signing in...'
                : mode === 'register'
                ? 'Create Account'
                : 'Sign In'}
            </button>
          </form>

          <div className="mt-4 border-t pt-4" style={{ borderColor: 'var(--border-color)' }}>
            {mode === 'login' && (
              <div className="mb-3">
                <label className="mb-1 block text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>
                  First-time Google sign-in role
                </label>
                <select
                  value={role}
                  onChange={(event) => setRole(event.target.value)}
                  className="w-full rounded-lg border px-3 py-2 text-sm"
                  style={{ background: 'var(--card-bg-pink)', borderColor: 'var(--border-color)' }}
                >
                  <option value="student">Student</option>
                  <option value="faculty">Faculty</option>
                  <option value="vendor">Vendor</option>
                </select>
              </div>
            )}

            <button
              type="button"
              onClick={handleGoogleClick}
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg border py-3 text-sm font-semibold transition-all hover:shadow disabled:opacity-50"
              style={{ borderColor: 'var(--border-color)', color: 'var(--text-color)', background: 'var(--card-bg-pink)' }}
            >
              <GoogleIcon />
              {loading ? 'Please wait...' : 'Continue with Google'}
            </button>
          </div>

          <button
            type="button"
            className="mt-4 text-left text-sm underline"
            style={{ color: 'var(--text-secondary)' }}
            onClick={switchMode}
          >
            {mode === 'register'
              ? 'Already have an account? Sign in'
              : 'New user? Register'}
          </button>
        </div>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#FFC107" d="M43.611 20.083H42V20H24v8h11.303C33.654 32.657 29.204 36 24 36c-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.84 1.154 7.961 3.039l5.657-5.657C34.047 6.053 29.275 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z" />
      <path fill="#FF3D00" d="M6.306 14.691l6.571 4.819C14.655 16.108 19.001 12 24 12c3.059 0 5.84 1.154 7.961 3.039l5.657-5.657C34.047 6.053 29.275 4 24 4c-7.682 0-14.313 4.337-17.694 10.691z" />
      <path fill="#4CAF50" d="M24 44c5.178 0 9.86-1.977 13.409-5.192l-6.191-5.238C29.14 35.091 26.676 36 24 36c-5.183 0-9.625-3.33-11.287-7.946l-6.52 5.025C9.529 39.556 16.227 44 24 44z" />
      <path fill="#1976D2" d="M43.611 20.083H42V20H24v8h11.303a12.064 12.064 0 01-4.085 5.571l.003-.002 6.191 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z" />
    </svg>
  );
}

export default Login;
