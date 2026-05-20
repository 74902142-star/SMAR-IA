import { useState, useEffect, useRef } from 'react';
import { Row, Col, Badge, ProgressBar } from 'react-bootstrap';
import { ShieldCheck, AlertTriangle, Activity, Cpu, Thermometer, Clock, Target, List, Zap, Cpu as Processor, Server } from 'lucide-react';
import { toast } from 'react-toastify';



export default function Dashboard() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({ total_alerts: 0, actions_taken: 0 });
  const [packets, setPackets] = useState([]);
  const [recentIps, setRecentIps] = useState({});
  const ws = useRef(null);

  // ── Datos reales del backend ────────────────────────────────
  const [systemStats, setSystemStats] = useState(null);


  useEffect(() => {
    // WebSocket for live traffic
    ws.current = new WebSocket('ws://localhost:8000/ws');
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'traffic_update') {
        const id = Math.random().toString(36).substr(2, 9);
        
        // Burst detection logic
        const ipCount = (recentIps[data.source_ip] || 0) + 1;
        setRecentIps(prev => ({ ...prev, [data.source_ip]: ipCount }));
        
        // Determine packet type
        let type = 'normal';
        if (ipCount > 3) type = 'burst';
        else if (data.is_alert) {
          type = data.confidence > 0.9 ? 'critical' : 'suspicious';
        }

        const newPacket = {
          id,
          type,
          origin: Math.floor(Math.random() * 3) + 1 
        };
        
        setPackets(prev => [...prev, newPacket]);
        
        // Push to live logs
        const newLog = {
          timestamp: data.timestamp,
          source_ip: data.source_ip,
          attack_type: data.is_alert ? data.predicted_class : null,
          action_taken: data.action_taken,
          isLive: true
        };
        setLogs(prev => [newLog, ...prev.slice(0, 14)]);

        // Trigger Toast Alerts for suspicious traffic
        if (data.is_alert) {
          const toastType = data.confidence > 0.9 ? 'error' : 'warning';
          toast[toastType](`INGRESO SOSPECHOSO: ${data.predicted_class} desde ${data.source_ip}`, {
            position: "top-right",
            autoClose: 5000,
            theme: "dark",
            style: {
              border: data.confidence > 0.9 ? '1px solid #ff0055' : '1px solid #f59e0b',
              background: '#0d1117',
              fontFamily: "'Space Mono', monospace"
            }
          });
        }
        
        // Remove packet after animation (1s)

        setTimeout(() => {
          setPackets(prev => prev.filter(p => p.id !== id));
          // Gradually decrease IP count
          setRecentIps(prev => {
            const newCounts = { ...prev };
            if (newCounts[data.source_ip] > 0) newCounts[data.source_ip]--;
            return newCounts;
          });
        }, 1000);

      }
    };

    // Fetch initial logs
    fetch('http://localhost:8000/api/logs?limit=10')
      .then(res => res.json())
      .then(data => {
        setLogs(data);
        setStats({
          total_alerts: data.length,
          actions_taken: data.filter(l => l.action_taken !== 'NONE' && l.action_taken !== 'ALERTED').length
        });
      });

    return () => ws.current?.close();
  }, []);

  // ── Fetch estadísticas reales del sistema ────────────────────
  useEffect(() => {
    const fetchStats = () => {
      fetch('http://localhost:8000/api/stats')
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) setSystemStats(data);
        })
        .catch(() => {});
    };

    fetchStats();
    const interval = setInterval(fetchStats, 15000); // cada 15s
    return () => clearInterval(interval);
  }, []);

  // ── Valores derivados de datos reales ─────────────────────────
  const cpuPercent = systemStats?.resources?.cpu_percent ?? 0;
  const ramPercent = systemStats?.resources?.ram_percent ?? 0;
  const uptime = systemStats?.uptime ?? '000:00:00';
  const avgConfidence = systemStats?.model?.confidence_avg ?? 90;
  const pendingAlerts = systemStats?.counts?.pending_alerts ?? 0;
  const criticalCount = systemStats?.counts?.critical ?? 0;
  const totalLogs24h = systemStats?.counts?.total_last_24h ?? 0;
  const autoBlocked = systemStats?.counts?.auto_blocked ?? 0;
  const manualBlocked = systemStats?.counts?.manual_blocked ?? 0;
  const totalBlocked = autoBlocked + manualBlocked;

  // Determinar estado del sistema basado en CPU
  const systemStatus = cpuPercent > 85 ? 'ALERTA' : cpuPercent > 60 ? 'ELEVADO' : 'NOMINAL';
  const statusBg = cpuPercent > 85 ? 'danger' : cpuPercent > 60 ? 'warning' : 'success';

  // Throughput estimado (basado en tráfico procesado)
  const throughput = totalLogs24h > 0 
    ? `${(totalLogs24h / 86400 * 1.5).toFixed(1)} TB/S` 
    : '0.0 TB/S';

  return (
    <div className="dashboard-content">
      <Row className="g-4">
        {/* Top Row: Live Traffic and System Health */}
        <Col lg={8}>
          <div className="cyber-widget large-widget">
            <div className="widget-header">
              <div className="title-area">
                <Activity size={18} className="text-cyan me-2" />
                <h5 className="m-0">TRÁFICO DE RED EN VIVO</h5>
              </div>
              <span className="subtitle">ANÁLISIS DE PAQUETES EN TIEMPO REAL _ SMAR-IA_CORE_01</span>
            </div>
            <div className="traffic-map-container">
              {/* Live Network Graph */}
              <div className="network-graph">
                <div className="node central">
                  <Processor size={24} />
                  <div className="glow-ring"></div>
                </div>
                
                {/* Static Origin Nodes */}
                <div className="node cyan pos-1"><Server size={12} /></div>
                <div className="node red pos-2"><Server size={12} /></div>
                <div className="node yellow pos-3"><Server size={12} /></div>
                
                {/* Connection Lines */}
                <div className="connection-line line-1"></div>
                <div className="connection-line line-2"></div>
                <div className="connection-line line-3"></div>

                {/* Dynamic Packets */}
                {packets.map(packet => (
                  <div 
                    key={packet.id} 
                    className={`packet origin-${packet.origin} type-${packet.type}`}
                  >
                    <div className="packet-glow"></div>
                  </div>
                ))}
              </div>

              <div className="traffic-stats">
                <div className="stat-item">
                  <span className="label">RENDIMIENTO</span>
                  <span className="value">{throughput}</span>
                </div>
                <div className="stat-item">
                  <span className="label">EVENTOS 24H</span>
                  <span className="value text-pink">{totalLogs24h.toLocaleString()}</span>
                </div>
              </div>
            </div>

          </div>
        </Col>

        <Col lg={4}>
          <div className="cyber-widget mb-4">
            <div className="widget-header">
              <div className="title-area">
                <Activity size={18} className="text-cyan me-2" />
                <h5 className="m-0">ESTADO DEL SISTEMA</h5>
              </div>
              <Badge bg={statusBg} className="nominal-badge">{systemStatus}</Badge>
            </div>
            <div className="health-stats mt-4">
              <div className="progress-group mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <span className="label">USO DE CPU</span>
                  <span className="value">{cpuPercent.toFixed(0)}%</span>
                </div>
                <div className="cyber-progress">
                  <div className="progress-bar cyan" style={{width: `${Math.min(cpuPercent, 100)}%`}}></div>
                </div>
              </div>
              <div className="progress-group mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <span className="label">USO DE RAM</span>
                  <span className="value">{ramPercent.toFixed(0)}%</span>
                </div>
                <div className="cyber-progress">
                  <div className="progress-bar pink" style={{width: `${Math.min(ramPercent, 100)}%`}}></div>
                </div>
              </div>
              <div className="uptime-info">
                <div className="label">UPTIME: {uptime}</div>
                <Clock size={16} className="text-muted" />
              </div>
            </div>
          </div>

          <div className="cyber-widget active-threats">
            <div className="widget-header">
              <div className="title-area">
                <AlertTriangle size={18} className="text-pink me-2" />
                <h5 className="m-0">AMENAZAS ACTIVAS</h5>
              </div>
              <AlertTriangle size={18} className="text-pink" />
            </div>
            <div className="threat-count-area">
              <span className="huge-number">{String(criticalCount + pendingAlerts).padStart(2, '0')}</span>
              <span className="high-alert">{criticalCount > 0 ? 'ALERTA ALTA' : 'SIN ALERTAS'}</span>
            </div>
            <div className="threat-list">
              {systemStats?.attack_distribution?.slice(0, 2).map((attack, i) => (
                <div key={i} className={`threat-item ${i === 0 ? 'pink' : 'yellow'}`}>
                  <div className="dot"></div>
                  {attack.type}: {attack.count} DETECCIONES
                </div>
              ))}
              {(!systemStats?.attack_distribution || systemStats.attack_distribution.length === 0) && (
                <>
                  <div className="threat-item yellow">
                    <div className="dot"></div>
                    MONITOREANDO RED... SIN AMENAZAS
                  </div>
                </>
              )}
            </div>
          </div>
        </Col>

        {/* Bottom Row: IA Analysis and Logs */}
        <Col lg={4}>
          <div className="cyber-widget h-100">
            <div className="widget-header">
              <div className="title-area">
                <Target size={18} className="text-yellow me-2" />
                <h5 className="m-0">CONFIANZA DE ANÁLISIS IA</h5>
              </div>
            </div>
            <div className="confidence-gauge">
              <div className="circular-progress">
                <div className="inner-circle">
                  <span className="percent">{avgConfidence.toFixed(0)}%</span>
                  <span className="status">{avgConfidence >= 90 ? 'ÓPTIMO' : avgConfidence >= 70 ? 'ACEPTABLE' : 'BAJO'}</span>
                </div>
              </div>
              <p className="analysis-text mt-4">
                {avgConfidence >= 90 
                  ? `Modelo operando con alta confianza. ${totalBlocked} amenazas mitigadas.`
                  : avgConfidence >= 70 
                  ? 'Confianza aceptable. Se recomienda supervisión manual.'
                  : 'Confianza baja. Revisar dataset de entrenamiento.'}
              </p>
            </div>
          </div>
        </Col>

        <Col lg={8}>
          <div className="cyber-widget terminal-widget h-100">
            <div className="widget-header">
              <div className="title-area">
                <List size={18} className="text-cyan me-2" />
                <h5 className="m-0">REGISTRO_ACTIVIDAD_RED_NEURAL</h5>
              </div>
              <div className="header-dots">
                <div className="dot green"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
            <div className="terminal-body mt-3">
              {logs.map((log, i) => (
                <div key={i} className={`log-line ${log.isLive ? 'live-fade-in' : ''}`}>
                  <span className="timestamp">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                  {log.attack_type ? (
                    <span className="message alert">
                      <AlertTriangle size={12} className="me-1" />
                      CRÍTICO: {log.attack_type} DETECTADA DESDE {log.source_ip}
                    </span>
                  ) : (
                    <span className="message info">
                      <Activity size={12} className="me-1" />
                      FLUJO_NOMINAL: PETICIÓN DESDE {log.source_ip} {'->'} {log.action_taken}
                    </span>

                  )}
                </div>
              ))}
              {!logs.length && (
                <div className="log-line text-muted">ESPERANDO TRANSMISIÓN DE DATOS...</div>
              )}
            </div>

          </div>
        </Col>
      </Row>
    </div>
  );
}
