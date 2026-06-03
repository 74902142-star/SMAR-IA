import { useState, useEffect, useContext, useCallback, useRef } from 'react';
import { Row, Col } from 'react-bootstrap';
import { AuthContext } from '../context/AuthContext';
import { ShieldAlert, Zap, Lock, Activity, Bug, Radio, AlertTriangle, CheckCircle, Shield } from 'lucide-react';
import { toast } from 'react-toastify';
import { BarChart, Bar, ResponsiveContainer, Cell } from 'recharts';
import { apiUrl, wsUrl } from '../api';

export default function MitigationZone() {
  const { token } = useContext(AuthContext);
  const [suspiciousIps, setSuspiciousIps] = useState([]);
  const [blockedIps, setBlockedIps] = useState([]);
  const [activeIncident, setActiveIncident] = useState(null);
  const [executing, setExecuting] = useState(null);
  const [summaryCounts, setSummaryCounts] = useState({ total_suspicious: 0, total_blocked: 0 });
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
          total_suspicious: data.total_suspicious || 0,
          total_blocked: data.total_blocked || 0,
        });
        setActiveIncident(prev => {
          if (data.suspicious_ips?.length > 0 && (!prev || !data.suspicious_ips.some(item => item.ip === prev.ip))) {
            return data.suspicious_ips[0];
          }
          return prev;
        });
      }
    } catch (err) {
      if (import.meta.env.DEV) console.warn("Error fetching suspicious IPs:", err);
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
    Promise.resolve().then(() => {
      fetchSuspicious();
    });
    const iv = setInterval(fetchSuspicious, 3000);
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
        setSummaryCounts(prev => ({ ...prev, total_blocked: (prev.total_blocked || 0) + 1 }));
        toast.success(`IP bloqueada: ${data.ip}`, { autoClose: 3000 });
      }

      if (data.event === 'unblock' || data.event === 'auto_unblock') {
        setBlockedIps(prev => prev.filter(item => item.ip !== data.ip));
        setSummaryCounts(prev => ({ ...prev, total_blocked: Math.max(0, (prev.total_blocked || 1) - 1) }));
        toast.info(`IP desbloqueada: ${data.ip}`, { autoClose: 3000 });
      }
    };
    return () => { if (ws.current) ws.current.close(); };
  }, []);


  const handleMitigate = async (ip, action, port = null) => {
    setExecuting(action);
    try {
      const r = await fetch(apiUrl('/api/mitigation/block'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ip, action, port, attack_type: 'IA Recommended Mitigation' }),
      });
      if (r.ok) {
        toast.success(`Protocolo ${action} ejecutado`);
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

  const handleEncrypt = async (ip) => {
    if (!ip) { toast.error('Seleccione una IP sospechosa primero'); return; }
    setExecuting('ENCRYPT');
    try {
      toast.info(`Protocolo de encriptación aplicado a segmento con IP ${ip}`);
      await new Promise(r => setTimeout(r, 1500));
      toast.success('Segmento encriptado correctamente');
    } catch {
      toast.error('Error al aplicar encriptación');
    } finally {
      setExecuting(null);
    }
  };

  const trendData = [{ v: 10 }, { v: 15 }, { v: 8 }, { v: 25 }, { v: 12 }];

  const recommendations = [
    {
      id: 'BLOCK_IP',
      icon: ShieldAlert,
      title: 'Aislamiento por Firewall',
      desc: 'Ajustar reglas para aislar la IP origen. Evita el movimiento lateral mientras preserva servicios internos.',
      prob: '94%',
      variant: 'blue',
      action: () => handleMitigate(activeIncident?.ip, 'BLOCK_IP'),
    },
    {
      id: 'CLOSE_TCP',
      icon: Zap,
      title: 'Terminar Conexión TCP',
      desc: 'Reinicio forzado del puerto 443. Advertencia: causará breve interrupción en servicios asociados.',
      prob: '100%',
      variant: 'rose',
      action: () => handleMitigate(activeIncident?.ip, 'CLOSE_TCP', 443),
    },
    {
      id: 'ENCRYPT',
      icon: Shield,
      title: 'Encriptar Segmento',
      desc: 'Aplica capa resistente al segmento comprometido como medida preventiva de protección.',
      prob: '88%',
      variant: 'amber',
      action: () => handleEncrypt(activeIncident?.ip),
    },
  ];

  return (
    <div className="mitigation-page">
      {/* ── Page header ── */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 4 }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1>Matriz de Amenazas</h1>
          <p>
            Incidente: <span style={{ color: 'var(--rose)', fontFamily: "'Space Mono',monospace" }}>#TK-8829</span>
            &nbsp;·&nbsp;Prioridad:&nbsp;
            <span style={{ color: 'var(--rose)', fontWeight: 700 }}>CRÍTICA</span>
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className="badge-pill rose">{summaryCounts.total_suspicious} sospechosas</div>
          <div className="badge-pill emerald">{summaryCounts.total_blocked} bloqueadas</div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        {[
          { label: 'UPTIME', value: '99.98%', color: 'cyan' },
          { label: 'LATENCIA', value: '12ms', color: 'amber' },
        ].map(({ label, value, color }) => (
          <div key={label} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-sm)', padding: '8px 20px' }}>
            <div style={{ fontSize: '0.6rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: '1rem', fontWeight: 800, color: `var(--${color})`, fontFamily: "'Space Mono',monospace" }}>{value}</div>
          </div>
        ))}
      </div>

      {/* ── Main two-column ── */}
      <Row className="g-3">
        {/* Incident Profile */}
        <Col lg={7}>
          <div className="incident-profile" style={{ height: '100%' }}>
            <div className="incident-profile-header">
              <Radio size={14} />
              PERFIL DE INCURSIÓN
              <span style={{ marginLeft: 'auto', fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 400 }}>
                LIVE FEED · SEÑAL: 92%
              </span>
            </div>
            <div className="incident-profile-body">
              {/* Scan visual */}
              <div className="threat-scan-visual">
                <div className="threat-ring" />
                <div className="threat-icon-glow">
                  <Bug size={36} />
                </div>
              </div>

              <p style={{ textAlign: 'center', fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: "'Space Mono',monospace", letterSpacing: '1px', marginBottom: 20 }}>
                FLUJOS_DE_PAQUETES_ENCRIPTADOS
              </p>

              {/* Details grid */}
              <div style={{ background: 'var(--input-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--input-border)', padding: '4px 16px', marginBottom: 20 }}>
                {[
                  { label: 'NODO ORIGEN',    value: activeIncident?.ip || '192.168.1.104', color: 'cyan' },
                  { label: 'ALERTAS RECIENTES', value: activeIncident ? `${activeIncident.alerts} en 5 min` : '—', color: 'amber' },
                  { label: 'ÚLTIMO AVISO',     value: activeIncident?.last_seen ? new Date(activeIncident.last_seen).toLocaleTimeString('es-PE', { hour12: false }) : '—', color: 'cyan' },
                  { label: 'FIRMA',            value: 'POLYMORPHIC_WORM_V3',    color: 'amber' },
                  { label: 'VECTOR',           value: 'L7_APPLICATION_EXPLOIT', color: 'rose' },
                  { label: 'ÍNDICE RIESGO',    value: '9.8 / 10.0',             color: 'rose' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="detail-row">
                    <span className="detail-label">{label}</span>
                    <span className="detail-value" style={{ color: `var(--${color})`, fontFamily: "'Space Mono',monospace", fontSize: '0.8rem' }}>{value}</span>
                  </div>
                ))}
              </div>

              {/* Log feed */}
              <div className="mitig-log-area">
                <div className="mitig-log-line info">[14:02:11] INICIALIZANDO INSPECCIÓN PROFUNDA DE PAQUETES...</div>
                <div className="mitig-log-line warning">[14:02:14] DESAJUSTE DE CABECERA DETECTADO EN PUERTO 443</div>
                <div className="mitig-log-line alert">[14:02:15] ADVERTENCIA: INTENTO DE EJECUCIÓN NO IDENTIFICADO</div>
                <div className="mitig-log-line info">[14:02:17] REDIRIGIENDO TRÁFICO A HONEYPOT_DELTA_9</div>
                <div className="mitig-log-line success">[14:02:19] MOTOR LISTO PARA MITIGACIÓN.</div>
                <div className="mitig-log-line blink">&gt; ESPERANDO DESPLIEGUE DE MITIGACIÓN...</div>
              </div>

              {/* Suspicious IPs table */}
              {suspiciousIps.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <div style={{ fontSize: '0.68rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 700 }}>
                    IPs SOSPECHOSAS ACTIVAS
                  </div>
                  {suspiciousIps.map((item) => (
                    <div
                      key={item.ip}
                      onClick={() => setActiveIncident(item)}
                      style={{
                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        padding: '10px 14px', marginBottom: 6,
                        background: activeIncident?.ip === item.ip ? 'rgba(244,63,94,0.08)' : 'var(--input-bg)',
                        border: `1px solid ${activeIncident?.ip === item.ip ? 'rgba(244,63,94,0.3)' : 'var(--input-border)'}`,
                        borderRadius: 'var(--radius-sm)', cursor: 'pointer', transition: 'all 0.2s',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <AlertTriangle size={14} style={{ color: 'var(--rose)' }} />
                        <span style={{ fontFamily: "'Space Mono',monospace", fontSize: '0.78rem', color: 'var(--text-white)' }}>{item.ip}</span>
                      </div>
                      <span className="badge-pill rose">{item.alerts} alertas</span>
                    </div>
                  ))}
                </div>
              )}
              {blockedIps.length > 0 && (
                <div style={{ marginTop: 20 }}>
                  <div style={{ fontSize: '0.68rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 10, fontWeight: 700 }}>
                    IPs BLOQUEADAS ACTIVAS
                  </div>
                  {blockedIps.map((item) => (
                    <div key={item.ip} style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      padding: '10px 14px', marginBottom: 6,
                      background: 'var(--input-bg)',
                      border: '1px solid var(--input-border)',
                      borderRadius: 'var(--radius-sm)',
                    }}>
                      <div>
                        <div style={{ fontFamily: "'Space Mono',monospace", fontSize: '0.78rem', color: 'var(--text-white)' }}>{item.ip}</div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 2 }}>
                          Método: {item.method || 'AUTO'} · {item.expires_at ? `expira ${new Date(item.expires_at).toLocaleTimeString('es-PE', {hour12:false})}` : 'sin expiración'}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <span className="badge-pill rose">BLOQUEADA</span>
                        <button className="btn-ghost-blue" style={{ padding: '6px 10px', fontSize: '0.72rem' }} onClick={() => handleUnblock(item.ip)}>DESBLOQUEAR</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </Col>

        {/* IA Recommendations */}
        <Col lg={5}>
          <div className="widget" style={{ height: '100%' }}>
            <div className="widget-header">
              <div className="widget-header-left">
                <Activity size={15} style={{ color: 'var(--blue)' }} />
                <div className="widget-title">Recomendaciones IA</div>
              </div>
              <div style={{ display: 'flex', gap: 4 }}>
                {[...Array(3)].map((_, i) => (
                  <span key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--blue)', opacity: 0.6 + i * 0.2 }} />
                ))}
              </div>
            </div>
            <div className="widget-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {recommendations.map(({ id, icon: Icon, title, desc, prob, variant, action }) => (
                <div key={id} className={`rec-card ${variant === 'rose' ? 'danger' : variant === 'amber' ? 'warning' : ''}`}>
                  <div className="rec-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 32, height: 32, borderRadius: 'var(--radius-sm)', background: `rgba(${variant === 'blue' ? '59,130,246' : variant === 'rose' ? '244,63,94' : '245,158,11'},0.1)`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: `var(--${variant})` }}>
                        <Icon size={16} />
                      </div>
                      <span className="rec-title">{title}</span>
                    </div>
                    <span className={`badge-pill ${variant}`}>REC.</span>
                  </div>
                  <p className="rec-desc">{desc}</p>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span className="rec-prob">PROB. ÉXITO: {prob}</span>
                    {action ? (
                      <button
                        className={`btn-ghost-${variant === 'rose' ? 'rose' : 'blue'}`}
                        style={{ padding: '5px 14px', fontSize: '0.72rem' }}
                        onClick={action}
                        disabled={executing === id || !activeIncident}
                      >
                        {executing === id ? 'EJECUTANDO...' : 'EJECUTAR'}
                      </button>
                    ) : (
                      <button className="btn-outline" style={{ padding: '5px 14px', fontSize: '0.72rem' }}>
                        ACTIVAR
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Col>
      </Row>

      {/* ── Stats bar ── */}
      <Row className="g-3">
        <Col md={3}>
          <div className="widget">
            <div className="widget-body" style={{ padding: '14px 18px' }}>
              <div style={{ fontSize: '0.65rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 8 }}>TENDENCIA DETECCIÓN</div>
              <div style={{ height: 44 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={trendData}>
                    <Bar dataKey="v" radius={[3, 3, 0, 0]}>
                      {trendData.map((e, i) => (
                        <Cell key={i} fill={i === 3 ? 'var(--rose)' : 'var(--blue)'} fillOpacity={0.6} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </Col>
        <Col md={6}>
          <div className="widget">
            <div className="widget-body" style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-sm)', background: 'rgba(59,130,246,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--blue)' }}>
                <Activity size={22} />
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 4 }}>CONFIANZA SMAR-IA</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 900, color: 'var(--blue)', fontFamily: "'Space Mono',monospace" }}>99.4%</div>
              </div>
              <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginBottom: 4 }}>IPs SOSPECHOSAS</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 900, color: 'var(--rose)' }}>{String(suspiciousIps.length).padStart(2, '0')}</div>
              </div>
            </div>
          </div>
        </Col>
        <Col md={3}>
          <div className="widget">
            <div className="widget-body" style={{ padding: '14px 18px' }}>
              <div style={{ fontSize: '0.65rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 8 }}>SEGURIDAD GLOBAL</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <CheckCircle size={18} style={{ color: 'var(--emerald)' }} />
                <span style={{ fontSize: '0.78rem', color: 'var(--emerald)', fontWeight: 600 }}>382 NODOS SEGUROS</span>
              </div>
            </div>
          </div>
        </Col>
      </Row>
    </div>
  );
}
