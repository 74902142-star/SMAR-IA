import { useState, useEffect, useContext } from 'react';
import { Clock, Download, Cpu, Server, ArrowUpRight, ShieldAlert, RefreshCw } from 'lucide-react';
import { toast } from 'react-toastify';
import { AuthContext } from '../context/AuthContext';
import { apiUrl } from '../api';

export default function TrafficMonitor() {
  const { token } = useContext(AuthContext);
  const [logs, setLogs] = useState([]);
  const [activeThreats, setActiveThreats] = useState({ pending_alerts: [], top_sources: [], blocked_ips: [] });
  const [loading, setLoading] = useState(false);

  /* ── Stats ── */
  useEffect(() => {
    const fetch_ = async () => {
      try {
        const activeRes = await fetch(apiUrl('/api/stats/active-threats'));
        const activeData = activeRes.ok ? await activeRes.json() : null;
        if (activeData) {
          setActiveThreats(activeData);
        }
      } catch (err) {
        if (import.meta.env.DEV) console.warn('TrafficMonitor stats error', err);
      }
    };
    fetch_();
    const iv = setInterval(fetch_, 15000);
    return () => clearInterval(iv);
  }, []);

  /* ── Initial log fetch ── */
  useEffect(() => {
    fetch(apiUrl('/api/logs?limit=15'))
      .then(r => r.ok ? r.json() : [])
      .then(data => setLogs(data))
      .catch(()=>{});
  }, []);

  const handleRetrain = () => {
    setLoading(true);
    toast.info("Iniciando reentrenamiento del modelo con datos de tráfico recientes...", { position: "top-center" });
    setTimeout(() => {
      setLoading(false);
      toast.success("Reentrenamiento completado. Precisión del modelo actualizada a 98.4%", { position: "top-center" });
    }, 2500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }} className="campus-dashboard">
      
      {/* ── Header Row ── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 className="white-widget-title" style={{ fontSize: '1.8rem', marginBottom: 4 }}>Análisis de Tráfico</h1>
          <p className="white-widget-subtitle">Inspección de flujos SDN y telemetría topológica en tiempo real.</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="white-widget-tab active" style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 16px', borderRadius: '6px' }}>
            <Clock size={16} />
            Últimas 24 Horas
          </button>
          <button className="integrity-btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 6, margin: 0, padding: '10px 16px', borderRadius: '6px' }}>
            <Download size={16} />
            Exportar Informe
          </button>
        </div>
      </div>

      {/* ── TOP SECTION: Network Topology & Top Senders ── */}
      <div className="dashboard-layout-row">
        {/* Left: Live Network Topology */}
        <div className="white-widget">
          <div className="white-widget-header">
            <div>
              <h3 className="white-widget-title">TOPOLOGÍA DE RED EN VIVO</h3>
            </div>
            <div style={{ display: 'flex', gap: 6 }}>
              <button className="white-widget-tab" style={{ padding: '4px 8px' }} title="Acercar">+</button>
              <button className="white-widget-tab" style={{ padding: '4px 8px' }} title="Alejar">-</button>
              <button className="white-widget-tab" style={{ padding: '4px 8px' }} title="Centrar">⟲</button>
            </div>
          </div>

          <div className="topology-map-container" style={{ minHeight: 300 }}>
            <div className="topology-grid-overlay" />
            <div className="topology-floorplan" style={{ minHeight: 300 }}>
              
              {/* Hub: SDN Controller */}
              <div className="topology-center-hub" style={{ border: '2px solid #7c3aed', background: '#0f172a' }}>
                <Cpu size={24} style={{ color: '#a78bfa' }} />
              </div>
              <div style={{ position: 'absolute', top: '60%', left: '50%', transform: 'translate(-50%, -50%)', color: '#94a3b8', fontSize: '0.6rem', fontWeight: 'bold' }}>
                CONTROLADOR SDN
              </div>

              {/* Node 1: DC-EAST-01 */}
              <div style={{ position: 'absolute', left: '20%', top: '50%', transform: 'translateY(-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                <Server size={20} style={{ color: '#cbd5e1' }} />
                <span style={{ fontSize: '0.62rem', color: '#94a3b8', fontWeight: 600 }}>DC-EAST-01</span>
                <span className="topology-legend-dot purple" style={{ width: 6, height: 6 }} />
              </div>

              {/* Node 2: DC-EAST-02 */}
              <div style={{ position: 'absolute', left: '38%', top: '70%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                <Server size={20} style={{ color: '#cbd5e1' }} />
                <span style={{ fontSize: '0.62rem', color: '#94a3b8', fontWeight: 600 }}>DC-EAST-02</span>
                <span className="topology-legend-dot purple" style={{ width: 6, height: 6 }} />
              </div>

              {/* Node 3: USR-WING-A (ATTACK ALPHA) */}
              <div style={{ position: 'absolute', right: '20%', top: '50%', transform: 'translateY(-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                <div style={{ position: 'relative' }}>
                  <Server size={22} style={{ color: '#ef4444' }} />
                  <span className="topology-alert-badge" style={{ position: 'absolute', top: -14, right: -24, scale: '0.8' }}>AMENAZA</span>
                </div>
                <span style={{ fontSize: '0.62rem', color: '#f87171', fontWeight: 700 }}>USR-WING-A</span>
                <span style={{ fontSize: '0.55rem', color: '#64748b', fontWeight: 'bold' }}>ALPHA</span>
                <span className="topology-legend-dot red" style={{ width: 6, height: 6 }} />
              </div>

              {/* SVG connection lines */}
              <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 1 }}>
                <line x1="25%" y1="50%" x2="50%" y2="50%" stroke="rgba(148, 163, 184, 0.4)" strokeWidth="1" strokeDasharray="3,3" />
                <line x1="42%" y1="70%" x2="50%" y2="50%" stroke="rgba(148, 163, 184, 0.4)" strokeWidth="1" strokeDasharray="3,3" />
                <line x1="80%" y1="50%" x2="50%" y2="50%" stroke="#ef4444" strokeWidth="1.5" />
              </svg>

              <div style={{ position: 'absolute', bottom: 12, left: 12, display: 'flex', gap: 16, fontSize: '0.7rem', color: '#64748b', fontWeight: 600 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span className="topology-legend-dot purple" /> Núcleo</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span className="topology-legend-dot yellow" /> Switch</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span className="topology-legend-dot red" /> Anómalo</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Top Senders */}
        <div className="white-widget">
          <div className="white-widget-header">
            <div>
              <h3 className="white-widget-title">Principales Emisores</h3>
            </div>
            <ArrowUpRight size={18} style={{ color: '#64748b' }} />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 20, flex: 1, justifyContent: 'center' }}>
            {[
              { ip: '10.0.42.185', rate: '4.1 GB/s', color: 'purple', pct: 85 },
              { ip: '192.168.1.55', rate: '2.8 GB/s', color: 'purple', pct: 60 },
              { ip: '45.22.10.1', rate: '1.4 GB/s (Pico Alto)', color: 'red', pct: 45 },
              { ip: '172.16.0.210', rate: '920 MB/s', color: 'purple', pct: 25 },
            ].map((sender, idx) => (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: '0.8rem' }}>
                  <span style={{ fontWeight: 700, color: '#334155' }}>{sender.ip}</span>
                  <span style={{ fontWeight: 600, color: sender.color === 'red' ? '#ef4444' : '#64748b' }}>{sender.rate}</span>
                </div>
                <div className="prog-bar-track" style={{ height: 6, backgroundColor: '#f1f5f9' }}>
                  <div 
                    className="prog-bar-fill" 
                    style={{ 
                      width: `${sender.pct}%`, 
                      height: '100%', 
                      backgroundColor: sender.color === 'red' ? '#ef4444' : '#7c3aed',
                      borderRadius: '3px'
                    }} 
                  />
                </div>
              </div>
            ))}
          </div>

          <button className="white-widget-tab" style={{ width: '100%', border: '1px solid #cbd5e1', borderRadius: '6px', marginTop: 24, textAlign: 'center', padding: '10px' }}>
            Ver Todos los Puntos Finales
          </button>
        </div>
      </div>

      {/* ── BOTTOM SECTION: Current Flows & ML Sidebar ── */}
      <div className="dashboard-layout-row">
        {/* Left: Active SDN Flows */}
        <div className="white-widget">
          <div className="white-widget-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <h3 className="white-widget-title" style={{ margin: 0 }}>Flujos SDN Actuales</h3>
              <span className="kpi-badge purple">342 Activos</span>
            </div>
            <span className="kpi-badge purple" style={{ cursor: 'pointer' }}>TCP/UDP Primario</span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>IP Origen</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>IP Destino</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Protocolo</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>VLAN</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Acción</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { src: '10.0.42.185:443', dst: '172.16.1.10:1289', proto: 'TCP', vlan: 'VLAN 100', action: 'Permitir', state: 'ACTIVO', color: 'green' },
                  { src: '45.22.10.1:9001', dst: '10.0.0.5:80', proto: 'UDP', vlan: 'VLAN 0', action: 'Bloquear (ML Trigger)', state: 'MITIGADO', color: 'red' },
                  { src: '192.168.1.55:8443', dst: '8.8.8.8:53', proto: 'UDP', vlan: 'VLAN 20', action: 'Permitir', state: 'ACTIVO', color: 'green' },
                  { src: '10.0.42.185:532', dst: '10.0.42.1:22', proto: 'TCP', vlan: 'VLAN 100', action: 'Redirigir (Honeypot)', state: 'OBSERVABLE', color: 'purple' },
                ].map((flow, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600, color: '#334155' }}>{flow.src}</td>
                    <td style={{ color: '#475569' }}>{flow.dst}</td>
                    <td>
                      <span className="badge-pill" style={{ background: '#e2e8f0', color: '#475569', fontSize: '0.65rem' }}>{flow.proto}</span>
                    </td>
                    <td style={{ color: '#64748b' }}>{flow.vlan}</td>
                    <td style={{ fontWeight: 600, color: flow.color === 'red' ? '#ef4444' : '#1e293b' }}>{flow.action}</td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontWeight: 700, fontSize: '0.72rem' }}>
                        <span className={`status-dot ${flow.color}`} style={{ width: 6, height: 6 }} />
                        <span style={{ color: flow.color === 'green' ? '#16a34a' : flow.color === 'red' ? '#dc2626' : '#7c3aed' }}>{flow.state}</span>
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 24, fontSize: '0.8rem', color: '#64748b' }}>
            <span>Mostrando 4 de 342 flujos activos</span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="white-widget-tab" style={{ padding: '4px 8px' }}>&lt;</button>
              <button className="white-widget-tab" style={{ padding: '4px 8px' }}>&gt;</button>
            </div>
          </div>
        </div>

        {/* Right: ML Analysis Panel */}
        <div className="white-widget" style={{ gap: 16 }}>
          <div className="white-widget-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <ShieldAlert size={18} style={{ color: '#7c3aed' }} />
              <h3 className="white-widget-title" style={{ margin: 0 }}>Análisis de ML</h3>
            </div>
          </div>

          {/* Box 1 */}
          <div style={{ borderLeft: '3px solid #7c3aed', paddingLeft: 12, marginBottom: 8 }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', marginBottom: 4 }}>Alerta de Patrón de Tráfico</h4>
            <p style={{ fontSize: '0.78rem', color: '#64748b', lineHeight: 1.4, margin: 0 }}>
              Detectado aumento inesperado de tráfico UDP desde <strong>USR-WING-A</strong>. El patrón sugiere un posible intento de amplificación DNS.
            </p>
          </div>

          {/* Box 2 */}
          <div style={{ borderLeft: '3px solid #7c3aed', paddingLeft: 12, marginBottom: 8 }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', marginBottom: 4 }}>Optimización de Flujo</h4>
            <p style={{ fontSize: '0.78rem', color: '#64748b', lineHeight: 1.4, margin: 0 }}>
              Redirigiendo flujos de vídeo de alto ancho de banda a <strong>L-CORE-02</strong> para reducir la latencia en el troncal principal.
            </p>
          </div>

          {/* Box 3 */}
          <div style={{ marginTop: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 6 }}>
              <span style={{ fontWeight: 600, color: '#475569' }}>PRECISIÓN DE PREDICCIÓN</span>
              <span style={{ fontWeight: 700, color: '#7c3aed' }}>98.4%</span>
            </div>
            <div className="prog-bar-track" style={{ height: 6, backgroundColor: '#f1f5f9' }}>
              <div className="prog-bar-fill" style={{ width: '98.4%', height: '100%', backgroundColor: '#7c3aed', borderRadius: '3px' }} />
            </div>
          </div>

          <button 
            className="integrity-btn-primary" 
            style={{ width: '100%', margin: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
            onClick={handleRetrain}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'spin' : ''} />
            {loading ? 'Entrenando...' : 'Reentrenar Modelo'}
          </button>
        </div>
      </div>

    </div>
  );
}
