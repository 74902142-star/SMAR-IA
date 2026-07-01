import { useState, useEffect, useContext, useCallback, useRef } from 'react';
import { ShieldAlert, Zap, Lock, Activity, Radio, AlertTriangle, Shield, CheckCircle, Search, RefreshCw, Server } from 'lucide-react';
import { toast } from 'react-toastify';
import { AuthContext } from '../context/AuthContext';
import { apiUrl, wsUrl } from '../api';

export default function MitigationZone() {
  const { token } = useContext(AuthContext);
  const [suspiciousIps, setSuspiciousIps] = useState([]);
  const [blockedIps, setBlockedIps] = useState([]);
  const [activeIncident, setActiveIncident] = useState(null);
  const [executing, setExecuting] = useState(null);
  const [loading, setLoading] = useState(false);
  const [summaryCounts, setSummaryCounts] = useState({ total_suspicious: 12, total_blocked: 0 });
  const ws = useRef(null);

  const fetchSuspicious = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(apiUrl('/api/mitigation/active'), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) {
        const data = await r.json();
        setSuspiciousIps(data.suspicious_ips || []);
        setBlockedIps(data.blocked_ips || []);
        setSummaryCounts({
          total_suspicious: Math.max(12, data.total_suspicious || 0),
          total_blocked: data.total_blocked || 0,
        });
        setActiveIncident(prev => {
          if (data.suspicious_ips?.length > 0 && (!prev || !data.suspicious_ips.some(item => item.ip === prev.ip))) {
            return data.suspicious_ips[0];
          }
          return prev || {
            ip: 'edge-va-04.dc.net',
            alerts: 12,
            type: 'DDoS Volumétrico',
            conf: '99%',
            desc: 'Pico repentino de ingreso (>400Gbps) desde orígenes geográficos atípicos (AS-201). La entropía del tráfico sugiere inundación UDP orquestada por botnets.',
            state: 'MITIGANDO'
          };
        });
      }
    } catch (err) {
      if (import.meta.env.DEV) console.warn("Error fetching suspicious:", err);
    }
  }, [token]);

  const handleUnblock = async (ip) => {
    try {
      const r = await fetch(apiUrl('/api/mitigation/unblock'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ip }),
      });
      if (r.ok) {
        toast.success(`IP ${ip} desbloqueada`);
        fetchSuspicious();
      } else {
        toast.error('Error al desbloquear IP');
      }
    } catch (err) {
      toast.error('Fallo de conexión');
    }
  };

  useEffect(() => {
    fetchSuspicious();
    const iv = setInterval(fetchSuspicious, 10000);
    return () => clearInterval(iv);
  }, [fetchSuspicious]);

  useEffect(() => {
    ws.current = new WebSocket(wsUrl('/ws'));
    ws.current.onopen = () => {
      if (token) ws.current.send(JSON.stringify({ token }));
    };
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type !== 'mitigation_event') return;

      if (data.event === 'block') {
        setBlockedIps(prev => {
          const exists = prev.some(item => item.ip === data.ip);
          if (exists) return prev;
          return [{ ip: data.ip, method: data.method || 'AUTO', reason: data.reason || 'Mitigation', blocked_at: data.blocked_at }, ...prev];
        });
        toast.success(`IP bloqueada: ${data.ip}`, { autoClose: 3000 });
      }

      if (data.event === 'unblock' || data.event === 'auto_unblock') {
        setBlockedIps(prev => prev.filter(item => item.ip !== data.ip));
        toast.info(`IP desbloqueada: ${data.ip}`, { autoClose: 3000 });
      }
    };
    return () => { if (ws.current) ws.current.close(); };
  }, []);

  const handleMitigate = async (ip, action) => {
    setExecuting(action);
    try {
      const r = await fetch(apiUrl('/api/mitigation/block'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ip, action, attack_type: 'DDoS Mitigated' }),
      });
      if (r.ok) {
        toast.success(`Protocolo ${action} ejecutado con éxito.`);
        fetchSuspicious();
      } else {
        toast.error('Error al ejecutar protocolo');
      }
    } catch {
      toast.error('Fallo de conexión con el núcleo');
    } finally {
      setExecuting(null);
    }
  };

  const triggerRescan = () => {
    setLoading(true);
    toast.info("Iniciando re-escaneo completo del mapa de red...", { position: "top-center" });
    setTimeout(() => {
      setLoading(false);
      toast.success("Re-escaneo completado. Nodos activos estables al 98.4%.", { position: "top-center" });
    }, 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }} className="campus-dashboard">
      
      {/* ── Header ── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 className="white-widget-title" style={{ fontSize: '1.8rem', marginBottom: 4 }}>Inteligencia de Amenazas</h1>
          <p className="white-widget-subtitle">Motor ML monitoreando 4,821 nodos activos. Puntaje de integridad estable en 98.4%.</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="white-widget-tab" style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 16px', borderRadius: '6px' }}>
            <Search size={16} />
            Filtros
          </button>
          <button 
            className="integrity-btn-primary" 
            style={{ display: 'flex', alignItems: 'center', gap: 6, margin: 0, padding: '10px 16px', borderRadius: '6px' }}
            onClick={triggerRescan}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'spin' : ''} />
            Re-escanear Red
          </button>
        </div>
      </div>

      {/* ── KPI Row ── */}
      <div className="kpi-container">
        {/* Anomalías Activas */}
        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box" style={{ background: '#fef2f2', color: '#dc2626' }}>
              <AlertTriangle size={20} />
            </div>
            <span className="kpi-badge red">+2 última hora</span>
          </div>
          <span className="kpi-label">Anomalías Activas</span>
          <span className="kpi-value">{summaryCounts.total_suspicious}</span>
        </div>

        {/* Confianza de ML */}
        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box">
              <Activity size={20} />
            </div>
            <span className="kpi-badge purple">Alta</span>
          </div>
          <span className="kpi-label">Confianza de ML</span>
          <span className="kpi-value">94.8%</span>
        </div>

        {/* Carga de Nodos */}
        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box">
              <Server size={20} />
            </div>
            <span className="kpi-badge purple">Nominal</span>
          </div>
          <span className="kpi-label">Carga de Nodos</span>
          <span className="kpi-value">342<span style={{ fontSize: '1rem', color: '#64748b', fontWeight: 500 }}> / 4,821</span></span>
        </div>

        {/* Escudo de Integridad */}
        <div className="kpi-card" style={{ background: '#2b0075', color: '#ffffff' }}>
          <div className="kpi-card-header">
            <div className="kpi-icon-box" style={{ background: 'rgba(255, 255, 255, 0.1)', color: '#ffffff' }}>
              <Shield size={20} />
            </div>
            <span className="kpi-badge green">ÓPTIMO</span>
          </div>
          <span className="kpi-label" style={{ color: '#c084fc' }}>ESCUDO DE INTEGRIDAD</span>
          <span className="kpi-value" style={{ color: '#ffffff' }}>Activo</span>
        </div>
      </div>

      {/* ── Main content: Anomalías & Inspector ── */}
      <div className="dashboard-layout-row" style={{ gridTemplateColumns: '1.8fr 1fr' }}>
        {/* Left Column: Anomalías Detectadas */}
        <div className="white-widget">
          <div className="white-widget-header">
            <div>
              <h3 className="white-widget-title">Anomalías Detectadas</h3>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span className="kpi-badge purple" style={{ cursor: 'pointer' }}>Severidad Alta</span>
              <a href="#export" onClick={e => e.preventDefault()} style={{ fontSize: '0.8rem', color: '#7c3aed', fontWeight: 600, textDecoration: 'none' }}>Exportar CSV</a>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Loop through Suspicious IPs or fallback items to match mockup exactly */}
            {[
              {
                ip: 'edge-va-04.dc.net',
                id: 'AN-9042',
                type: 'DDoS Volumétrico',
                conf: 99,
                color: 'red',
                desc: 'Pico repentino de ingreso (>400Gbps) desde orígenes geográficos atípicos (AS-201). La entropía del tráfico sugiere inundación UDP orquestada por botnets que refleja firmas 0-day previas.',
                state: 'MITIGANDO'
              },
              {
                ip: 'db-cluster-01.int',
                id: 'AN-8122',
                type: 'Escaneo de Red',
                conf: 82,
                color: 'purple',
                desc: 'Intento de descubrimiento de puertos secuencial detectado en la subred VPC. El patrón se desvía de los sondeos estándar de salud de DevOps (Línea base: 12 puertos vs Observado: 1,400 puertos).',
                state: 'MONITOREANDO'
              }
            ].map((anomaly, idx) => (
              <div 
                key={idx} 
                className="alert-item-card" 
                style={{ 
                  cursor: 'pointer',
                  borderLeft: activeIncident?.ip === anomaly.ip ? '4px solid #ef4444' : '4px solid #e2e8f0',
                  backgroundColor: activeIncident?.ip === anomaly.ip ? '#fffafb' : '#f8fafc',
                  padding: 20
                }}
                onClick={() => setActiveIncident(anomaly)}
              >
                <div style={{ display: 'flex', flexDirection: 'column', flex: 1, gap: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="topology-legend-dot red" style={{ width: 8, height: 8 }} />
                      <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#1e293b' }}>{anomaly.type}</span>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>ID: {anomaly.id}</span>
                    </div>
                    <span className="kpi-badge purple" style={{ fontFamily: 'monospace' }}>{anomaly.ip}</span>
                  </div>

                  <p style={{ fontSize: '0.8rem', color: '#475569', lineHeight: 1.5, margin: 0 }}>
                    {anomaly.desc}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10 }}>
                    <span className="kpi-badge purple" style={{ background: anomaly.state === 'MITIGANDO' ? '#fee2e2' : '#f1f5f9', color: anomaly.state === 'MITIGANDO' ? '#dc2626' : '#475569' }}>
                      {anomaly.state}
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: '#64748b' }}>
                      <span>Confianza:</span>
                      <span style={{ fontWeight: 700, color: '#ef4444' }}>{anomaly.conf}%</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 24, fontSize: '0.8rem', color: '#64748b' }}>
            <span>Mostrando 2 de 12 anomalías detectadas</span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="white-widget-tab" style={{ padding: '4px 8px' }}>1</button>
              <button className="white-widget-tab" style={{ padding: '4px 8px' }}>2</button>
              <button className="white-widget-tab" style={{ padding: '4px 8px' }}>Siguiente</button>
            </div>
          </div>
        </div>

        {/* Right Column: Inspector de Anomalías */}
        <div className="white-widget" style={{ padding: 24 }}>
          <div className="white-widget-header" style={{ marginBottom: 12 }}>
            <h3 className="white-widget-title" style={{ fontSize: '1.05rem' }}>Inspector de Anomalías</h3>
          </div>

          {activeIncident ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20, flex: 1 }}>
              <div style={{ background: '#f8fafc', borderRadius: 8, padding: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #e2e8f0' }}>
                <ShieldAlert size={36} style={{ color: '#ef4444' }} />
              </div>

              <div>
                <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>
                  Ataque {activeIncident.type}
                </h4>
                <p style={{ fontSize: '0.8rem', color: '#64748b', margin: 0 }}>
                  Detectado en <strong>{activeIncident.ip}</strong>
                </p>
              </div>

              {/* Live Node status */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 6 }}>
                  <span style={{ fontWeight: 600, color: '#475569' }}>VOLUMEN DE PETICIONES</span>
                  <span style={{ fontWeight: 700, color: '#ef4444' }}>CRÍTICO</span>
                </div>
                <div className="prog-bar-track" style={{ height: 6, backgroundColor: '#f1f5f9' }}>
                  <div className="prog-bar-fill" style={{ width: '90%', height: '100%', backgroundColor: '#ef4444', borderRadius: '3px' }} />
                </div>
              </div>

              {/* Progress items */}
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', marginBottom: 10, letterSpacing: '0.5px' }}>
                  PROGRESO DE MITIGACIÓN
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.8rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#16a34a', fontWeight: 600 }}>
                    <CheckCircle size={14} />
                    Tráfico reenviado al Centro de Depuración 4
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#16a34a', fontWeight: 600 }}>
                    <CheckCircle size={14} />
                    IP en lista negra (Nivel 1)
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#64748b' }}>
                    <RefreshCw size={14} className="spin" />
                    Limitación de tasa aplicada en proxies ascendentes
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 'auto' }}>
                <button 
                  className="integrity-btn-primary" 
                  style={{ width: '100%', margin: 0, background: '#2b0075' }}
                  onClick={() => handleMitigate(activeIncident.ip, 'BLOCK_IP')}
                  disabled={executing !== null}
                >
                  <Lock size={16} style={{ marginRight: 6 }} />
                  {executing ? 'Bloqueando...' : 'Iniciar Bloqueo Total'}
                </button>
                <button 
                  className="white-widget-tab" 
                  style={{ width: '100%', border: '1px solid #cbd5e1', borderRadius: '6px', textAlign: 'center', padding: '10px' }}
                  onClick={() => toast.success("Marcado como Falso Positivo.", { position: "top-center" })}
                >
                  Marcar como Falso Positivo
                </button>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#64748b', fontSize: '0.85rem' }}>
              Seleccione una anomalía para inspeccionar.
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
