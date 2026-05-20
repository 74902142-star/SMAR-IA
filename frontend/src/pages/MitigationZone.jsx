import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Row, Col, Table, Button, Form, Modal, Badge } from 'react-bootstrap';
import { ShieldAlert, Zap, Lock, Terminal, Activity, Bug, Radio, CheckCircle, AlertTriangle } from 'lucide-react';
import { toast } from 'react-toastify';
import { BarChart, Bar, ResponsiveContainer, Cell } from 'recharts';

export default function MitigationZone() {
  const [suspiciousIps, setSuspiciousIps] = useState([]);
  const { token } = useContext(AuthContext);
  const [activeIncident, setActiveIncident] = useState(null);

  const fetchSuspicious = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/mitigation/suspicious', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSuspiciousIps(data);
        if (data.length > 0 && !activeIncident) {
          setActiveIncident(data[0]);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchSuspicious();
    const interval = setInterval(fetchSuspicious, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleMitigate = async (ip, action, port = null) => {
    try {
      const payload = {
        ip: ip,
        action: action,
        port: port,
        attack_type: "IA Recommended Mitigation"
      };

      const res = await fetch('http://localhost:8000/api/mitigation/block', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        toast.success(`Protocolo ${action} ejecutado con éxito`, { theme: "dark" });
        fetchSuspicious();
      } else {
        toast.error("Error al ejecutar protocolo de seguridad");
      }
    } catch (e) {
      toast.error("Fallo de conexión con el núcleo");
    }
  };

  const trendData = [
    { v: 10 }, { v: 15 }, { v: 8 }, { v: 25 }, { v: 12 }
  ];

  return (
    <div className="mitigation-page">
      <div className="matrix-header d-flex justify-content-between align-items-start mb-4">
        <div>
          <h1 className="matrix-title">Matriz_de_Amenazas_Activa</h1>
          <p className="matrix-subtitle">Incidente: #TK-8829 | Prioridad: <span className="text-pink">CRÍTICA</span></p>
        </div>
        <div className="header-stats-boxes d-flex gap-3">
          <div className="mini-stat-box">
            <span className="label">UPTIME</span>
            <span className="value text-cyan">99.98%</span>
          </div>
          <div className="mini-stat-box">
            <span className="label">LATENCIA</span>
            <span className="value text-yellow">12ms</span>
          </div>
        </div>
      </div>

      <Row className="g-4">
        <Col lg={7}>
          <div className="cyber-panel incursion-profile">
            <div className="panel-header">
              <Radio size={16} className="text-pink me-2" />
              <span>PERFIL_DE_INCURSIÓN</span>
              <span className="ms-auto text-muted small">LIVE FEED // SEÑAL: 92%</span>
            </div>
            <div className="panel-body text-center py-5">
              <div className="bug-icon-container mb-4">
                <Bug size={80} className="text-pink-glow" />
                <div className="scanning-line"></div>
              </div>
              <p className="status-text text-muted mb-5">FLUJOS_DE_PAQUETES_ENCRIPTADOS</p>
              
              <div className="profile-details-grid text-start px-4">
                <div className="detail-item">
                  <span className="label">NODO_ORIGEN</span>
                  <span className="value text-cyan">{activeIncident?.ip || "192.168.1.104"} (SHINJUKU_DISTRICT)</span>
                </div>
                <div className="detail-item">
                  <span className="label">FIRMA</span>
                  <span className="value text-yellow">POLYMORPHIC_WORM_V3</span>
                </div>
                <div className="detail-item">
                  <span className="label">VECTOR_ATAQUE</span>
                  <span className="value text-pink">L7_APPLICATION_EXPLOIT</span>
                </div>
                <div className="detail-item">
                  <span className="label">ÍNDICE_RIESGO</span>
                  <span className="value text-pink">9.8 / 10.0</span>
                </div>
              </div>

              <div className="terminal-log-area mt-5 text-start">
                <div className="log-line info">[14:02:11] INICIALIZANDO INSPECCIÓN PROFUNDA DE PAQUETES...</div>
                <div className="log-line warning">[14:02:14] DESAJUSTE DE CABECERA DETECTADO EN PUERTO 443</div>
                <div className="log-line alert">[14:02:15] ADVERTENCIA: INTENTO DE EJECUCIÓN NO IDENTIFICADO</div>
                <div className="log-line info">[14:02:17] REDIRIGIENDO TRÁFICO A HONEYPOT_DELTA_9</div>
                <div className="log-line success">[14:02:19] ANALIZANDO COMPORTAMIENTO... MOTOR LISTO.</div>
                <div className="log-line blink mt-2">{">"} ESPERANDO DESPLIEGUE DE MITIGACIÓN...</div>
              </div>
            </div>
          </div>
        </Col>

        <Col lg={5}>
          <div className="cyber-panel ia-recommendations h-100">
            <div className="panel-header">
              <Activity size={16} className="text-cyan me-2" />
              <span>RECOMENDACIONES IA</span>
              <div className="header-dots ms-auto">
                <div className="dot cyan"></div>
                <div className="dot cyan"></div>
                <div className="dot cyan"></div>
              </div>
            </div>
            <div className="panel-body p-4">
              {/* Rec 1 */}
              <div className="rec-card mb-4">
                <div className="d-flex gap-3">
                  <div className="rec-icon cyan"><ShieldAlert size={24} /></div>
                  <div className="rec-content">
                    <div className="d-flex justify-content-between">
                      <h6 className="m-0">AISLAMIENTO POR FIREWALL</h6>
                      <Badge className="badge-cyan">RECOMENDADO</Badge>
                    </div>
                    <span className="prob">PROBABILIDAD ÉXITO: 94%</span>
                    <p className="mt-2 text-muted small">Ajustar reglas para aislar la IP origen. Evita el movimiento lateral mientras preserva servicios internos.</p>
                    <button 
                      className="btn-matrix-cyan w-100 mt-2"
                      onClick={() => handleMitigate(activeIncident?.ip, "BLOCK_IP")}
                    >
                      EJECUTAR AISLAMIENTO
                    </button>
                  </div>
                </div>
              </div>

              {/* Rec 2 */}
              <div className="rec-card mb-4 border-pink-subtle">
                <div className="d-flex gap-3">
                  <div className="rec-icon pink"><Zap size={24} /></div>
                  <div className="rec-content">
                    <h6 className="m-0">TERMINAR CONEXIÓN</h6>
                    <span className="prob">PROBABILIDAD ÉXITO: 100%</span>
                    <p className="mt-2 text-muted small">Reinicio forzado del puerto objetivo. Advertencia: Causará una breve interrupción en servicios asociados.</p>
                    <button 
                      className="btn-matrix-pink w-100 mt-2"
                      onClick={() => handleMitigate(activeIncident?.ip, "CLOSE_TCP", 443)}
                    >
                      TERMINAR AHORA
                    </button>
                  </div>
                </div>
              </div>

              {/* Rec 3 */}
              <div className="rec-card border-yellow-subtle">
                <div className="d-flex gap-3">
                  <div className="rec-icon yellow"><Lock size={24} /></div>
                  <div className="rec-content">
                    <h6 className="m-0">ENCRIPTAR SEGMENTO</h6>
                    <span className="prob">PROBABILIDAD ÉXITO: 88%</span>
                    <p className="mt-2 text-muted small">Aplicar capa resistente a cuántica al segmento comprometido. Medida preventiva de protección.</p>
                    <button className="btn-matrix-yellow w-100 mt-2">
                      ACTIVAR ENCRIPTACIÓN
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Col>
      </Row>

      <Row className="g-4 mt-4">
        <Col md={3}>
          <div className="mini-widget">
            <span className="label">TENDENCIA_DETECCIÓN</span>
            <div style={{height: '40px'}} className="mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData}>
                  <Bar dataKey="v" radius={[2, 2, 0, 0]}>
                    {trendData.map((e, i) => (
                      <Cell key={i} fill={i === 3 ? '#ff0055' : '#00f0ff'} fillOpacity={0.5} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Col>
        <Col md={6}>
          <div className="mini-widget d-flex align-items-center gap-4">
            <div className="confidence-icon"><Activity size={24} className="text-pink" /></div>
            <div>
              <span className="label">CONFIANZA_SMAR-IA</span>
              <h3 className="m-0 text-cyan">99.4%</h3>
            </div>
          </div>
        </Col>
        <Col md={3}>
          <div className="mini-widget text-end">
            <span className="label">SEGURIDAD_GLOBAL_RED</span>
            <div className="d-flex justify-content-end gap-1 mt-2">
              <div className="status-dot green"></div>
              <div className="status-dot green"></div>
              <div className="status-dot green"></div>
              <span className="ms-2 small text-muted">382 NODOS SEGUROS</span>
            </div>
          </div>
        </Col>
      </Row>
    </div>
  );
}
