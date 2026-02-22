import api from './api';
import {
  createUserWithEmailAndPassword,
  deleteUser,
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  signInWithEmailAndPassword,
  signOut,
} from 'firebase/auth';
import { ensureFirebaseAuth, firebaseConfig, isFirebaseConfigured } from './firebase';

function requireFirebaseAuth() {
  const firebaseAuth = isFirebaseConfigured ? ensureFirebaseAuth() : null;
  if (!firebaseAuth) {
    throw new Error(
      'Firebase auth is not configured. Set REACT_APP_FIREBASE_* variables and restart frontend.'
    );
  }
  return firebaseAuth;
}

function toFriendlyAuthError(error) {
  if (error?.response) {
    return error;
  }

  if (typeof error?.code === 'string' && error.code.startsWith('auth/')) {
    if (error.code === 'auth/configuration-not-found') {
      const projectId = firebaseConfig.projectId || '(missing REACT_APP_FIREBASE_PROJECT_ID)';
      return new Error(
        `Firebase Auth configuration is missing for project "${projectId}". ` +
          'In Firebase Console -> Authentication -> Sign-in method, enable Email/Password, ' +
          'and in Authentication -> Settings -> Authorized domains add localhost.'
      );
    }
    if (error.code === 'auth/operation-not-allowed') {
      return new Error(
        'Email/Password sign-in is disabled in Firebase Console. Enable it under Authentication -> Sign-in method.'
      );
    }
    if (error.code === 'auth/invalid-api-key') {
      return new Error(
        'Invalid Firebase API key. Check REACT_APP_FIREBASE_API_KEY in frontend/.env and restart the frontend.'
      );
    }
    if (error.code === 'auth/popup-closed-by-user') {
      return new Error('Google sign-in was cancelled. Please try again.');
    }
    if (error.code === 'auth/operation-not-supported-in-this-environment') {
      return new Error('Google sign-in popup is blocked in this environment. Enable popups and retry.');
    }
    return new Error(error.message || 'Firebase authentication failed.');
  }

  const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000/api';
  const friendlyError = new Error(
    `Cannot reach backend API at ${baseUrl}. Verify backend is running and REACT_APP_API_BASE_URL is correct.`
  );
  friendlyError.cause = error;
  return friendlyError;
}

async function registerBackendProfile({ email, role }) {
  if (!email) {
    throw new Error('Authenticated account email was not found.');
  }
  const response = await api.post('/auth/register', { email, role });
  return response.data;
}

const authService = {
  async register(userData) {
    const firebaseAuth = requireFirebaseAuth();
    let createdCredential = null;

    try {
      createdCredential = await createUserWithEmailAndPassword(
        firebaseAuth,
        userData.email,
        userData.password
      );
    } catch (error) {
      throw toFriendlyAuthError(error);
    }

    try {
      if (createdCredential?.user) {
        const idToken = await createdCredential.user.getIdToken();
        localStorage.setItem('token', idToken);
      }

      return await registerBackendProfile({
        email: userData.email,
        role: userData.role,
      });
    } catch (error) {
      if (createdCredential?.user) {
        try {
          await deleteUser(createdCredential.user);
        } catch (cleanupError) {
          console.warn('Firebase user cleanup failed after backend register error.', cleanupError);
        }
      }
      localStorage.removeItem('token');
      throw toFriendlyAuthError(error);
    }
  },

  async login(email, password) {
    const firebaseAuth = requireFirebaseAuth();

    try {
      const credential = await signInWithEmailAndPassword(firebaseAuth, email, password);
      const idToken = await credential.user.getIdToken();
      localStorage.setItem('token', idToken);
      return { access_token: idToken, token_type: 'bearer' };
    } catch (error) {
      throw toFriendlyAuthError(error);
    }
  },

  async loginWithGoogle() {
    const firebaseAuth = requireFirebaseAuth();
    const provider = new GoogleAuthProvider();
    provider.setCustomParameters({ prompt: 'select_account' });

    try {
      const credential = await signInWithPopup(firebaseAuth, provider);
      const idToken = await credential.user.getIdToken();
      localStorage.setItem('token', idToken);
      return {
        access_token: idToken,
        token_type: 'bearer',
        email: credential.user.email,
      };
    } catch (error) {
      throw toFriendlyAuthError(error);
    }
  },

  async registerCurrentUserProfile(role) {
    const firebaseAuth = ensureFirebaseAuth();
    const email = firebaseAuth?.currentUser?.email;
    try {
      return await registerBackendProfile({ email, role });
    } catch (error) {
      throw toFriendlyAuthError(error);
    }
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async logout() {
    try {
      const firebaseAuth = ensureFirebaseAuth();
      if (isFirebaseConfigured && firebaseAuth) {
        await signOut(firebaseAuth);
      }
    } catch (error) {
      console.warn('Firebase sign-out skipped:', error);
    }
    localStorage.removeItem('token');
  },

  isAuthenticated() {
    const firebaseAuth = ensureFirebaseAuth();
    if (isFirebaseConfigured && firebaseAuth?.currentUser) {
      return true;
    }
    return !!localStorage.getItem('token');
  },

  async getAuthToken() {
    const firebaseAuth = ensureFirebaseAuth();
    if (isFirebaseConfigured && firebaseAuth?.currentUser) {
      const idToken = await firebaseAuth.currentUser.getIdToken();
      localStorage.setItem('token', idToken);
      return idToken;
    }
    return localStorage.getItem('token');
  },

  onAuthStateChanged(callback) {
    const firebaseAuth = ensureFirebaseAuth();
    if (isFirebaseConfigured && firebaseAuth) {
      return onAuthStateChanged(firebaseAuth, callback);
    }
    return () => {};
  },

  isFirebaseAuthEnabled() {
    return isFirebaseConfigured;
  },
};

export default authService;
