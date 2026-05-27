import { useContext } from 'react';
import { ThemeProvider, ThemeContext } from './context/ThemeContext';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { ToastContainer } from 'react-toastify';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Layout from './pages/Layout';
import Dashboard from './pages/Dashboard';
import TrafficMonitor from './pages/TrafficMonitor';
import MitigationZone from './pages/MitigationZone';
import Settings from './pages/Settings';
import Logs from './pages/Logs';
import RuleManager from './pages/RuleManager';



// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { token } = useContext(AuthContext);
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="traffic" element={<TrafficMonitor />} />
        <Route path="mitigation" element={<MitigationZone />} />
        <Route path="settings" element={<Settings />} />
        <Route path="logs" element={<Logs />} />
        <Route path="rules" element={<RuleManager />} />


      </Route>
    </Routes>
  );
}

function AppContent() {
  const { theme } = useContext(ThemeContext);

  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
        <ToastContainer theme={theme === 'light' ? 'light' : 'dark'} position="top-right" />
      </AuthProvider>
    </Router>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
