import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useContext, useState, useEffect, useRef } from 'react';
import { AuthContext } from '../context/AuthContext';
import { ThemeContext } from '../context/ThemeContext';
import { apiUrl, apiGet } from '../api';
import {
  LayoutDashboard, Bell, Shield, Settings, LogOut,
  Terminal, Activity, Search, Network, Moon, Sun, ScrollText,
  X, ExternalLink, User, ChevronDown, Filter
} from 'lucide-react';


const NAV_ITEMS = [
  { to: '/',           label: 'Panel Principal', icon: LayoutDashboard, end: true },
  { to: '/traffic',    label: 'Análisis de Tráfico', icon: Activity },
  { to: '/mitigation', label: 'Detección de Amenazas', icon: Shield },
  { to: '/rules',      label: 'Reglas de Mitigación', icon: ScrollText },
  { to: '/settings',   label: 'Configuración ML', icon: Settings },
  { to: '/logs',       label: 'Registros', icon: Terminal },
];

export default function Layout() {
  const { logout, user, token } = useContext(AuthContext);
  const { theme, toggleTheme } = useContext(ThemeContext);
  const location = useLocation();
  const navigate = useNavigate();
  const [systemHealth, setSystemHealth] = useState({ status: 'checking', ml_loaded: false, uptime: '000:00:00' });
  const [alertsCount, setAlertsCount] = useState(0);
  const [alertsList, setAlertsList] = useState([]);
  const [showNotifPanel, setShowNotifPanel] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const notifRef = useRef(null);
  const userRef = useRef(null);

  useEffect(() => {
    const fetchHealth = () => {
      fetch(apiUrl('/api/health'))
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
      fetch(apiUrl('/api/stats/alerts-count'))
        .then(r => r.ok ? r.json() : null)
        .then(d => {
          if (d) {
            setAlertsCount(d.pending_count || 0);
            setAlertsList(d.recent_alerts || []);
          }
        })
        .catch(() => {});
    };
    fetch_();
    const iv = setInterval(fetch_, 10000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    function handleClick(e) {
      if (notifRef.current && !notifRef.current.contains(e.target)) setShowNotifPanel(false);
      if (userRef.current && !userRef.current.contains(e.target)) setShowUserMenu(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/logs?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  const netDiagramUrl = `https://www.google.com/maps?q=${systemHealth.status === 'online' ? 'SmarIA+Network' : ''}`;

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
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '12px',
            backgroundColor: '#f1f5f9',
            border: '1px solid #cbd5e1',
            borderRadius: '8px',
            marginBottom: '12px'
          }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '6px',
              backgroundColor: '#4b1a9e',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              fontWeight: 700,
              fontSize: '0.85rem',
              flexShrink: 0
            }}>
              AD
            </div>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#1e293b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.username || 'Usuario Admin'}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#64748b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                Líder de Seguridad
              </div>
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

          <form className="app-header-search" onSubmit={handleSearch}>
            <Search size={15} className="search-icon" />
            <input type="text" placeholder="Buscar IPs, eventos..."
              value={searchQuery} onChange={e => setSearchQuery(e.target.value)} />
          </form>

          <div style={{marginLeft:'auto', display:'flex', alignItems:'center', gap:10}}>
            <div className="header-status-badge">
              <span className={`status-dot ${dotClass}`} />
              IA: {statusLabel}
            </div>
            <div className="header-divider" />
            <div className="header-icon-btn" onClick={toggleTheme} title={`Cambiar a tema ${theme === 'dark' ? 'claro' : 'oscuro'}`}>
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </div>
            <div className="header-icon-btn" onClick={() => window.open(netDiagramUrl, '_blank')} title="Ver red">
              <Network size={16} />
            </div>
            <div className="header-icon-btn" style={{position:'relative'}} ref={notifRef} onClick={() => setShowNotifPanel(p => !p)}>
              <Bell size={16} />
              {alertsCount > 0 && <span className="header-notif-count">{alertsCount > 9 ? '9+' : alertsCount}</span>}
              {showNotifPanel && (
                <div className="dropdown-panel notif-panel">
                  <div className="dropdown-panel-header">
                    <span>Notificaciones</span>
                    <X size={14} onClick={() => setShowNotifPanel(false)} style={{cursor:'pointer'}} />
                  </div>
                  {alertsList.length > 0 ? alertsList.slice(0, 5).map((a, i) => (
                    <div key={i} className="dropdown-panel-item">
                      <div className="dropdown-panel-item-title">{a.attack_type || 'Evento'}</div>
                      <div className="dropdown-panel-item-sub">{a.source_ip} · {a.timestamp ? new Date(a.timestamp).toLocaleTimeString('es-PE', {hour12:false}) : ''}</div>
                    </div>
                  )) : (
                    <div className="dropdown-panel-item" style={{color:'var(--text-muted)'}}>Sin notificaciones recientes</div>
                  )}
                  <div className="dropdown-panel-footer" onClick={() => { navigate('/traffic'); setShowNotifPanel(false); }}>
                    Ver todas las alertas
                  </div>
                </div>
              )}
            </div>
            <div className="header-avatar" ref={userRef} onClick={() => setShowUserMenu(p => !p)} style={{cursor:'pointer'}}>
              {(user?.username || 'A').charAt(0).toUpperCase()}
              {showUserMenu && (
                <div className="dropdown-panel user-menu">
                  <div className="dropdown-panel-header">
                    <User size={14} />
                    <span>{user?.username || 'admin'}</span>
                  </div>
                  <div className="dropdown-panel-item" onClick={() => { navigate('/settings'); setShowUserMenu(false); }}>
                    Configuración
                  </div>
                  <div className="dropdown-panel-item" onClick={() => { logout(); setShowUserMenu(false); }}>
                    Cerrar Sesión
                  </div>
                </div>
              )}
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
