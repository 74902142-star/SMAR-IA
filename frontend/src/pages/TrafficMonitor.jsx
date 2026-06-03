import { useState, useEffect, useRef, useContext } from 'react';
import { Row, Col } from 'react-bootstrap';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { ShieldAlert, Activity, Database, Search, Lock, X } from 'lucide-react';

import { toast } from 'react-toastify';
import { AuthContext } from '../context/AuthContext';
import { apiUrl, wsUrl } from '../api';

function severityOf(confidence) {
  if (confidence >= 0.90) return { level:'critical', label:'CRÍTICO',  color:'rose',  Icon: ShieldAlert };
  if (confidence >= 0.50) return { level:'warning',  label:'ADVERTENCIA', color:'amber', Icon: Database };
  return                          { level:'info',     label:'INFO',     color:'cyan',  Icon: Search };
}

export default function TrafficMonitor() {
  const { token } = useContext(AuthContext);
  const [threatCards, setThreatCards]   = useState([]);
  const [summaryStats, setSummaryStats] = useState({ critical:0, warning:0, info:0 });
  const [heatmapData, setHeatmapData]   = useState([]);
  const [activeThreats, setActiveThreats] = useState({ pending_alerts: [], top_sources: [], blocked_ips: [] });
  const [mitigStats, setMitigStats]     = useState({ shields:0, suppression:0 });
  const [detailCard, setDetailCard]     = useState(null);
  const [purging, setPurging]           = useState(false);
  const ws = useRef(null);
  const wsToken = token;

  /* ── Stats ── */
  useEffect(() => {
    const fetch_ = async () => {
      try {
        const [statsRes, activeRes] = await Promise.all([
          fetch(apiUrl('/api/stats')),
          fetch(apiUrl('/api/stats/active-threats')),
        ]);
        const statsData = statsRes.ok ? await statsRes.json() : null;
        const activeData = activeRes.ok ? await activeRes.json() : null;

        if (statsData) {
          setSummaryStats({ critical: statsData.counts?.critical||0, warning: statsData.counts?.warning||0, info: statsData.counts?.info||0 });
          if (statsData.hourly_traffic?.length > 0)
            setHeatmapData(statsData.hourly_traffic.map(h => ({ name: h.hour, val: h.count })));
          const tot = (statsData.counts?.critical||0)+(statsData.counts?.warning||0)+(statsData.counts||0);
          const blk = (statsData.counts?.auto_blocked||0)+(statsData.counts?.manual_blocked||0);
          setMitigStats({
            shields: tot > 0 ? Math.min(Math.round((blk/tot)*100),100) : 0,
            suppression: tot > 0 ? Math.min(Math.round(((tot-(statsData.counts?.pending_alerts||0))/tot)*100),100) : 0,
          });
        }

        if (activeData) {
          setActiveThreats(activeData);
        }
      } catch (err) {
        if (import.meta.env.DEV) console.warn('TrafficMonitor fetch error', err);
      }
    };
    fetch_();
    const iv = setInterval(fetch_, 15000);
    return () => clearInterval(iv);
  }, []);

  /* ── Initial threat cards ── */
  useEffect(() => {
    fetch(apiUrl('/api/logs?limit=20'))
      .then(r => r.ok ? r.json() : [])
      .then(data => {
        const attacks = data.filter(l => l.attack_type && l.attack_type !== 'Normal' && l.attack_type !== 'Unknown').slice(0,6);
        setThreatCards(attacks.map(log => {
          const conf = log.confidence || 0;
          const sev  = severityOf(conf);
          const diff = Math.floor((new Date()-new Date(log.timestamp))/60000);
          const ago  = diff < 1 ? 'AHORA' : diff < 60 ? `${diff}m` : diff < 1440 ? `${Math.floor(diff/60)}h` : `${Math.floor(diff/1440)}d`;
          return { id: log.id, ...sev, title: log.attack_type, sourceIp: log.source_ip, destIp: log.destination_ip, confidence: (conf*100).toFixed(1), ago, actionTaken: log.action_taken };
        }));
      }).catch(()=>{});
  }, []);

  /* ── WebSocket live feed ── */
  useEffect(() => {
    ws.current = new WebSocket(wsUrl('/ws'));
    ws.current.onopen = () => {
      if (token) ws.current.send(JSON.stringify({ token }));
    };
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'traffic_update') {
        if (!data.is_alert) return;
        const conf = data.confidence || 0;
        const sev  = severityOf(conf);
        const card = { id: Date.now(), ...sev, title: data.predicted_class, sourceIp: data.source_ip, destIp: data.destination_ip||'GATEWAY', confidence: (conf*100).toFixed(1), ago:'AHORA', actionTaken: data.action_taken };
        setThreatCards(prev => [card, ...prev.slice(0,5)]);
        toast.warning(`Amenaza: ${data.predicted_class} desde ${data.source_ip}`);

        if (data.event === 'block') {
          toast.success(`IP bloqueada: ${data.ip}`, { autoClose: 3000 });
        }
        if (data.event === 'unblock' || data.event === 'auto_unblock') {
          toast.info(`IP desbloqueada: ${data.ip}`, { autoClose: 3000 });
        }
      }
    };
    return () => { if (ws.current) ws.current.close(); };
  }, [token]);

  /* ── Block IP ── */
  const handleBlock = async (ip, title) => {
    try {
      const r = await fetch(apiUrl('/api/mitigation/block'), {
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},
        body: JSON.stringify({ ip, action:'BLOCK_IP', attack_type: title }),
      });
      if (r.ok) {
        toast.success(`IP ${ip} bloqueada`);
        setThreatCards(prev => prev.filter(c => c.sourceIp !== ip));
      } else {
        toast.error('Error al bloquear IP');
      }
    } catch { toast.error('Fallo de conexión'); }
  };

  /* ── Emergency purge ── */
  const handleEmergencyPurge = async () => {
    if (!window.confirm('¿Está seguro de ejecutar un PURGADO DE EMERGENCIA? Se desbloquearán TODAS las IPs y se limpiarán las alertas pendientes.')) return;
    setPurging(true);
    try {
      const unblockPromises = activeThreats.blocked_ips.map(item =>
        fetch(apiUrl('/api/mitigation/unblock'), {
          method:'POST',
          headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},
          body: JSON.stringify({ ip: item.ip }),
        })
      );
      await Promise.allSettled(unblockPromises);
      toast.success(`Purga completada: ${activeThreats.blocked_ips.length} IPs desbloqueadas`);
      setThreatCards([]);
      setActiveThreats(prev => ({ ...prev, blocked_ips: [], pending_alerts: [] }));
    } catch {
      toast.error('Error durante el purgado de emergencia');
    } finally {
      setPurging(false);
    }
  };

  const pendingCount = activeThreats.pending_alerts ? activeThreats.pending_alerts.length : activeThreats.total_pending ?? 0;
  const blockedCount = activeThreats.blocked_ips ? activeThreats.blocked_ips.length : activeThreats.total_blocked ?? 0;

  const heatmap = heatmapData.length > 0 ? heatmapData : [
    {name:'00h',val:0},{name:'03h',val:0},{name:'06h',val:0},{name:'09h',val:0},
    {name:'12h',val:0},{name:'15h',val:0},{name:'18h',val:0},{name:'21h',val:0},
  ];

  return (
    <div style={{display:'flex', flexDirection:'column', gap:24}}>
      {/* ── Header ── */}
      <div style={{display:'flex', alignItems:'flex-end', justifyContent:'space-between'}}>
        <div className="page-header" style={{marginBottom:0}}>
          <h1>Amenazas Activas</h1>
          <p>Análisis heurístico en tiempo real del tráfico externo</p>
        </div>
        <div style={{display:'flex', flexDirection:'column', gap:10}}>
          <div style={{display:'flex', gap:8}}>
            <div className="badge-pill rose">{pendingCount} alertas pendientes</div>
            <div className="badge-pill emerald">{blockedCount} IPs bloqueadas</div>
          </div>
          <div style={{display:'flex', gap:12}}>
            {[
              { label:'CRÍTICO', value: summaryStats.critical, c:'rose' },
              { label:'ADVERTENCIA', value: summaryStats.warning, c:'amber' },
              { label:'INFO', value: summaryStats.info, c:'cyan' },
            ].map(({ label, value, c }) => (
              <div key={label} style={{background:'var(--bg-card)', border:`1px solid var(--border-default)`, borderTop:`3px solid var(--${c})`, borderRadius:'var(--radius-sm)', padding:'8px 18px', textAlign:'center', minWidth:90}}>
                <div style={{fontSize:'0.6rem', letterSpacing:'1.5px', color:`var(--${c})`, marginBottom:4}}>{label}</div>
                <div style={{fontSize:'1.4rem', fontWeight:900, color:`var(--${c})`}}>{String(value).padStart(2,'0')}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Threat cards ── */}
      <div style={{display:'flex', flexDirection:'column', gap:10}}>
        {threatCards.length > 0 ? threatCards.map((card, idx) => {
          const { Icon } = card;
          return (
            <div key={card.id||idx} className={`alert-card ${card.level}`}>
              <div className={`alert-icon-box ${card.level}`}>
                <Icon size={20}/>
              </div>
              <div className="alert-body">
                <div className="alert-title">{card.title}</div>
                <div className="alert-meta">
                  ORIGEN: <span>{card.sourceIp}</span>
                  <span style={{margin:'0 12px', color:'var(--border-default)'}}>|</span>
                  DESTINO: <span>{card.destIp}</span>
                  <span style={{margin:'0 12px', color:'var(--border-default)'}}>|</span>
                  CONFIANZA: <span>{card.confidence}%</span>
                </div>
              </div>
              <div className="alert-actions-group">
                <span className="alert-time">DETECTADO {card.ago}</span>
                <span className={`badge-pill ${card.color}`}>{card.label}</span>
                <div style={{display:'flex', gap:8}}>
                  {card.actionTaken?.includes('BLOCKED') ? (
                    <span className="badge-pill emerald"><Lock size={11}/> BLOQUEADO</span>
                  ) : (
                    <button className="btn-ghost-rose" style={{padding:'5px 12px', fontSize:'0.7rem'}}
                      onClick={() => handleBlock(card.sourceIp, card.title)}>
                      BLOQUEAR
                    </button>
                  )}
                  <button className="btn-outline" style={{padding:'5px 12px', fontSize:'0.7rem'}}
                    onClick={() => setDetailCard(card)}>DETALLES</button>
                </div>
              </div>
            </div>
          );
        }) : (
          <div className="alert-card info" style={{justifyContent:'center', padding:'28px'}}>
            <div className="alert-icon-box info"><Activity size={20}/></div>
            <div className="alert-body">
              <div className="alert-title">Sin amenazas activas detectadas</div>
              <div className="alert-meta">El sistema monitorea el tráfico en tiempo real. Las alertas aparecerán aquí automáticamente.</div>
            </div>
            <span className="badge-pill emerald">NOMINAL</span>
          </div>
        )}
      </div>

      {/* ── Detail modal ── */}
      {detailCard && (
        <div className="modal-backdrop" onClick={() => setDetailCard(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <span>Detalles de Amenaza</span>
              <X size={16} onClick={() => setDetailCard(null)} style={{cursor:'pointer'}} />
            </div>
            <div className="modal-body">
              <div className="detail-row"><span className="detail-label">Tipo</span><span className="detail-value">{detailCard.title}</span></div>
              <div className="detail-row"><span className="detail-label">Origen</span><span className="detail-value">{detailCard.sourceIp}</span></div>
              <div className="detail-row"><span className="detail-label">Destino</span><span className="detail-value">{detailCard.destIp}</span></div>
              <div className="detail-row"><span className="detail-label">Confianza</span><span className="detail-value">{detailCard.confidence}%</span></div>
              <div className="detail-row"><span className="detail-label">Severidad</span><span className="detail-value">{detailCard.label}</span></div>
              <div className="detail-row"><span className="detail-label">Detectado</span><span className="detail-value">{detailCard.ago}</span></div>
              <div className="detail-row"><span className="detail-label">Acción</span><span className="detail-value">{detailCard.actionTaken || 'Pendiente'}</span></div>
            </div>
            <div className="modal-footer">
              <button className="btn-outline" onClick={() => setDetailCard(null)}>Cerrar</button>
              {!detailCard.actionTaken?.includes('BLOCKED') && (
                <button className="btn-ghost-rose" onClick={() => { handleBlock(detailCard.sourceIp, detailCard.title); setDetailCard(null); }}>
                  BLOQUEAR IP
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      <div style={{display:'grid', gap:12, gridTemplateColumns:'repeat(auto-fit,minmax(240px,1fr))', marginTop:12}}>
        <div className="widget" style={{padding:'18px 20px'}}>
          <div className="widget-header" style={{padding:'0 0 12px 0'}}>
            <div className="widget-header-left">
              <ShieldAlert size={15} style={{color:'var(--blue)'}} />
              <div className="widget-title">Top Orígenes Activos</div>
            </div>
          </div>
          <div style={{display:'flex', flexDirection:'column', gap:10}}>
            {activeThreats.top_sources?.length > 0 ? activeThreats.top_sources.map((entry) => (
              <div key={entry.source_ip} style={{display:'flex', justifyContent:'space-between', alignItems:'center', padding:'10px 12px', background:'rgba(255,255,255,0.03)', borderRadius:'var(--radius-sm)'}}>
                <div>
                  <div style={{fontSize:'0.85rem', fontWeight:700}}>{entry.source_ip}</div>
                  <div style={{fontSize:'0.72rem', color:'var(--text-muted)'}}>Alertas: {entry.count}</div>
                </div>
                <span className="badge-pill rose">{entry.last_seen ? new Date(entry.last_seen).toLocaleTimeString('es-PE', {hour12:false}) : '—'}</span>
              </div>
            )) : (
              <div style={{fontSize:'0.8rem', color:'var(--text-muted)'}}>No hay orígenes críticos activos en este momento.</div>
            )}
          </div>
        </div>

        <div className="widget" style={{padding:'18px 20px'}}>
          <div className="widget-header" style={{padding:'0 0 12px 0'}}>
            <div className="widget-header-left">
              <Lock size={15} style={{color:'var(--rose)'}} />
              <div className="widget-title">IPs Bloqueadas</div>
            </div>
          </div>
          <div style={{display:'flex', flexDirection:'column', gap:8}}>
            {activeThreats.blocked_ips?.length > 0 ? activeThreats.blocked_ips.map((item) => (
              <div key={item.ip} style={{display:'flex', justifyContent:'space-between', alignItems:'center', padding:'10px 12px', background:'rgba(255,255,255,0.03)', borderRadius:'var(--radius-sm)'}}>
                <div>
                  <div style={{fontSize:'0.85rem', fontWeight:700}}>{item.ip}</div>
                  <div style={{fontSize:'0.72rem', color:'var(--text-muted)'}}>Método: {item.method}</div>
                </div>
                <span className="badge-pill emerald">{item.blocked_at ? new Date(item.blocked_at).toLocaleTimeString('es-PE', {hour12:false}) : '—'}</span>
              </div>
            )) : (
              <div style={{fontSize:'0.8rem', color:'var(--text-muted)'}}>No se han bloqueado IPs recientes.</div>
            )}
          </div>
        </div>
      </div>

      {/* ── Charts Row ── */}
      <Row className="g-3">
        <Col lg={8}>
          <div className="widget">
            <div className="widget-header">
              <div className="widget-header-left">
                <Activity size={15} style={{color:'var(--blue)'}} />
                <div className="widget-title">Mapa de Calor — Tráfico 24h</div>
              </div>
              <span style={{fontSize:'0.65rem', color:'var(--text-muted)', fontFamily:"'Space Mono',monospace"}}>UTC · VENTANA MÁXIMA</span>
            </div>
            <div className="widget-body">
              <div style={{height:220}}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={heatmap} margin={{top:0,right:0,left:-20,bottom:0}}>
                    <XAxis dataKey="name" stroke="transparent" tick={{fill:'var(--text-muted)',fontSize:11}} />
                    <YAxis stroke="transparent" tick={{fill:'var(--text-muted)',fontSize:11}} />
                    <Tooltip
                      cursor={{fill:'rgba(255,255,255,0.04)'}}
                      contentStyle={{background:'var(--bg-card)',border:'1px solid var(--border-default)',borderRadius:'var(--radius-sm)',fontSize:'0.75rem'}}
                      formatter={v=>[`${v} eventos`,'Cantidad']}
                    />
                    <Bar dataKey="val" radius={[4,4,0,0]}>
                      {heatmap.map((e,i) => (
                        <Cell key={`hm-${i}`} fill={e.val>10?'var(--rose)':'var(--blue)'} fillOpacity={0.7} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </Col>

        <Col lg={4}>
          <div className="widget" style={{height:'100%'}}>
            <div className="widget-header">
              <div className="widget-header-left">
                <ShieldAlert size={15} style={{color:'var(--cyan)'}}/>
                <div className="widget-title">Estado de Mitigación</div>
              </div>
            </div>
            <div className="widget-body">
              {[
                { label:'Escudos Activos', value: mitigStats.shields, color:'blue' },
                { label:'Supresión de Amenazas', value: mitigStats.suppression, color:'emerald' },
              ].map(({ label, value, color }) => (
                <div key={label} className="mb-4">
                  <div style={{display:'flex', justifyContent:'space-between', marginBottom:8, fontSize:'0.75rem'}}>
                    <span style={{color:'var(--text-secondary)'}}>{label}</span>
                    <span style={{fontWeight:700, color:`var(--${color})`, fontFamily:"'Space Mono',monospace"}}>{value}%</span>
                  </div>
                  <div className="prog-bar-track">
                    <div className={`prog-bar-fill ${color}`} style={{width:`${value}%`}} />
                  </div>
                </div>
              ))}
              <p style={{fontSize:'0.73rem', color:'var(--text-muted)', lineHeight:1.5, marginTop:8}}>
                {mitigStats.shields > 70 ? 'Motor neural mitigando amenazas exitosamente.'
                  : mitigStats.shields > 30 ? 'Mitigación parcial activa. Revisión manual recomendada.'
                  : 'Nivel bajo. Iniciar procedimiento de respuesta.'}
              </p>
              <button className="btn-ghost-rose" style={{width:'100%', justifyContent:'center', marginTop:12}}
                onClick={handleEmergencyPurge} disabled={purging}>
                {purging ? 'PURGANDO...' : 'PURGADO DE EMERGENCIA'}
              </button>
            </div>
          </div>
        </Col>
      </Row>

      {/* Footer */}
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', paddingTop:12, borderTop:'1px solid var(--border-subtle)', fontSize:'0.7rem', fontFamily:"'Space Mono',monospace", color:'var(--text-muted)'}}>
        <div style={{display:'flex', alignItems:'center', gap:8}}>
          <span className="status-dot emerald pulse"/>
          FLUJO EN VIVO ACTIVO
        </div>
        <div style={{display:'flex', gap:24}}>
          <span>EVENTOS: <span style={{color:'var(--text-white)'}}>{(summaryStats.critical+summaryStats.warning+summaryStats.info).toLocaleString()}</span></span>
          <span>BLOQUEADAS: <span style={{color:'var(--rose)'}}>{String(threatCards.filter(c=>c.actionTaken?.includes('BLOCKED')).length).padStart(2,'0')}</span></span>
        </div>
      </div>
    </div>
  );
}
