import { useState, useEffect, useRef } from 'react';
import { Row, Col } from 'react-bootstrap';
import { Terminal, Download, Maximize2, Cpu, Activity, Server, CheckCircle2 } from 'lucide-react';


export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [categories, setCategories] = useState({ network: true, security: true, ai: true });
  const [stats, setStats] = useState({ total: 0, critical: 0 });
  const terminalEndRef = useRef(null);
  const ws = useRef(null);

  const scrollToBottom = () => terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });

  useEffect(() => {
    fetch('http://localhost:8000/api/logs?limit=60')
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

    ws.current = new WebSocket('ws://localhost:8000/ws');
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

  const filtered = logs.filter(l => {
    if (filter === 'CRITICAL') return l.isCritical;
    if (filter === 'NORMAL')   return !l.isCritical;
    return true;
  });

  const catColor = (cat) => {
    if (cat === 'CRITICAL_ERR') return 'var(--rose)';
    if (cat === 'NW_TRAFFIC')   return 'var(--blue)';
    return 'var(--cyan)';
  };

  return (
    <div className="logs-page">
      {/* ── Header ── */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1>System Log Stream</h1>
          <p>Real-time network audit &amp; AI decision telemetry</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.72rem', fontFamily: "'Space Mono',monospace", color: 'var(--text-muted)' }}>
            <span className="status-dot emerald pulse" />
            LIVE FEED
          </div>
          <select
            value={filter}
            onChange={e => setFilter(e.target.value)}
            style={{
              background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-default)',
              borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)',
              padding: '7px 12px', fontSize: '0.78rem', outline: 'none',
              fontFamily: "'Inter',sans-serif", cursor: 'pointer',
            }}
          >
            <option value="ALL">TODOS LOS EVENTOS</option>
            <option value="CRITICAL">SOLO CRÍTICOS</option>
            <option value="NORMAL">SOLO NORMALES</option>
          </select>
        </div>
      </div>

      <Row className="g-3">
        {/* ── Left sidebar stats ── */}
        <Col lg={3}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {/* Stat cards */}
            {[
              { label: 'TOTAL EVENTOS / SESIÓN', value: stats.total.toLocaleString(), color: 'blue' },
              { label: 'ANOMALÍAS CRÍTICAS',     value: String(stats.critical),       color: 'rose' },
              { label: 'LÍNEAS RENDERIZADAS',    value: String(filtered.length),      color: 'cyan' },
            ].map(({ label, value, color }) => (
              <div key={label} className="log-sidebar-stat">
                <div className="log-sidebar-label">{label}</div>
                <div className={`log-sidebar-value text-${color}`}>{value}</div>
              </div>
            ))}

            {/* Topology widget */}
            <div className="widget" style={{ overflow: 'hidden' }}>
              <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.65rem', letterSpacing: '1.5px', color: 'var(--amber)', fontWeight: 700, marginBottom: 2 }}>NETWORK_TOPOLOGY</div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>Sub-Sector 7-B Status</div>
              </div>
              <div style={{ height: 80, position: 'relative', overflow: 'hidden', background: 'rgba(0,0,0,0.2)' }}>
                {/* Animated scan line */}
                <div style={{
                  position: 'absolute', left: 0, right: 0, height: '1px',
                  background: 'linear-gradient(90deg, transparent, var(--blue), transparent)',
                  animation: 'scanline 2.5s linear infinite',
                }} />
                <style>{`@keyframes scanline { 0%{top:0%} 100%{top:100%} }`}</style>
                {/* Grid */}
                <div style={{
                  position: 'absolute', inset: 0, opacity: 0.15,
                  backgroundImage: 'linear-gradient(var(--blue) 1px, transparent 1px), linear-gradient(90deg, var(--blue) 1px, transparent 1px)',
                  backgroundSize: '20px 20px',
                }} />
              </div>
            </div>

            {/* Log categories */}
            <div className="widget">
              <div className="widget-header">
                <div className="widget-title">Categorías</div>
              </div>
              <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
                {[
                  { key: 'network',  label: 'Network Events',    color: 'blue' },
                  { key: 'security', label: 'Security Audits',   color: 'amber' },
                  { key: 'ai',       label: 'AI Decision Logs',  color: 'rose' },
                ].map(({ key, label, color }) => (
                  <div key={key} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ width: 8, height: 8, borderRadius: '50%', background: `var(--${color})`, display: 'inline-block' }} />
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{label}</span>
                    </div>
                    <label className="toggle-wrapper">
                      <input
                        type="checkbox"
                        checked={categories[key]}
                        onChange={() => setCategories(prev => ({ ...prev, [key]: !prev[key] }))}
                      />
                      <span className="toggle-slider" />
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Col>

        {/* ── Terminal ── */}
        <Col lg={9}>
          <div className="terminal-window">
            {/* Title bar */}
            <div className="terminal-titlebar">
              <div className="terminal-dots">
                <span className="dot-r" />
                <span className="dot-y" />
                <span className="dot-g" />
              </div>
              <div className="terminal-path">
                <Terminal size={13} />
                <span style={{ color: 'var(--blue)' }}>root</span>
                <span className="sep">@</span>
                <span>smar-ia</span>
                <span className="sep">:</span>
                <span style={{ color: 'var(--emerald)' }}>~/_logs/live</span>
              </div>
              <div className="terminal-actions">
                <Download size={14} />
                <Maximize2 size={14} />
              </div>
            </div>

            {/* Log body */}
            <div className="terminal-body">
              {/* Init lines */}
              <div className="log-entry" style={{ marginBottom: 8, paddingBottom: 8, borderBottom: '1px solid var(--border-subtle)' }}>
                <span className="log-time" style={{ color: 'var(--emerald)' }}>SMAR-IA</span>
                <span className="log-msg" style={{ color: 'var(--text-muted)' }}>System log stream initialized · filter: {filter}</span>
              </div>

              {filtered.map((log, i) => (
                <div key={i} className={`log-entry ${log.isCritical ? 'critical' : ''}`}>
                  <span className="log-time">[{log.timestamp}]</span>
                  <span
                    className="log-cat-badge badge-pill"
                    style={{
                      background: log.isCritical ? 'rgba(244,63,94,0.1)' : 'rgba(6,182,212,0.1)',
                      color: catColor(log.category),
                      border: `1px solid ${log.isCritical ? 'rgba(244,63,94,0.25)' : 'rgba(6,182,212,0.25)'}`,
                      fontSize: '0.58rem', padding: '1px 7px', flexShrink: 0,
                    }}
                  >
                    {log.category}
                  </span>
                  <span className="log-msg">{log.message}</span>
                </div>
              ))}

              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 10, color: 'var(--text-muted)', fontFamily: "'Space Mono',monospace", fontSize: '0.72rem' }}>
                <span className="blink-cursor" />
                WAITING FOR DATA PACKETS...
              </div>
              <div ref={terminalEndRef} />
            </div>

            {/* Status bar */}
            <div className="terminal-statusbar">
              <div style={{ display: 'flex', gap: 20 }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span className="status-dot green pulse" /> LIVE FEED
                </span>
                <span style={{ color: 'rgba(255,255,255,0.2)' }}>·</span>
                <span>VERBOSE MODE: <span style={{ color: 'var(--text-muted)' }}>OFF</span></span>
              </div>
              <span>LINES: <span style={{ color: 'var(--text-white)' }}>{filtered.length}</span></span>
            </div>
          </div>
        </Col>
      </Row>

      {/* ── Bottom info bar ── */}
      <Row className="g-3">
        {[
          { icon: Cpu,          label: 'MEMORY USAGE',  value: '4.2 GB / 32 GB', color: 'blue' },
          { icon: Activity,     label: 'CPU CLUSTER',   value: '64% Load',       color: 'rose' },
          { icon: CheckCircle2, label: 'HUB SYNC',      value: 'Synced Now',     color: 'emerald' },
          { icon: Server,       label: 'ACTIVE NODES',  value: '1,024 Nodes',    color: 'cyan' },
        ].map(({ icon: Icon, label, value, color }) => (
          <Col key={label} md={3}>
            <div className="widget">
              <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '16px 18px' }}>
                <div style={{ width: 40, height: 40, borderRadius: 'var(--radius-sm)', background: `rgba(${color === 'blue' ? '59,130,246' : color === 'rose' ? '244,63,94' : color === 'emerald' ? '16,185,129' : '6,182,212'},0.1)`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: `var(--${color})`, flexShrink: 0 }}>
                  <Icon size={18} />
                </div>
                <div>
                  <div style={{ fontSize: '0.62rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 700 }}>{label}</div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-white)' }}>{value}</div>
                </div>
              </div>
            </div>
          </Col>
        ))}
      </Row>
    </div>
  );
}
