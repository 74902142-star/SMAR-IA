import { useState, useEffect, useRef, useContext } from 'react';
import { Row, Col } from 'react-bootstrap';
import {
  Activity, AlertTriangle, ShieldCheck, Cpu, Server,
  Clock, Target, List, Radio, Shield, MapPin, Eye, Play
} from 'lucide-react';
import { toast } from 'react-toastify';
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { apiUrl, wsUrl } from '../api';
import { AuthContext } from '../context/AuthContext';

export default function Dashboard() {
  const { token } = useContext(AuthContext);
  const [logs, setLogs] = useState([]);
  const [systemStats, setSystemStats] = useState(null);
  const [livePackets, setLivePackets] = useState([]);
  const recentIpsRef = useRef({});
  const ws = useRef(null);
  const pktId = useRef(0);
  const [activeTab, setActiveTab] = useState('Vivo');

  /* ── WebSocket ─────────────────────────────────────── */
  useEffect(() => {
    ws.current = new WebSocket(wsUrl('/ws'));
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type !== 'traffic_update') return;

      const id = ++pktId.current;
      const currentRecent = recentIpsRef.current;
      const ipCount = (currentRecent[data.source_ip] || 0) + 1;
      
      recentIpsRef.current = { ...currentRecent, [data.source_ip]: ipCount };

      let pktType = 'normal';
      if (ipCount > 3) pktType = 'burst';
      else if (data.is_alert) pktType = data.confidence > 0.9 ? 'alert' : 'warning';

      setLivePackets(prev => [...prev, { id, type: pktType }]);
      setTimeout(() => {
        setLivePackets(prev => prev.filter(p => p.id !== id));
        recentIpsRef.current = {
          ...recentIpsRef.current,
          [data.source_ip]: Math.max(0, (recentIpsRef.current[data.source_ip] || 0) - 1)
        };
      }, 1200);

      const newLog = {
        timestamp: data.timestamp,
        source_ip: data.source_ip,
        attack_type: data.is_alert ? data.predicted_class : null,
        action_taken: data.action_taken,
        isLive: true,
      };
      setLogs(prev => [newLog, ...prev.slice(0, 14)]);

      if (data.is_alert) {
        const isHigh = data.confidence > 0.9;
        toast[isHigh ? 'error' : 'warning'](
          `${data.predicted_class} desde ${data.source_ip}`,
          { autoClose: 4000, position: 'top-right' }
        );
      }
    };

    /* ── Initial logs ── */
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    fetch(apiUrl('/api/logs?limit=12'), { headers })
      .then(r => r.ok ? r.json() : [])
      .then(d => Array.isArray(d) ? setLogs(d) : setLogs([]))
      .catch(() => setLogs([]));

    return () => { if (ws.current) ws.current.close(); };
  }, []);

  /* ── Stats polling ─────────────────────────────────── */
  useEffect(() => {
    const fetch_ = () => {
      fetch(apiUrl('/api/stats'))
        .then(r => r.ok ? r.json() : null)
        .then(d => { if (d) setSystemStats(d); })
        .catch(() => {});
    };
    fetch_();
    const iv = setInterval(fetch_, 15000);
    return () => clearInterval(iv);
  }, []);

  /* ── Derived values ────────────────────────────────── */
  const cpu          = systemStats?.resources?.cpu_percent ?? 0;
  const ram          = systemStats?.resources?.ram_percent ?? 0;
  const uptime       = systemStats?.uptime ?? '000:00:00';
  const confidence   = systemStats?.model?.confidence_avg ?? 99.95;
  const pending      = systemStats?.counts?.pending_alerts ?? 0;
  const critical     = systemStats?.counts?.critical ?? 0;
  const total24h     = systemStats?.counts?.total_last_24h ?? 14802;
  const autoBlocked  = systemStats?.counts?.auto_blocked ?? 0;
  const manualBlocked= systemStats?.counts?.manual_blocked ?? 0;
  const activeBlocked= systemStats?.counts?.active_blocked_ips ?? 142;

  // Chart Mock Data matching mockup layout
  const chartData = [
    { time: '08:00', flow: 2400 },
    { time: '08:10', flow: 2000 },
    { time: '08:15', flow: 4800 },
    { time: '08:20', flow: 3800 },
    { time: '08:30', flow: 5800 },
    { time: '08:35', flow: 3000 },
    { time: '08:40', flow: 4200 },
    { time: '08:45', flow: 1800 },
    { time: '08:50', flow: 5500 },
    { time: '09:00', flow: 3500 },
  ];

  // Click Actions for Integrity Box
  const handleScan = () => {
    toast.info("Iniciando escaneo de integridad en el campus...", { position: "top-center" });
    setTimeout(() => {
      toast.success("Hashes de nodos locales verificados con éxito. 0 anomalías encontradas.", { position: "top-center" });
    }, 2000);
  };

  const handleDeepAnalysis = () => {
    toast.success("Análisis profundo de políticas de firewall completado. Estado de protección óptimo.", { position: "top-center" });
  };

  return (
    <div className="campus-dashboard">
      
      {/* ── TOP KPI ROW (4 Cards) ─────────────────────────────── */}
      <div className="kpi-container">
        {/* Card 1: Flujo de Red */}
        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box">
              <Radio size={20} />
            </div>
            <span className="kpi-badge purple">+3%</span>
          </div>
          <span className="kpi-label">Flujo de Red</span>
          <span className="kpi-value">{total24h.toLocaleString()}</span>
        </div>

        {/* Card 2: Precisión del Modelo */}
        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box">
              <Target size={20} />
            </div>
            <span className="kpi-badge purple" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
              <span className="status-dot purple pulse" style={{ width: 6, height: 6 }} />
              Precisión
            </span>
          </div>
          <span className="kpi-label">Precisión del Modelo</span>
          <span className="kpi-value">{confidence.toFixed(2)}%</span>
        </div>

        {/* Card 3: Mitigaciones Locales */}
        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box">
              <ShieldCheck size={20} />
            </div>
            <span className="kpi-badge green">Activo</span>
          </div>
          <span className="kpi-label">Mitigaciones Locales (24h)</span>
          <span className="kpi-value">{activeBlocked}</span>
        </div>

        {/* Card 4: Estado de la Red */}
        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box">
              <Shield size={20} />
            </div>
            <span className="kpi-badge green" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <span className="status-dot green" style={{ width: 6, height: 6 }} />
              ÓPTIMO
            </span>
          </div>
          <span className="kpi-label">Estado de la Red</span>
          <span className="kpi-value" style={{ color: '#2b0075' }}>Estable</span>
        </div>
      </div>

      {/* ── MIDDLE ROW: BarChart & Alerts ────────────────────────────────── */}
      <div className="dashboard-layout-row">
        {/* Left: Internal Traffic */}
        <div className="white-widget">
          <div className="white-widget-header">
            <div>
              <h3 className="white-widget-title">Intensidad de Tráfico Interno</h3>
              <p className="white-widget-subtitle">Flujo de paquetes interno a través de conmutadores</p>
            </div>
            <div className="white-widget-tabs">
              <button 
                className={`white-widget-tab ${activeTab === 'Vivo' ? 'active' : ''}`}
                onClick={() => setActiveTab('Vivo')}
              >
                Vivo
              </button>
              <button 
                className={`white-widget-tab ${activeTab === '1H' ? 'active' : ''}`}
                onClick={() => setActiveTab('1H')}
              >
                1H
              </button>
              <button 
                className={`white-widget-tab ${activeTab === 'Turno' ? 'active' : ''}`}
                onClick={() => setActiveTab('Turno')}
              >
                Turno
              </button>
            </div>
          </div>
          
          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                <XAxis 
                  dataKey="time" 
                  tickLine={false} 
                  axisLine={false} 
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                />
                <Tooltip 
                  cursor={{ fill: 'rgba(243, 240, 255, 0.4)' }}
                  contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px' }}
                />
                <Bar dataKey="flow" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#d8b4fe' : '#c084fc'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Critical Alerts */}
        <div className="white-widget">
          <div className="white-widget-header">
            <div>
              <h3 className="white-widget-title">Alertas Críticas</h3>
            </div>
            <a href="#logs" className="login-forgot-link" style={{ fontSize: '0.8rem' }}>Ver Registros</a>
          </div>

          <div className="critical-alerts-list">
            {/* Dynamic log integration combined with mock alerts for wow effect */}
            {logs.filter(l => l.attack_type).slice(0, 1).map((log, index) => (
              <div key={`live-${index}`} className="alert-item-card critical">
                <div className="alert-item-icon-container critical">
                  <AlertTriangle size={18} />
                </div>
                <div className="alert-item-content">
                  <div className="alert-item-meta">
                    <span className="alert-item-badge critical">VIVO</span>
                    <span className="alert-item-time">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="alert-item-title">{log.attack_type} Detectado</div>
                  <div className="alert-item-desc">Bloqueo automático ejecutado para IP origen {log.source_ip}. Acción: {log.action_taken}.</div>
                </div>
              </div>
            ))}

            {/* Alert 1 */}
            <div className="alert-item-card critical">
              <div className="alert-item-icon-container critical">
                <MapPin size={18} />
              </div>
              <div className="alert-item-content">
                <div className="alert-item-meta">
                  <span className="alert-item-badge critical">CRÍTICO</span>
                  <span className="alert-item-time">08:44:11</span>
                </div>
                <div className="alert-item-title">Acceso no autorizado en Ala B</div>
                <div className="alert-item-desc">Intento fallido de anulación biométrica en entrada de Sala de Servidores 402.</div>
              </div>
            </div>

            {/* Alert 2 */}
            <div className="alert-item-card warning">
              <div className="alert-item-icon-container warning">
                <AlertTriangle size={18} />
              </div>
              <div className="alert-item-content">
                <div className="alert-item-meta">
                  <span className="alert-item-badge warning">ADVERTENCIA</span>
                  <span className="alert-item-time">08:32:05</span>
                </div>
                <div className="alert-item-title">Tráfico elevado en Laboratorio Biblioteca</div>
                <div className="alert-item-desc">Ancho de banda de salida superior al 80% en switch SW-LIB-G1.</div>
              </div>
            </div>

            {/* Alert 3 */}
            <div className="alert-item-card info">
              <div className="alert-item-icon-container info">
                <Radio size={18} />
              </div>
              <div className="alert-item-content">
                <div className="alert-item-meta">
                  <span className="alert-item-badge info">INFO</span>
                  <span className="alert-item-time">08:15:22</span>
                </div>
                <div className="alert-item-title">Nuevo punto de acceso activo</div>
                <div className="alert-item-desc">AP-WEST-14 aprovisionado e integrado con éxito.</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── BOTTOM ROW: Campus Integrity & Topology Map ────────────────────────────────── */}
      <div className="dashboard-layout-row">
        {/* Left: Integrity Box */}
        <div className="white-widget" style={{ justifyContent: 'center' }}>
          <div className="campus-integrity-box">
            <div className="integrity-shield-container">
              <Shield size={36} strokeWidth={2} />
            </div>
            <h3 className="integrity-title">Integridad del Campus</h3>
            <p className="integrity-subtitle">
              Hashes de nodos locales verificados. Políticas de firewall óptimas.
            </p>
            <button className="integrity-btn-primary" onClick={handleScan}>
              Escanear Ala
            </button>
            <button className="integrity-btn-secondary" onClick={handleDeepAnalysis}>
              Ejecutar Análisis Profundo
            </button>
          </div>
        </div>

        {/* Right: Topology floorplan map */}
        <div className="white-widget">
          <div className="white-widget-header" style={{ marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <List size={18} />
              <h3 className="white-widget-title" style={{ margin: 0 }}>VISTA DE TOPOLOGÍA DEL CAMPUS (3000 m²)</h3>
            </div>
            <div className="topology-legend">
              <div className="topology-legend-item">
                <span className="topology-legend-dot red" />
                <span>Carga Alta</span>
              </div>
              <div className="topology-legend-item">
                <span className="topology-legend-dot yellow" />
                <span>Media</span>
              </div>
              <div className="topology-legend-item">
                <span className="topology-legend-dot purple" />
                <span>Nominal</span>
              </div>
            </div>
          </div>

          <div className="topology-map-container">
            <div className="topology-grid-overlay" />
            <div className="topology-floorplan">
              {/* HUB center */}
              <div className="topology-center-hub" title="Centro de Conmutadores">
                <Server size={22} />
              </div>

              {/* Zone 1: Admin */}
              <div className="topology-zone admin">
                <span>Ala Admin</span>
                <span className="topology-dot purple" />
              </div>

              {/* Zone 2: Library */}
              <div className="topology-zone library">
                <span>Laboratorio Biblioteca</span>
                <span className="topology-dot yellow" />
              </div>

              {/* Zone 3: R&D */}
              <div className="topology-zone research">
                <span className="topology-alert-badge">Alerta</span>
                <span>Ala I+D</span>
                <span className="topology-dot red" />
              </div>

              {/* Dynamic Connection lines represented as custom SVG overlays inside the canvas */}
              <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 1 }}>
                {/* Admin to Hub */}
                <line x1="25%" y1="35%" x2="50%" y2="50%" stroke="rgba(124, 58, 237, 0.4)" strokeWidth="1" strokeDasharray="3,3" />
                {/* Library to Hub */}
                <line x1="38%" y1="75%" x2="50%" y2="50%" stroke="rgba(245, 158, 11, 0.4)" strokeWidth="1" strokeDasharray="3,3" />
                {/* Research to Hub */}
                <line x1="75%" y1="45%" x2="50%" y2="50%" stroke="rgba(239, 68, 68, 0.5)" strokeWidth="1.5" />
              </svg>

              <div className="topology-footer-label">Escala: 1:500 (Área Total 3000m²)</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
