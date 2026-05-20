import { Outlet, NavLink } from 'react-router-dom';
import { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Container, Row, Col } from 'react-bootstrap';
import { LayoutDashboard, Bell, Shield, Settings, LogOut, Box, Search, HelpCircle, Terminal, User, Network } from 'lucide-react';
import { ToastContainer } from 'react-toastify';

export default function Layout() {
  const { logout, user } = useContext(AuthContext);

  // ── Estado del sistema en vivo ──────────────────────────────
  const [systemHealth, setSystemHealth] = useState({
    status: 'checking',
    ml_loaded: false,
    uptime: '000:00:00',
  });
  const [alertsCount, setAlertsCount] = useState(0);

  // Polling de /api/health cada 30 segundos
  useEffect(() => {
    const fetchHealth = () => {
      fetch('http://localhost:8000/api/health')
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) {
            setSystemHealth({
              status: data.status,
              ml_loaded: data.components?.ml_model?.status === 'loaded',
              uptime: data.uptime || '000:00:00',
            });
          }
        })
        .catch(() => {
          setSystemHealth(prev => ({ ...prev, status: 'offline' }));
        });
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Polling de alertas pendientes cada 10 segundos
  useEffect(() => {
    const fetchAlerts = () => {
      fetch('http://localhost:8000/api/stats/alerts-count')
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) {
            setAlertsCount(data.pending_count || 0);
          }
        })
        .catch(() => {});
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  // Determinar color del indicador de estado
  const statusDotClass = systemHealth.status === 'online' ? 'green'
    : systemHealth.status === 'degraded' ? 'yellow'
    : systemHealth.status === 'offline' ? 'red'
    : '';

  const statusText = systemHealth.status === 'online' ? 'ACTIVO'
    : systemHealth.status === 'degraded' ? 'PARCIAL'
    : systemHealth.status === 'offline' ? 'OFFLINE'
    : 'VERIFICANDO';

  return (
    <Container fluid className="p-0 dashboard-root">
      <ToastContainer />
      <div className="layout-container">
        {/* Sidebar */}
        <aside className="cyber-sidebar">
          <div className="sidebar-brand">
            <Box size={32} className="brand-icon" />
            <div className="brand-text">
              <div className="brand-name">SMAR-IA</div>
              <div className="brand-version">IDS v1.0 NIDS</div>
            </div>
          </div>

          <nav className="sidebar-nav">
            <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <LayoutDashboard size={20} /> <span>PANEL DE CONTROL</span>
            </NavLink>
            <NavLink to="/traffic" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Bell size={20} /> <span>ALERTAS</span>
            </NavLink>
            <NavLink to="/mitigation" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Shield size={20} /> <span>MITIGACIÓN</span>
            </NavLink>
            <NavLink to="/settings" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Settings size={20} /> <span>CONFIGURACIÓN</span>
            </NavLink>
          </nav>

          <div className="sidebar-actions mt-auto">
            <button className="cyber-btn-secondary w-100 mb-4">
              DESPLEGAR MITIGACIÓN
            </button>
            <div className="sidebar-footer-links">
              <a href="#support"><HelpCircle size={16} /> SOPORTE</a>
              <NavLink to="/logs" className={({ isActive }) => `footer-nav-link ${isActive ? 'active' : ''}`}>
                <Terminal size={16} /> <span>REGISTROS</span>
              </NavLink>
              <button className="logout-link" onClick={logout}>

                <LogOut size={16} /> CERRAR SESIÓN
              </button>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="main-content">
          {/* Header */}
          <header className="cyber-header">
            <div className="header-logo">SMAR-IA</div>
            <div className="header-search">
              <Search size={18} className="search-icon" />
              <input type="text" placeholder="CONSULTAR RED..." />
            </div>
            <div className="header-status">
              <div className="status-item">
                <div className={`status-dot ${statusDotClass}`}></div>
                ESTADO IA: {statusText}
              </div>
              <div className="status-item">SISTEMA: {systemHealth.status === 'online' ? '100%' : systemHealth.status === 'degraded' ? 'PARCIAL' : 'N/A'}</div>
            </div>
            <div className="header-actions">
              <Network size={20} />
              <Shield size={20} />
              <div className="notification-icon">
                <Bell size={20} />
                {alertsCount > 0 && <span className="count">{alertsCount > 99 ? '99+' : alertsCount}</span>}
              </div>
              <div className="user-profile" title={user?.username || 'admin'}>
                <User size={20} />
              </div>
            </div>
          </header>

          {/* Page Content */}
          <div className="page-content">
            <Outlet />
          </div>
        </main>
      </div>
    </Container>
  );
}
