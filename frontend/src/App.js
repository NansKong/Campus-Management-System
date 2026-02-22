// import React from 'react';
// import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// import { AuthProvider, useAuth } from './context/AuthContext';
// import { ThemeProvider } from './context/ThemeContext';
// import Login from './components/Auth/Login';
// import Dashboard from './pages/Dashboard';
// import FoodOrderPage from './pages/FoodOrderPage';
// import AttendancePage from './pages/AttendancePage';
// import RemedialPage from './pages/RemedialPage';
// import ResourcesPage from './pages/ResourcesPage';
// import FoodAnalyticsPage from './pages/FoodAnalyticsPage';

// // Protected Route Component
// function ProtectedRoute({ children }) {
//   const { isAuthenticated, loading } = useAuth();

//   if (loading) {
//     return (
//       <div className="flex items-center justify-center min-h-screen">
//         <div className="text-xl font-semibold">Loading...</div>
//       </div>
//     );
//   }

//   return isAuthenticated ? children : <Navigate to="/" />;
// }

// function AppRoutes() {
//   return (
//     <Routes>
//       <Route path="/" element={<Login />} />
//       <Route
//         path="/dashboard"
//         element={
//           <ProtectedRoute>
//             <Dashboard />
//           </ProtectedRoute>
//         }
//       />
//       <Route
//         path="/attendance"
//         element={
//           <ProtectedRoute>
//             <AttendancePage />
//           </ProtectedRoute>
//         }
//       />
//       <Route
//         path="/food"
//         element={
//           <ProtectedRoute>
//             <FoodOrderPage />
//           </ProtectedRoute>
//         }
//       />
//       <Route
//         path="/food-analytics"
//         element={
//           <ProtectedRoute>
//             <FoodAnalyticsPage />
//           </ProtectedRoute>
//         }
//       />
//       <Route
//         path="/remedial"
//         element={
//           <ProtectedRoute>
//             <RemedialPage />
//           </ProtectedRoute>
//         }
//       />
//       <Route
//         path="/resources"
//         element={
//           <ProtectedRoute>
//             <ResourcesPage />
//           </ProtectedRoute>
//         }
//       />
//     </Routes>
//   );
// }

// function App() {
//   return (
//     <Router>
//       <ThemeProvider>
//         <AuthProvider>
//           <AppRoutes />
//         </AuthProvider>
//       </ThemeProvider>
//     </Router>
//   );
// }

// export default App;

import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

import AppLayout from './components/layout/AppLayout';

// Auth
import Login from './components/Auth/Login';

// Pages
import Dashboard from './pages/Dashboard';
import AttendancePage from './pages/AttendancePage';
import FoodOrderPage from './pages/FoodOrderPage';
import FoodAnalyticsPage from './pages/FoodAnalyticsPage';
import RemedialPage from './pages/RemedialPage';
import ResourcesPage from './pages/ResourcesPage';
import ProfilePage from './pages/ProfilePage';
import StudentManagementPage from './pages/StudentManagementPage';
import { ensureFirebaseAnalytics } from './services/firebase';

/* ---------------- Protected Route ---------------- */

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <span className="text-lg font-semibold">Loading...</span>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/" />;
}

/* ---------------- App Routes ---------------- */

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Login />} />

      {/* Protected with Layout */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/attendance" element={<AttendancePage />} />
        <Route path="/food" element={<FoodOrderPage />} />
        <Route path="/food-analytics" element={<FoodAnalyticsPage />} />
        <Route path="/remedial" element={<RemedialPage />} />
        <Route path="/students" element={<StudentManagementPage />} />
        <Route path="/resources" element={<ResourcesPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>
    </Routes>
  );
}

/* ---------------- Root App ---------------- */

function App() {
  useEffect(() => {
    ensureFirebaseAnalytics();
  }, []);

  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
