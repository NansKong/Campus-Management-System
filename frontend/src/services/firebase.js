import { getApp, getApps, initializeApp } from 'firebase/app';
import { getAnalytics, isSupported } from 'firebase/analytics';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || '',
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || '',
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || '',
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: process.env.REACT_APP_FIREBASE_APP_ID || '',
  measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID || '',
};

const requiredKeys = ['apiKey', 'authDomain', 'projectId', 'appId'];
const isFirebaseConfigured = requiredKeys.every(
  (key) =>
    Boolean(firebaseConfig[key]) &&
    !String(firebaseConfig[key]).toLowerCase().includes('your-')
);

let firebaseApp = null;
let firebaseAuth = null;
let firebaseAnalytics = null;

function ensureFirebaseAuth() {
  if (!isFirebaseConfigured) {
    return null;
  }
  if (firebaseAuth) {
    return firebaseAuth;
  }

  try {
    firebaseApp = getApps().length ? getApp() : initializeApp(firebaseConfig);
    firebaseAuth = getAuth(firebaseApp);
    return firebaseAuth;
  } catch (error) {
    console.warn('Firebase auth initialization failed.', error);
    return null;
  }
}

async function ensureFirebaseAnalytics() {
  if (!isFirebaseConfigured || !firebaseConfig.measurementId) {
    return null;
  }
  if (firebaseAnalytics) {
    return firebaseAnalytics;
  }

  try {
    if (typeof window === 'undefined') {
      return null;
    }
    const supported = await isSupported();
    if (!supported) {
      return null;
    }

    if (!firebaseApp) {
      firebaseApp = getApps().length ? getApp() : initializeApp(firebaseConfig);
    }
    firebaseAnalytics = getAnalytics(firebaseApp);
    return firebaseAnalytics;
  } catch (error) {
    console.warn('Firebase analytics initialization skipped.', error);
    return null;
  }
}

export { firebaseAuth, ensureFirebaseAuth, ensureFirebaseAnalytics, isFirebaseConfigured };
export { firebaseConfig };
