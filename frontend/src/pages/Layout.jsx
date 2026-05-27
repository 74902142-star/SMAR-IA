import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { ThemeContext } from '../context/ThemeContext';
import {
  LayoutDashboard, Bell, Shield, Settings, LogOut,
  Terminal, Activity, Search, Network, Moon, Sun, ScrollText
} from 'lucide-react';


const NAV_ITEMS = [
  { to: '/',           label: 'Panel de Control', icon: LayoutDashboard, end: true },
  { to: '/traffic',    label: 'Alertas',           icon: Bell },
  { to: '/mitigation', label: 'Mitigación',        icon: Shield },
  { to: '/rules',      label: 'Reglas',            icon: ScrollText },
  { to: '/logs',       label: 'Registros',         icon: Terminal },
  { to: '/settings',  label: 'Configuración',     icon: Settings },
];

export default function Layout() {
  const { logout, user } = useContext(AuthContext);
  const { theme, toggleTheme } = useContext(ThemeContext);
  const location = useLocation();
  const [systemHealth, setSystemHealth] = useState({ status: 'checking', ml_loaded: false, uptime: '000:00:00' });
  const [alertsCount, setAlertsCount] = useState(0);

  useEffect(() => {
    const fetchHealth = () => {
      fetch('http://localhost:8000/api/health')
        .then(r => r.ok ? r.json() : null)
        .then(d => {
          if (d) setSystemHealth({ status: d.status, ml_loaded: d.components?.ml_model?.status === 'loaded', uptime: d.uptime || '000:00:00' });
        })
        .catch(() => setSystemHealth(p => ({ ...p, status: 'offline' })));
    };
    fetchHealth();
    const iv = setInterval(fetchHealth, 30000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const fetch_ = () => {
      fetch('http://localhost:8000/api/stats/alerts-count')
        .then(r => r.ok ? r.json() : null)
        .then(d => { if (d) setAlertsCount(d.pending_count || 0); })
        .catch(() => {});
    };
    fetch_();
    const iv = setInterval(fetch_, 10000);
    return () => clearInterval(iv);
  }, []);

  const dotClass = systemHealth.status === 'online' ? 'green' : systemHealth.status === 'degraded' ? 'yellow' : systemHealth.status === 'offline' ? 'red' : '';
  const statusLabel = systemHealth.status === 'online' ? 'EN LÍNEA' : systemHealth.status === 'degraded' ? 'PARCIAL' : systemHealth.status === 'offline' ? 'OFFLINE' : 'VERIFICANDO';

  const currentTitle = NAV_ITEMS.find(i => i.end ? location.pathname === i.to : location.pathname.startsWith(i.to))?.label || 'Panel';

  return (
    <div className="app-layout">

      {/* Sidebar */}
      <aside className="app-sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <Shield size={20} />
          </div>
          <div className="sidebar-logo-text">
            <div className="sidebar-logo-name">SMAR-IA</div>
            <div className="sidebar-logo-version">IDS v1.0 · NIDS</div>
          </div>
        </div>

        <div className="sidebar-section-label">Navegación</div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} />
              <span>{label}</span>
              {label === 'Alertas' && alertsCount > 0 && (
                <span className="sidebar-nav-badge">{alertsCount > 99 ? '99+' : alertsCount}</span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-system-status">
            <div className="label">ESTADO DEL SISTEMA</div>
            <div className="value">
              <span className={`status-dot ${dotClass} pulse`} />
              <span style={{color: dotClass === 'green' ? 'var(--emerald)' : dotClass === 'red' ? 'var(--rose)' : 'var(--amber)'}}>{statusLabel}</span>
            </div>
            <div className="value" style={{marginTop:4, fontSize:'0.65rem', color:'var(--text-muted)'}}>
              <Activity size={11} style={{marginRight:4}} />
              {systemHealth.uptime}
            </div>
          </div>
          <button className="sidebar-nav-item" onClick={logout} style={{color:'var(--rose)'}}>
            <LogOut size={17} />
            <span>Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="app-main">
        <header className="app-header">
          <span className="app-header-title">{currentTitle}</span>

          <div className="app-header-search">
            <Search size={15} className="search-icon" />
            <input type="text" placeholder="Buscar IPs, eventos..." />
          </div>

          <div style={{marginLeft:'auto', display:'flex', alignItems:'center', gap:10}}>
            <div className="header-status-badge">
              <span className={`status-dot ${dotClass}`} />
              IA: {statusLabel}
            </div>
            <div className="header-divider" />
            <div className="header-icon-btn" onClick={toggleTheme} title={`Cambiar a tema ${theme === 'dark' ? 'claro' : 'oscuro'}`}>
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </div>
            <div className="header-icon-btn">
              <Network size={16} />
            </div>
            <div className="header-icon-btn" style={{position:'relative'}}>
              <Bell size={16} />
              {alertsCount > 0 && <span className="header-notif-count">{alertsCount > 9 ? '9+' : alertsCount}</span>}
            </div>
            <div className="header-avatar" title={user?.username || 'admin'}>
              {(user?.username || 'A').charAt(0).toUpperCase()}
            </div>
          </div>
        </header>

        <div className="page-wrapper">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
