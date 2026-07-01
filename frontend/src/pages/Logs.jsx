import { useState, useEffect, useRef } from 'react';
import { Row, Col } from 'react-bootstrap';
import { Terminal, Download, Maximize2, Minimize2, Cpu, Activity, Server, CheckCircle2 } from 'lucide-react';
import { toast } from 'react-toastify';
import { apiUrl, wsUrl } from '../api';

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [categories, setCategories] = useState({ network: true, security: true, ai: true });
  const [stats, setStats] = useState({ total: 0, critical: 0 });
  const [fullscreen, setFullscreen] = useState(false);
  const terminalEndRef = useRef(null);
  const ws = useRef(null);
  const terminalRef = useRef(null);

  const scrollToBottom = () => terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });

  useEffect(() => {
    fetch(apiUrl('/api/logs?limit=60'))
      .then(r => r.json())
      .then(data => {
        const formatted = data.map(log => ({
          timestamp: new Date(log.timestamp).toLocaleTimeString('es-PE', { hour12: false }),
          category: log.attack_type && log.attack_type !== 'Normal' ? 'CRITICAL_ERR' : 'SEC_AUDIT',
          message: log.attack_type && log.attack_type !== 'Normal'
            ? `UNAUTHORIZED_ACCESS detected at ${log.destination_ip} · Confidence: ${((log.confidence || 0) * 100).toFixed(1)}% · Action: ${log.action_taken}`
            : `Routine check OK · IP ${log.source_ip} · ${log.action_taken}`,
          isCritical: !!(log.attack_type && log.attack_type !== 'Normal'),
        }));
        setLogs(formatted);
        setStats({ total: data.length, critical: data.filter(l => l.attack_type && l.attack_type !== 'Normal').length });
      })
      .catch(() => {});

    ws.current = new WebSocket(wsUrl('/ws'));
    ws.current.onopen = () => {
      ws.current.send(JSON.stringify({}));
    };
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type !== 'traffic_update') return;
      const newLog = {
        timestamp: new Date(data.timestamp).toLocaleTimeString('es-PE', { hour12: false }),
        category: data.is_alert ? 'CRITICAL_ERR' : 'NW_TRAFFIC',
        message: data.is_alert
          ? `${data.predicted_class.toUpperCase()} from ${data.source_ip} · Action: ${data.action_taken}`
          : `Inbound from ${data.source_ip} · handled by gateway`,
        isCritical: data.is_alert,
      };
      setLogs(prev => [...prev.slice(-99), newLog]);
      if (data.is_alert) setStats(prev => ({ ...prev, critical: prev.critical + 1 }));
      setStats(prev => ({ ...prev, total: prev.total + 1 }));
    };
    return () => ws.current?.close();
  }, []);

  useEffect(() => { scrollToBottom(); }, [logs]);

  const handleDownload = () => {
    const content = filtered.map(l => `[${l.timestamp}] [${l.category}] ${l.message}`).join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `smaria_logs_${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const toggleFullscreen = () => {
    setFullscreen(f => !f);
  };

  const filtered = logs.filter(l => {
    if (filter === 'CRITICAL') return l.isCritical;
    if (filter === 'NORMAL')   return !l.isCritical;
    return true;
  }).filter(l => {
    if (!categories.network && l.category === 'NW_TRAFFIC') return false;
    if (!categories.security && l.category === 'SEC_AUDIT') return false;
    if (!categories.ai && l.category === 'CRITICAL_ERR') return false;
    return true;
  });

  const catColor = (cat) => {
    if (cat === 'CRITICAL_ERR') return '#ef4444';
    if (cat === 'NW_TRAFFIC')   return '#7c3aed';
    return '#2b0075';
  };

  const terminalContent = (
    <div className="terminal-window" style={{ background: '#0f172a', border: '1px solid #1e293b' }} ref={terminalRef}>
      <div className="terminal-titlebar" style={{ background: '#1e293b', borderBottom: '1px solid #334155' }}>
        <div className="terminal-dots">
          <span className="dot-r" />
          <span className="dot-y" />
          <span className="dot-g" />
        </div>
        <div className="terminal-path" style={{ color: '#94a3b8' }}>
          <Terminal size={13} />
          <span style={{ color: '#a78bfa' }}>root</span>
          <span className="sep">@</span>
          <span>smar-ia</span>
          <span className="sep">:</span>
          <span style={{ color: '#34d399' }}>~/_logs/live</span>
        </div>
        <div className="terminal-actions" style={{ color: '#94a3b8' }}>
          <Download size={14} onClick={handleDownload} style={{cursor:'pointer', marginRight: 10}} />
          {fullscreen
            ? <Minimize2 size={14} onClick={toggleFullscreen} style={{cursor:'pointer'}} />
            : <Maximize2 size={14} onClick={toggleFullscreen} style={{cursor:'pointer'}} />
          }
        </div>
      </div>

      <div className="terminal-body" style={{ background: '#090d16', color: '#cbd5e1' }}>
        <div className="log-entry" style={{ marginBottom: 8, paddingBottom: 8, borderBottom: '1px solid #1e293b' }}>
          <span className="log-time" style={{ color: '#34d399' }}>[SYSTEM]</span>
          <span className="log-msg" style={{ color: '#64748b' }}>System log stream initialized · filter: {filter}</span>
        </div>

        {filtered.map((log, i) => (
          <div key={`${log.timestamp}-${i}`} className={`log-entry ${log.isCritical ? 'critical' : ''}`}>
            <span className="log-time" style={{ color: '#64748b' }}>[{log.timestamp}]</span>
            <span
              className="log-cat-badge badge-pill"
              style={{
                background: log.isCritical ? 'rgba(239,68,68,0.15)' : 'rgba(124,58,237,0.15)',
                color: catColor(log.category),
                fontSize: '0.62rem', padding: '2px 8px', flexShrink: 0,
              }}
            >
              {log.category}
            </span>
            <span className="log-msg" style={{ color: log.isCritical ? '#f87171' : '#cbd5e1' }}>{log.message}</span>
          </div>
        ))}

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 10, color: '#64748b', fontFamily: "'Space Mono',monospace", fontSize: '0.72rem' }}>
          <span className="blink-cursor" />
          ESPERANDO NUEVOS EVENTOS...
        </div>
        <div ref={terminalEndRef} />
      </div>

      <div className="terminal-statusbar" style={{ background: '#1e293b', borderTop: '1px solid #334155', color: '#94a3b8' }}>
        <div style={{ display: 'flex', gap: 20 }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span className="status-dot green pulse" style={{ width: 6, height: 6 }} /> LIVE STREAM
          </span>
        </div>
        <span>LÍNEAS: <span style={{ color: '#ffffff', fontWeight: 'bold' }}>{filtered.length}</span></span>
      </div>
    </div>
  );

  if (fullscreen) {
    return (
      <div style={{ position: 'fixed', inset: 0, zIndex: 9999, background: '#090d16', padding: 12 }}>
        {terminalContent}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }} className="campus-dashboard">
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 className="white-widget-title" style={{ fontSize: '1.8rem', marginBottom: 4 }}>Registros del Sistema</h1>
          <p className="white-widget-subtitle">Auditoría en tiempo real y flujo de telemetría de decisiones de la IA.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <select
            value={filter}
            onChange={e => setFilter(e.target.value)}
            style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '6px', color: '#1e293b', padding: '8px 12px', fontSize: '0.82rem' }}
          >
            <option value="ALL">TODOS LOS EVENTOS</option>
            <option value="CRITICAL">SOLO CRÍTICOS</option>
            <option value="NORMAL">SOLO NORMALES</option>
          </select>
        </div>
      </div>

      <div className="dashboard-layout-row" style={{ gridTemplateColumns: '1fr 3fr' }}>
        {/* Left column: stats and category filters */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {[
            { label: 'TOTAL EVENTOS / SESIÓN', value: stats.total.toLocaleString(), color: '#7c3aed' },
            { label: 'ANOMALÍAS CRÍTICAS',     value: String(stats.critical),       color: '#ef4444' },
            { label: 'LÍNEAS REGISTRADAS',    value: String(filtered.length),      color: '#7c3aed' },
          ].map((item, idx) => (
            <div key={idx} className="kpi-card" style={{ padding: 16 }}>
              <span className="kpi-label" style={{ fontSize: '0.72rem' }}>{item.label}</span>
              <span className="kpi-value" style={{ fontSize: '1.4rem', color: item.color }}>{item.value}</span>
            </div>
          ))}

          {/* Categories card */}
          <div className="white-widget" style={{ padding: 16 }}>
            <div className="white-widget-header" style={{ marginBottom: 12, paddingBottom: 8, borderBottom: '1px solid #e2e8f0' }}>
              <h3 className="white-widget-title" style={{ fontSize: '0.9rem' }}>Categorías</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[
                { key: 'network',  label: 'Tráfico de Red',    color: '#7c3aed' },
                { key: 'security', label: 'Auditoría',   color: '#2b0075' },
                { key: 'ai',       label: 'Decisiones IA',  color: '#ef4444' },
              ].map(({ key, label, color }) => (
                <div key={key} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: color, display: 'inline-block' }} />
                    <span style={{ fontSize: '0.78rem', color: '#475569', fontWeight: 600 }}>{label}</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={categories[key]}
                    onChange={() => setCategories(prev => ({ ...prev, [key]: !prev[key] }))}
                    style={{ cursor: 'pointer', accentColor: '#2b0075', width: 15, height: 15 }}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column: Terminal window */}
        <div>
          {terminalContent}
        </div>
      </div>

      {/* Bottom info panels */}
      <div className="kpi-container">
        {[
          { icon: Cpu,          label: 'USO DE MEMORIA',  value: '4.2 GB / 32 GB' },
          { icon: Activity,     label: 'CARGA DEL CLUSTER',   value: '64%' },
          { icon: CheckCircle2, label: 'SINCRONIZACIÓN',      value: 'Al día' },
          { icon: Server,       label: 'NODOS EN LÍNEA',  value: '1,024 Nodos' },
        ].map((stat, i) => (
          <div key={i} className="kpi-card" style={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div className="kpi-icon-box" style={{ width: 32, height: 32 }}>
                <stat.icon size={16} />
              </div>
              <div>
                <span className="kpi-label" style={{ fontSize: '0.65rem' }}>{stat.label}</span>
                <span className="kpi-value" style={{ fontSize: '0.9rem', color: '#1e293b' }}>{stat.value}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
