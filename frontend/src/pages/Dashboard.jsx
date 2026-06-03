import { useState, useEffect, useRef, useContext } from 'react';
import { Row, Col } from 'react-bootstrap';
import {
  Activity, AlertTriangle, ShieldCheck, Cpu, Server,
  Clock, Target, List
} from 'lucide-react';
import { toast } from 'react-toastify';
import { apiUrl } from '../api';
import { AuthContext } from '../context/AuthContext';

export default function Dashboard() {
  const { token } = useContext(AuthContext);
  const [logs, setLogs] = useState([]);
  const [systemStats, setSystemStats] = useState(null);
  const [livePackets, setLivePackets] = useState([]);
  const recentIpsRef = useRef({});
  const ws = useRef(null);
  const pktId = useRef(0);

  /* ── WebSocket ─────────────────────────────────────── */
  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/ws');
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
  const confidence   = systemStats?.model?.confidence_avg ?? 90;
  const pending      = systemStats?.counts?.pending_alerts ?? 0;
  const critical     = systemStats?.counts?.critical ?? 0;
  const total24h     = systemStats?.counts?.total_last_24h ?? 0;
  const autoBlocked  = systemStats?.counts?.auto_blocked ?? 0;
  const manualBlocked= systemStats?.counts?.manual_blocked ?? 0;
  const activeBlocked= systemStats?.counts?.active_blocked_ips ?? (autoBlocked + manualBlocked);
  const totalBlocked = activeBlocked;
  const systemOk     = cpu < 60;

  const circumference = 2 * Math.PI * 54;
  const dashOffset    = circumference - (confidence / 100) * circumference;

  return (
    <div className="dashboard-grid">
      {/* ── TOP KPI ROW ─────────────────────────────── */}
      <Row className="g-3">
        {[
          { label: 'ALERTAS PENDIENTES', value: String(pending).padStart(2,'0'), meta: `${critical} críticas`, accent: pending>0?'rose':'emerald', icon: AlertTriangle },
          { label: 'TOTAL ÚLTIMAS 24H',  value: total24h.toLocaleString(),    meta: 'eventos procesados', accent:'blue',  icon: Activity },
          { label: 'IPs BLOQUEADAS',     value: String(totalBlocked),          meta: `${autoBlocked} auto · ${manualBlocked} manual`, accent:'amber', icon: ShieldCheck },
          { label: 'UPTIME SISTEMA',     value: uptime,                        meta: cpu.toFixed(0)+'% CPU · '+ram.toFixed(0)+'% RAM', accent:'cyan', icon: Clock },
        ].map(({ label, value, meta, accent, icon: Icon }) => (
          <Col key={label} xs={6} xl={3}>
            <div className="stat-tile">
              <div className={`stat-tile-accent ${accent}`} />
              <div style={{paddingLeft:10}}>
                <div className="stat-tile-label">{label}</div>
                <div className={`stat-tile-value text-${accent}`}>{value}</div>
                <div className="stat-tile-meta">{meta}</div>
              </div>
              <Icon size={28} style={{position:'absolute', right:16, top:'50%', transform:'translateY(-50%)', opacity:0.08}} />
            </div>
          </Col>
        ))}
      </Row>

      {/* ── MIDDLE ROW ────────────────────────────────── */}
      <Row className="g-3">
        {/* Network Map */}
        <Col lg={8}>
          <div className="widget" style={{height:'100%'}}>
            <div className="widget-header">
              <div className="widget-header-left">
                <Activity size={16} style={{color:'var(--blue)'}} />
                <div>
                  <div className="widget-title">Tráfico de Red en Vivo</div>
                  <div className="widget-subtitle">Análisis de paquetes en tiempo real</div>
                </div>
              </div>
              <span className="badge-pill blue">
                <span className="status-dot blue pulse" />
                EN VIVO
              </span>
            </div>
            <div className="widget-body" style={{padding:0}}>
              <div className="network-canvas">
                {/* Connection lines */}
                <div className="net-line" style={{width:160, top:'50%', left:'50%', transform:'translate(-50%,-50%) rotate(-30deg)'}} />
                <div className="net-line" style={{width:160, top:'50%', left:'50%', transform:'translate(-50%,-50%) rotate(-145deg)'}} />
                <div className="net-line" style={{width:160, top:'50%', left:'50%', transform:'translate(-50%,-50%) rotate(25deg)'}} />
                <div className="net-line" style={{width:160, top:'50%', left:'50%', transform:'translate(-50%,-50%) rotate(155deg)'}} />

                {/* Satellites */}
                <div className="net-node satellite a"><Server size={14}/></div>
                <div className="net-node satellite b"><Server size={14}/></div>
                <div className="net-node satellite c"><Server size={14}/></div>
                <div className="net-node satellite d"><Server size={14}/></div>

                {/* Core */}
                <div className="net-node core"><Cpu size={22}/></div>

                {/* Dynamic packets */}
                {livePackets.map(p => (
                  <div key={p.id} className={`packet-dot ${p.type === 'burst' ? 'alert' : p.type}`} />
                ))}
              </div>

              {/* Bottom stats bar */}
              <div style={{display:'flex', gap:0, borderTop:'1px solid var(--border-subtle)'}}>
                {[
                  { label:'THROUGHPUT', value: total24h > 0 ? `${(total24h/86400*1.5).toFixed(1)} TB/S` : '0.0 TB/S' },
                  { label:'EVENTOS 24H', value: total24h.toLocaleString() },
                  { label:'ESTADO CPU',  value: cpu.toFixed(0)+'%' },
                ].map(({ label, value }) => (
                  <div key={label} style={{flex:1, padding:'14px 20px', borderRight:'1px solid var(--border-subtle)'}}>
                    <div style={{fontSize:'0.62rem', letterSpacing:'1.5px', color:'var(--text-muted)', marginBottom:4}}>{label}</div>
                    <div style={{fontSize:'1rem', fontWeight:700, color:'var(--text-white)'}}>{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Col>

        {/* Right column */}
        <Col lg={4}>
          <div style={{display:'flex', flexDirection:'column', gap:12, height:'100%'}}>
            {/* System health */}
            <div className="widget">
              <div className="widget-header">
                <div className="widget-header-left">
                  <Cpu size={15} style={{color:'var(--cyan)'}} />
                  <div className="widget-title">Estado del Sistema</div>
                </div>
                <span className={`badge-pill ${systemOk ? 'emerald' : cpu>85 ? 'rose' : 'amber'}`}>
                  {systemOk ? 'NOMINAL' : cpu > 85 ? 'CRÍTICO' : 'ELEVADO'}
                </span>
              </div>
              <div className="widget-body">
                {[
                  { label:'CPU', value: cpu, color:'blue' },
                  { label:'RAM', value: ram, color:'cyan' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="mb-3">
                    <div style={{display:'flex', justifyContent:'space-between', marginBottom:6, fontSize:'0.72rem'}}>
                      <span style={{color:'var(--text-secondary)'}}>{label}</span>
                      <span style={{fontWeight:700, fontFamily:"'Space Mono',monospace"}}>{value.toFixed(0)}%</span>
                    </div>
                    <div className="prog-bar-track">
                      <div className={`prog-bar-fill ${color}`} style={{width: `${Math.min(value,100)}%`}} />
                    </div>
                  </div>
                ))}
                <div style={{display:'flex', alignItems:'center', gap:8, marginTop:8, fontSize:'0.7rem', color:'var(--text-muted)', fontFamily:"'Space Mono',monospace"}}>
                  <Clock size={12}/> {uptime}
                </div>
              </div>
            </div>

            {/* Threats */}
            <div className="widget" style={{flex:1}}>
              <div className="widget-header">
                <div className="widget-header-left">
                  <AlertTriangle size={15} style={{color:'var(--rose)'}} />
                  <div className="widget-title">Amenazas Activas</div>
                </div>
                {(critical + pending) > 0 && <span className="badge-pill rose">{critical + pending}</span>}
              </div>
              <div className="widget-body">
                <div style={{textAlign:'center', marginBottom:16}}>
                  <span style={{fontSize:'3rem', fontWeight:900, color: (critical+pending)>0 ? 'var(--rose)':'var(--emerald)', lineHeight:1}}>
                    {String(critical+pending).padStart(2,'0')}
                  </span>
                  <div style={{fontSize:'0.7rem', letterSpacing:'2px', color:'var(--text-muted)', marginTop:4}}>
                    {critical > 0 ? 'ALERTA ALTA' : 'SIN AMENAZAS'}
                  </div>
                </div>
                <div style={{display:'flex', flexDirection:'column', gap:8}}>
                  {systemStats?.attack_distribution?.slice(0,3).map((a, i) => (
                    <div key={i} style={{display:'flex', alignItems:'center', justifyContent:'space-between', padding:'8px 10px', background:'var(--input-bg)', borderRadius:'var(--radius-sm)', fontSize:'0.72rem'}}>
                      <span style={{color:'var(--text-secondary)'}}>{a.type}</span>
                      <span className="badge-pill rose">{a.count}</span>
                    </div>
                  ))}
                  {(!systemStats?.attack_distribution?.length) && (
                    <div style={{fontSize:'0.72rem', color:'var(--text-muted)', textAlign:'center', padding:8}}>Monitoreando red...</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </Col>
      </Row>

      {/* ── BOTTOM ROW ────────────────────────────────── */}
      <Row className="g-3">
        {/* IA Confidence gauge */}
        <Col lg={4}>
          <div className="widget" style={{height:'100%'}}>
            <div className="widget-header">
              <div className="widget-header-left">
                <Target size={15} style={{color:'var(--amber)'}} />
                <div className="widget-title">Confianza de la IA</div>
              </div>
            </div>
            <div className="widget-body" style={{display:'flex', flexDirection:'column', alignItems:'center', padding:'28px 20px'}}>
              <div className="ring-gauge">
                <svg viewBox="0 0 120 120">
                  <circle className="track" cx="60" cy="60" r="54" />
                  <circle
                    className="fill"
                    cx="60" cy="60" r="54"
                    style={{strokeDashoffset: dashOffset, strokeDasharray: circumference}}
                  />
                </svg>
                <div className="ring-gauge-center">
                  <div className="ring-gauge-value">{confidence.toFixed(0)}%</div>
                  <div className="ring-gauge-label">{confidence>=90?'ÓPTIMO':confidence>=70?'BUENO':'BAJO'}</div>
                </div>
              </div>
              <p style={{marginTop:20, fontSize:'0.75rem', color:'var(--text-muted)', textAlign:'center', lineHeight:1.6}}>
                {confidence >= 90
                  ? `Modelo operando con alta confianza. ${totalBlocked} amenazas mitigadas.`
                  : confidence >= 70
                  ? 'Confianza aceptable. Se recomienda supervisión manual.'
                  : 'Confianza baja. Revisar dataset de entrenamiento.'}
              </p>
              <div style={{display:'flex', gap:20, marginTop:8}}>
                {[{label:'Auto-bloqueadas', value:autoBlocked, c:'rose'},{label:'Manual',value:manualBlocked,c:'amber'}].map(({label,value,c})=>(
                  <div key={label} style={{textAlign:'center'}}>
                    <div style={{fontSize:'1.1rem', fontWeight:800, color:`var(--${c})`}}>{value}</div>
                    <div style={{fontSize:'0.62rem', color:'var(--text-muted)'}}>{label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Col>

        {/* Live log terminal */}
        <Col lg={8}>
          <div className="widget" style={{height:'100%'}}>
            <div className="widget-header">
              <div className="widget-header-left">
                <List size={15} style={{color:'var(--blue)'}} />
                <div>
                  <div className="widget-title">Registro de Actividad</div>
                  <div className="widget-subtitle">Flujo en tiempo real</div>
                </div>
              </div>
              <div style={{display:'flex', gap:6}}>
                <span style={{width:10,height:10,borderRadius:'50%',background:'#ff5f57',display:'inline-block'}} />
                <span style={{width:10,height:10,borderRadius:'50%',background:'#febc2e',display:'inline-block'}} />
                <span style={{width:10,height:10,borderRadius:'50%',background:'#28c840',display:'inline-block'}} />
              </div>
            </div>
            <div className="widget-body" style={{padding:0}}>
              <div className="dash-terminal" style={{padding:'16px 20px'}}>
                {Array.isArray(logs) && logs.map((log, i) => (
                  <div key={i} className={`dash-log-line ${log.isLive ? 'live-fade-in' : ''}`}>
                    <span className="dash-log-time">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                    <span className={`dash-log-msg ${log.attack_type ? 'alert' : 'info'}`}>
                      {log.attack_type
                        ? `⚠ CRÍTICO: ${log.attack_type} desde ${log.source_ip}`
                        : `→ FLUJO_OK: ${log.source_ip} · ${log.action_taken}`}
                    </span>
                  </div>
                ))}
                {(!Array.isArray(logs) || !logs.length) && (
                  <div className="dash-log-line"><span className="dash-log-time">--:--:--</span><span className="dash-log-msg">Esperando transmisión de datos...</span></div>
                )}
              </div>
            </div>
          </div>
        </Col>
      </Row>
    </div>
  );
}
