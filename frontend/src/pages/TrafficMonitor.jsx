import { useState, useEffect, useRef, useContext } from 'react';
import { Row, Col, Badge, ProgressBar } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { AlertTriangle, ShieldAlert, Info, Database, Globe, Lock, Search, Activity, Zap } from 'lucide-react';
import { toast } from 'react-toastify';
import { AuthContext } from '../context/AuthContext';

export default function TrafficMonitor() {
  const { token } = useContext(AuthContext);
  const [trafficData, setTrafficData] = useState([]);
  const [threatCards, setThreatCards] = useState([]);
  const [summaryStats, setSummaryStats] = useState({ critical: 0, warning: 0, info: 0 });
  const [heatmapData, setHeatmapData] = useState([]);
  const [mitigationStats, setMitigationStats] = useState({ shields: 0, suppression: 0 });
  const ws = useRef(null);

  // ── Fetch estadísticas reales ────────────────────────────────
  useEffect(() => {
    const fetchStats = () => {
      fetch('http://localhost:8000/api/stats')
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (!data) return;

          // Summary boxes con datos reales
          setSummaryStats({
            critical: data.counts?.critical || 0,
            warning: data.counts?.warning || 0,
            info: data.counts?.info || 0,
          });

          // Heatmap con distribución horaria real
          if (data.hourly_traffic && data.hourly_traffic.length > 0) {
            const mapped = data.hourly_traffic.map(h => ({
              name: h.hour,
              val: h.count,
            }));
            setHeatmapData(mapped);
          }

          // Métricas de mitigación
          const totalAlerts = (data.counts?.critical || 0) + (data.counts?.warning || 0) + (data.counts?.info || 0);
          const totalBlocked = (data.counts?.auto_blocked || 0) + (data.counts?.manual_blocked || 0);
          const shieldPercent = totalAlerts > 0 ? Math.min(Math.round((totalBlocked / totalAlerts) * 100), 100) : 0;
          const suppressionPercent = totalAlerts > 0 ? Math.min(Math.round(((totalAlerts - (data.counts?.pending_alerts || 0)) / totalAlerts) * 100), 100) : 0;
          
          setMitigationStats({
            shields: shieldPercent,
            suppression: suppressionPercent,
          });
        })
        .catch(() => {});
    };

    fetchStats();
    const interval = setInterval(fetchStats, 15000);
    return () => clearInterval(interval);
  }, []);

  // ── Fetch threat cards desde logs reales ──────────────────────
  useEffect(() => {
    fetch('http://localhost:8000/api/logs?limit=20')
      .then(res => res.ok ? res.json() : [])
      .then(data => {
        // Filtrar solo ataques y tomar los más recientes
        const attacks = data
          .filter(log => log.attack_type && log.attack_type !== 'Normal' && log.attack_type !== 'Unknown')
          .slice(0, 5);
        
        const cards = attacks.map(log => {
          const confidence = log.confidence || 0;
          let severity = 'info';
          let severityLabel = 'INFO';
          let badgeClass = 'badge-cyan';
          let borderClass = 'info-border';
          let iconComponent = Search;

          if (confidence >= 0.90) {
            severity = 'critical';
            severityLabel = 'CRÍTICO';
            badgeClass = 'badge-red';
            borderClass = 'critical-border';
            iconComponent = ShieldAlert;
          } else if (confidence >= 0.50) {
            severity = 'warning';
            severityLabel = 'ADVERTENCIA';
            badgeClass = 'badge-yellow';
            borderClass = 'warning-border';
            iconComponent = Database;
          }

          // Calcular tiempo relativo
          const logTime = new Date(log.timestamp);
          const now = new Date();
          const diffMs = now - logTime;
          const diffMin = Math.floor(diffMs / 60000);
          const timeAgo = diffMin < 1 ? 'AHORA' 
            : diffMin < 60 ? `HACE ${diffMin}M`
            : diffMin < 1440 ? `HACE ${Math.floor(diffMin / 60)}H`
            : `HACE ${Math.floor(diffMin / 1440)}D`;

          return {
            id: log.id,
            severity,
            severityLabel,
            badgeClass,
            borderClass,
            IconComponent: iconComponent,
            title: log.attack_type,
            sourceIp: log.source_ip,
            destIp: log.destination_ip,
            confidence: (confidence * 100).toFixed(1),
            timeAgo,
            actionTaken: log.action_taken,
          };
        });

        setThreatCards(cards);
      })
      .catch(() => {});
  }, []);

  // ── WebSocket para tráfico en vivo ────────────────────────────
  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/ws');
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'traffic_update') {
        const newPoint = {
          time: new Date(data.timestamp).toLocaleTimeString(),
          confidence: data.confidence * 100,
          class: data.predicted_class,
          isAlert: data.is_alert,
          ip: data.source_ip
        };
        setTrafficData(prev => [...prev.slice(-19), newPoint]); 

        if (data.is_alert) {
          toast.warning(`Amenaza detectada: ${data.predicted_class} desde ${data.source_ip}`, { theme: "dark" });

          // Agregar nueva threat card en vivo
          const confidence = data.confidence || 0;
          const newCard = {
            id: Date.now(),
            severity: confidence >= 0.9 ? 'critical' : confidence >= 0.5 ? 'warning' : 'info',
            severityLabel: confidence >= 0.9 ? 'CRÍTICO' : confidence >= 0.5 ? 'ADVERTENCIA' : 'INFO',
            badgeClass: confidence >= 0.9 ? 'badge-red' : confidence >= 0.5 ? 'badge-yellow' : 'badge-cyan',
            borderClass: confidence >= 0.9 ? 'critical-border' : confidence >= 0.5 ? 'warning-border' : 'info-border',
            IconComponent: confidence >= 0.9 ? ShieldAlert : confidence >= 0.5 ? Database : Search,
            title: data.predicted_class,
            sourceIp: data.source_ip,
            destIp: data.destination_ip || 'CORE_GATEWAY',
            confidence: (confidence * 100).toFixed(1),
            timeAgo: 'AHORA',
            actionTaken: data.action_taken,
          };
          setThreatCards(prev => [newCard, ...prev.slice(0, 4)]);
        }
      }
    };
    return () => { if (ws.current) ws.current.close(); };
  }, []);

  // ── Bloquear IP desde las threat cards ────────────────────────
  const handleBlockIp = async (ip, attackType) => {
    try {
      const res = await fetch('http://localhost:8000/api/mitigation/block', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ip: ip,
          action: 'BLOCK_IP',
          attack_type: attackType || 'Manual Block from Alerts',
        }),
      });

      if (res.ok) {
        toast.success(`IP ${ip} bloqueada exitosamente`, { theme: 'dark' });
        // Remover la card de la lista
        setThreatCards(prev => prev.filter(c => c.sourceIp !== ip));
      } else {
        toast.error('Error al bloquear IP', { theme: 'dark' });
      }
    } catch (e) {
      toast.error('Fallo de conexión con el backend', { theme: 'dark' });
    }
  };

  // Si no hay datos de heatmap, usar fallback estático
  const displayHeatmap = heatmapData.length > 0 ? heatmapData : [
    { name: '00:00', val: 0 }, { name: '03:00', val: 0 }, { name: '06:00', val: 0 },
    { name: '09:00', val: 0 }, { name: '12:00', val: 0 }, { name: '15:00', val: 0 },
    { name: '18:00', val: 0 }, { name: '21:00', val: 0 },
  ];

  return (
    <div className="alerts-page">
      <div className="alerts-header-area mb-5">
        <div className="d-flex justify-content-between align-items-end">
          <div>
            <h1 className="alerts-title">Amenazas Activas</h1>
            <p className="alerts-subtitle">ANÁLISIS HEURÍSTICO EN TIEMPO REAL DEL TRÁFICO EXTERNO</p>
          </div>
          <div className="summary-boxes-container">
            <div className="summary-box critical">
              <span className="label">CRÍTICO</span>
              <span className="value">{String(summaryStats.critical).padStart(2, '0')}</span>
            </div>
            <div className="summary-box warning">
              <span className="label">ADVERTENCIA</span>
              <span className="value">{String(summaryStats.warning).padStart(2, '0')}</span>
            </div>
            <div className="summary-box info">
              <span className="label">INFO</span>
              <span className="value">{String(summaryStats.info).padStart(2, '0')}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="threat-list-container mb-5">
        {threatCards.length > 0 ? (
          threatCards.map((card, index) => (
            <div key={card.id || index} className={`threat-card ${card.borderClass} ${index > 0 ? 'mt-3' : ''}`}>
              <div className="card-left">
                <div className={`icon-box ${card.severity === 'critical' ? 'red' : card.severity === 'warning' ? 'yellow' : 'cyan'}`}>
                  <card.IconComponent size={20} />
                </div>
                <div className="threat-info">
                  <div className="d-flex align-items-center gap-3">
                    <Badge className={card.badgeClass}>{card.severityLabel}</Badge>
                    <h5 className="m-0">{card.title}</h5>
                  </div>
                  <div className="threat-meta mt-2">
                    <span>ORIGEN: <span className={card.severity === 'critical' ? 'text-pink' : card.severity === 'warning' ? 'text-yellow' : 'text-cyan'}>{card.sourceIp}</span></span>
                    <span className="ms-4">OBJETIVO: <span className="text-cyan">{card.destIp}</span></span>
                    <span className="ms-4">CONFIANZA: <span className="text-white">{card.confidence}%</span></span>
                  </div>
                </div>
              </div>
              <div className="card-right">
                <span className="time-ago">DETECTADO {card.timeAgo}</span>
                <div className="action-buttons">
                  {card.actionTaken && card.actionTaken.includes('BLOCKED') ? (
                    <button className="btn-details" disabled>BLOQUEADO</button>
                  ) : (
                    <>
                      <button className="btn-quarantine" onClick={() => handleBlockIp(card.sourceIp, card.title)}>CUARENTENA</button>
                      <button className="btn-details">DETALLES</button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="threat-card info-border">
            <div className="card-left">
              <div className="icon-box cyan"><Activity size={20} /></div>
              <div className="threat-info">
                <div className="d-flex align-items-center gap-3">
                  <Badge className="badge-cyan">NOMINAL</Badge>
                  <h5 className="m-0">Sin amenazas activas detectadas</h5>
                </div>
                <div className="threat-meta mt-2">
                  <span className="text-muted">El sistema está monitoreando el tráfico de red. Las amenazas aparecerán aquí automáticamente.</span>
                </div>
              </div>
            </div>
            <div className="card-right">
              <span className="time-ago">EN VIVO</span>
            </div>
          </div>
        )}
      </div>

      <Row className="g-4 mt-5">
        <Col lg={8}>
          <div className="cyber-widget">
            <div className="widget-header">
              <h5 className="m-0">MAPA DE CALOR DE TRÁFICO: ÚLTIMAS 24H</h5>
            </div>
            <div className="chart-area mt-4" style={{ height: '250px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={displayHeatmap}>
                  <XAxis dataKey="name" stroke="#555" fontSize={10} />
                  <Tooltip 
                    cursor={{fill: 'rgba(255,255,255,0.05)'}}
                    contentStyle={{background: '#0d1117', border: '1px solid #333'}}
                    formatter={(value) => [`${value} eventos`, 'Cantidad']}
                  />
                  <Bar dataKey="val">
                    {displayHeatmap.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.val > 10 ? '#ff0055' : '#00f0ff'} fillOpacity={0.6} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="d-flex justify-content-between mt-3 text-muted" style={{fontSize: '0.65rem', letterSpacing: '1px'}}>
                <span>00:00 UTC</span>
                <span className="text-pink">VENTANA MÁXIMA DE BRECHA</span>
                <span>23:59 UTC</span>
              </div>
            </div>
          </div>
        </Col>
        <Col lg={4}>
          <div className="cyber-widget h-100">
            <div className="widget-header">
              <h5 className="m-0">ESTADO DE MITIGACIÓN NEURAL</h5>
            </div>
            <div className="mitigation-status-area mt-4">
              <div className="status-progress-item mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <span className="label">Escudos Activos</span>
                  <span className="value text-cyan">{mitigationStats.shields}%</span>
                </div>
                <div className="cyber-progress">
                  <div className="progress-bar cyan" style={{width: `${mitigationStats.shields}%`}}></div>
                </div>
              </div>
              <div className="status-progress-item mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <span className="label">Supresión de Amenazas</span>
                  <span className="value text-pink">{mitigationStats.suppression}%</span>
                </div>
                <div className="cyber-progress">
                  <div className="progress-bar pink" style={{width: `${mitigationStats.suppression}%`}}></div>
                </div>
              </div>
              <p className="footer-note mt-4">
                {mitigationStats.shields > 70 
                  ? 'El motor neural está mitigando amenazas exitosamente.'
                  : mitigationStats.shields > 30
                  ? 'Mitigación parcial activa. Se recomienda revisión manual.'
                  : 'Nivel de mitigación bajo. Iniciar procedimiento de respuesta.'}
              </p>
              <button className="emergency-flush-btn mt-3">
                PURGADO DE EMERGENCIA
              </button>
            </div>
          </div>
        </Col>
      </Row>

      <div className="alerts-footer-info mt-4 d-flex justify-content-between align-items-center">
        <div className="status-pill">
          <div className="dot green-pulse"></div>
          FLUJO_EN_VIVO_ON
        </div>
        <div className="stats-pills d-flex gap-4">
          <div className="stat-pill">EVENTOS PROCESADOS: <span className="text-cyan">{(summaryStats.critical + summaryStats.warning + summaryStats.info).toLocaleString()}</span></div>
          <div className="stat-pill">IPs BLOQUEADAS: <span className="text-pink">{String(threatCards.filter(c => c.actionTaken?.includes('BLOCKED')).length).padStart(2, '0')}</span></div>
        </div>
      </div>
    </div>
  );
}
