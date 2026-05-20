import { useState, useEffect, useRef } from 'react';
import { Row, Col, Form } from 'react-bootstrap';
import { 
  Terminal, 
  Filter, 
  Download, 
  Maximize2, 
  Cpu, 
  Activity, 
  Network, 
  Server,
  AlertTriangle,
  CheckCircle2,
  Clock
} from 'lucide-react';

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('ALL_EVENTS');
  const terminalEndRef = useRef(null);
  const ws = useRef(null);

  const [categories, setCategories] = useState({
    network: true,
    security: true,
    ai: true
  });

  const scrollToBottom = () => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Initial fetch
    fetch('http://localhost:8000/api/logs?limit=50')
      .then(res => res.json())
      .then(data => {
        const formattedLogs = data.map(log => ({
          timestamp: new Date(log.timestamp).toLocaleTimeString(),
          category: log.attack_type !== 'Normal' ? 'CRITICAL_ERR' : 'SEC_AUDIT',
          message: log.attack_type !== 'Normal' 
            ? `UNAUTHORIZED_ACCESS_ATTEMPT detected at node ${log.destination_ip}. Confidence: ${(log.confidence * 100).toFixed(2)}%`
            : `Routine check passed for IP ${log.source_ip}. Action: ${log.action_taken}`,
          isCritical: log.attack_type !== 'Normal'
        }));
        setLogs(formattedLogs);
      });

    // WebSocket for live stream
    ws.current = new WebSocket('ws://localhost:8000/ws');
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'traffic_update') {
        const newLog = {
          timestamp: new Date(data.timestamp).toLocaleTimeString(),
          category: data.is_alert ? 'CRITICAL_ERR' : 'NW_TRAFFIC',
          message: data.is_alert 
            ? `${data.predicted_class.toUpperCase()} detected from ${data.source_ip}. Action: ${data.action_taken}`
            : `Inbound request from ${data.source_ip} handled by gateway.`,
          isCritical: data.is_alert
        };
        setLogs(prev => [...prev.slice(-99), newLog]);
      }
    };

    return () => ws.current?.close();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  return (
    <div className="logs-page">
      <div className="logs-header-area mb-5">
        <div className="d-flex justify-content-between align-items-end">
          <div className="title-section">
            <h1 className="cyber-title mb-1">SYSTEM_LOG_STREAM</h1>
            <p className="cyber-subtitle text-cyan">REAL-TIME NETWORK AUDIT & AI DECISION TELEMETRY</p>
          </div>
          <div className="header-meta d-flex gap-4">
            <div className="meta-item">
              <span className="dot green"></span>
              <span className="label-sm">UPTIME: 142:12:05</span>
            </div>
            <div className="filter-dropdown">
              <span className="label-sm me-2 text-secondary">FILTER:</span>
              <select 
                className="cyber-select" 
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="ALL_EVENTS">ALL_EVENTS</option>
                <option value="CRITICAL_ONLY">CRITICAL_ONLY</option>
                <option value="AI_LOGIC">AI_LOGIC</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <Row className="g-4">
        {/* Left Stats Sidebar */}
        <Col lg={3}>
          <div className="logs-side-stats">
            <div className="cyber-widget mb-4">
              <span className="label-sm text-secondary d-block mb-1">TOTAL EVENTS / 24H</span>
              <h3 className="huge-number-sm text-cyan m-0">482,901</h3>
              <div className="mini-progress mt-2">
                <div className="fill cyan" style={{width: '70%'}}></div>
              </div>
            </div>

            <div className="cyber-widget mb-4">
              <span className="label-sm text-secondary d-block mb-1">CRITICAL ANOMALIES</span>
              <h3 className="huge-number-sm text-pink m-0">12</h3>
              <span className="trend text-pink mt-1 d-block" style={{fontSize: '0.65rem'}}>
                <Activity size={12} className="me-1" /> +4 since last cycle
              </span>
            </div>

            <div className="cyber-widget topology-widget mb-4 p-0 overflow-hidden">
               <div className="topology-overlay p-3">
                  <span className="label-sm text-yellow">NETWORK_TOPOLOGY</span>
                  <h6 className="m-0">Sub-Sector 7-B Status</h6>
               </div>
               <div className="topology-visual">
                  <div className="scan-line"></div>
                  <div className="grid-bg"></div>
               </div>
            </div>

            <div className="cyber-widget">
              <span className="label-sm text-secondary d-block mb-3">LOG CATEGORIES</span>
              <div className="category-list">
                <div className="category-item d-flex align-items-center justify-content-between mb-2">
                  <div className="d-flex align-items-center gap-2">
                    <div className="dot-sm cyan"></div>
                    <span className="cat-name">Network Events</span>
                  </div>
                  <Form.Check 
                    className="cyber-checkbox"
                    checked={categories.network}
                    onChange={() => setCategories({...categories, network: !categories.network})}
                  />
                </div>
                <div className="category-item d-flex align-items-center justify-content-between mb-2">
                  <div className="d-flex align-items-center gap-2">
                    <div className="dot-sm yellow"></div>
                    <span className="cat-name">Security Audits</span>
                  </div>
                  <Form.Check 
                    className="cyber-checkbox"
                    checked={categories.security}
                    onChange={() => setCategories({...categories, security: !categories.security})}
                  />
                </div>
                <div className="category-item d-flex align-items-center justify-content-between">
                  <div className="d-flex align-items-center gap-2">
                    <div className="dot-sm pink"></div>
                    <span className="cat-name">AI Decision Logs</span>
                  </div>
                  <Form.Check 
                    className="cyber-checkbox"
                    checked={categories.ai}
                    onChange={() => setCategories({...categories, ai: !categories.ai})}
                  />
                </div>
              </div>
            </div>
          </div>
        </Col>

        {/* Main Terminal Area */}
        <Col lg={9}>
          <div className="terminal-container h-100">
            <div className="terminal-header">
              <div className="header-dots">
                <span className="dot pink"></span>
                <span className="dot yellow"></span>
                <span className="dot green"></span>
              </div>
              <div className="header-path">
                <Terminal size={14} className="me-2" />
                ROOT@SMAR-IA: ~/_LOGS/LIVE_STREAM
              </div>
              <div className="header-actions">
                <Download size={14} className="me-3" />
                <Maximize2 size={14} />
              </div>
            </div>

            <div className="terminal-body scrollbar-custom">
              {logs.map((log, i) => (
                <div key={i} className={`log-entry ${log.isCritical ? 'critical' : ''}`}>
                  <span className="log-time">[{log.timestamp}]</span>
                  <span className={`log-cat ${log.category === 'CRITICAL_ERR' ? 'text-pink' : 'text-cyan'}`}>
                    [{log.category}]
                  </span>
                  <span className="log-msg">{log.message}</span>
                </div>
              ))}
              <div className="terminal-status-line mt-3">
                <span className="cursor-blink">_</span> WAITING FOR DATA PACKETS...
              </div>
              <div ref={terminalEndRef} />
            </div>

            <div className="terminal-footer">
              <div className="footer-left d-flex gap-4">
                <div className="status-indicator">
                  <div className="dot-pulse green"></div>
                  LIVE FEED
                </div>
                <div className="status-indicator inactive">
                  <div className="dot gray"></div>
                  VERBOSE MODE
                </div>
              </div>
              <div className="footer-right text-secondary">
                LINES_RENDERED: <span className="text-white">{logs.length}</span>
              </div>
            </div>
          </div>
        </Col>
      </Row>

      {/* Bottom Info Bar */}
      <Row className="g-4 mt-4">
        <Col md={3}>
          <div className="cyber-widget footer-info-card">
            <div className="d-flex align-items-center gap-3">
              <div className="info-icon cyan"><Cpu size={18} /></div>
              <div>
                <span className="label-sm text-secondary">MEMORY USAGE</span>
                <h5 className="m-0">4.2 GB / 32 GB</h5>
              </div>
            </div>
          </div>
        </Col>
        <Col md={3}>
          <div className="cyber-widget footer-info-card">
            <div className="d-flex align-items-center gap-3">
              <div className="info-icon pink"><Activity size={18} /></div>
              <div>
                <span className="label-sm text-secondary">CPU CLUSTER</span>
                <h5 className="m-0">64% Load</h5>
              </div>
            </div>
          </div>
        </Col>
        <Col md={3}>
          <div className="cyber-widget footer-info-card">
            <div className="d-flex align-items-center gap-3">
              <div className="info-icon yellow"><CheckCircle2 size={18} /></div>
              <div>
                <span className="label-sm text-secondary">HUB SYNC</span>
                <h5 className="m-0">Synced Now</h5>
              </div>
            </div>
          </div>
        </Col>
        <Col md={3}>
          <div className="cyber-widget footer-info-card">
            <div className="d-flex align-items-center gap-3">
              <div className="info-icon cyan"><Server size={18} /></div>
              <div>
                <span className="label-sm text-secondary">ACTIVE NODES</span>
                <h5 className="m-0">1,024 Nodes</h5>
              </div>
            </div>
          </div>
        </Col>
      </Row>
    </div>
  );
}
