import { useState } from 'react';
import { Row, Col, Form, Button } from 'react-bootstrap';
import { Settings as SettingsIcon, Cpu, Bell, Palette, Activity, RefreshCcw, Save, Cloud, 
  Clock, 
  Lock,
  Info
} from 'lucide-react';
import { toast } from 'react-toastify';

export default function Settings() {
  const [autonomy, setAutonomy] = useState(78);
  const [neonIntensity, setNeonIntensity] = useState(100);
  const [visualSchema, setVisualSchema] = useState('pink');
  const [adaptiveReasoning, setAdaptiveReasoning] = useState(true);
  const [predictiveDeletion, setPredictiveDeletion] = useState(false);
  
  const [thresholds, setThresholds] = useState({
    breaches: true,
    discrepancy: false,
    latency: true
  });

  const handleSave = () => {
    toast.success('CONFIGURACIÓN ACTUALIZADA CORRECTAMENTE', {
      position: "bottom-right",
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      theme: "dark",
      style: {
        border: '1px solid #ff0055',
        backgroundColor: '#0d1117',
        color: '#fff',
        fontFamily: "'Space Mono', monospace"
      }
    });
  };

  const handleReset = () => {
    setAutonomy(78);
    setNeonIntensity(100);
    setVisualSchema('pink');
    setAdaptiveReasoning(true);
    setPredictiveDeletion(false);
    toast.info('VALORES RESTABLECIDOS POR DEFECTO');
  };

  return (
    <div className="settings-page">
      <div className="settings-header d-flex justify-content-between align-items-end mb-5">
        <div className="header-text">
          <h1 className="cyber-title mb-2">SYSTEM_PREFERENCES</h1>
          <p className="cyber-subtitle text-secondary">
            Modifica los parámetros de comportamiento del motor cognitivo SMAR-IA. 
            Los cambios se aplican en tiempo real a través de la red neural.
          </p>
        </div>
        <div className="header-actions d-flex gap-3">
          <button className="cyber-btn-outline" onClick={handleReset}>
            <RefreshCcw size={16} className="me-2" /> REABLECER
          </button>
          <button className="cyber-btn-primary pink" onClick={handleSave}>
            <Save size={16} className="me-2" /> GUARDAR CAMBIOS
          </button>
        </div>
      </div>

      <Row className="g-4">
        {/* AI Autonomy Level */}
        <Col lg={8}>
          <div className="cyber-card settings-card highlight-card">
            <div className="card-header-cyber">
              <Cpu size={20} className="text-pink me-2" />
              <h5 className="m-0">NIVEL DE AUTONOMÍA IA</h5>
            </div>
            
            <div className="autonomy-selector-container my-5">
              <div className="d-flex justify-content-between mb-3">
                <span className="label-sm text-pink">AGENCIA NEURAL</span>
                <span className="label-sm text-pink">{autonomy}% - AGENCIA AVANZADA</span>
              </div>
              <div className="autonomy-track">
                <div className="autonomy-fill" style={{ width: `${autonomy}%` }}></div>
                <div className="track-markers">
                  <div className={`marker ${autonomy >= 0 ? 'active' : ''}`}><span className="marker-label">PASIVO</span></div>
                  <div className={`marker ${autonomy >= 33 ? 'active' : ''}`}><span className="marker-label">SUPERVISADO</span></div>
                  <div className={`marker ${autonomy >= 66 ? 'active' : ''}`}><span className="marker-label">AUTÓNOMO</span></div>
                  <div className={`marker ${autonomy >= 95 ? 'active' : ''}`}><span className="marker-label text-red">ILIMITADO</span></div>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={autonomy} 
                  onChange={(e) => setAutonomy(e.target.value)}
                  className="autonomy-input"
                />
              </div>
            </div>

            <Row className="mt-5">
              <Col md={6}>
                <div className={`feature-box ${adaptiveReasoning ? 'active' : ''}`} onClick={() => setAdaptiveReasoning(!adaptiveReasoning)}>
                  <div className="checkbox-custom">
                    {adaptiveReasoning && <div className="check-mark"></div>}
                  </div>
                  <div className="feature-info">
                    <h6>Razonamiento Adaptativo</h6>
                    <p>Permite a la IA recalibrar rutas lógicas basadas en metadatos ambientales entrantes.</p>
                  </div>
                </div>
              </Col>
              <Col md={6}>
                <div className={`feature-box ${predictiveDeletion ? 'active' : ''}`} onClick={() => setPredictiveDeletion(!predictiveDeletion)}>
                  <div className="checkbox-custom">
                    {predictiveDeletion && <div className="check-mark"></div>}
                  </div>
                  <div className="feature-info">
                    <h6>Eliminación Predictiva</h6>
                    <p>Habilita la purga automática de logs de caché de baja prioridad sin aviso al operador.</p>
                  </div>
                </div>
              </Col>
            </Row>
            
            <div className="card-decoration-brain">
               <Cpu size={120} strokeWidth={0.5} />
            </div>
          </div>
        </Col>

        {/* Core Diagnostics */}
        <Col lg={4}>
          <div className="cyber-card settings-card diagnostic-card">
            <div className="card-header-cyber">
              <h5 className="m-0 text-cyan">DIAGNÓSTICO NÚCLEO</h5>
            </div>
            
            <div className="diagnostic-gauge-wrapper">
              <div className="gauge-outer">
                <div className="gauge-inner">
                  <div className="score-value text-cyan">99.8</div>
                  <div className="score-label">PUNTUACIÓN COHERENCIA</div>
                </div>
                <div className="gauge-progress"></div>
              </div>
              <div className="gauge-decoration"></div>
            </div>

            <div className="diagnostic-links mt-auto">
              <div className="diag-link">
                <Activity size={16} /> <span>SOPORTE</span>
              </div>
              <div className="diag-link">
                <SettingsIcon size={16} /> <span>REGISTROS</span>
              </div>
            </div>
          </div>
        </Col>

        {/* Notification Thresholds */}
        <Col lg={6}>
          <div className="cyber-card settings-card">
            <div className="card-header-cyber">
              <Bell size={20} className="text-yellow me-2" />
              <h5 className="m-0">UMBRALES DE NOTIFICACIÓN</h5>
            </div>
            
            <div className="threshold-list mt-4">
              <div className="threshold-item d-flex align-items-center justify-content-between mb-4">
                <div className="item-info">
                  <span className="item-label">Brechas Críticas del Sistema</span>
                </div>
                <div className="item-controls d-flex align-items-center gap-3">
                  <span className="priority-tag p1">PRIORIDAD 1</span>
                  <Form.Check 
                    type="switch"
                    id="breach-switch"
                    checked={thresholds.breaches}
                    onChange={() => setThresholds({...thresholds, breaches: !thresholds.breaches})}
                    className="cyber-switch"
                  />
                </div>
              </div>

              <div className="threshold-item d-flex align-items-center justify-content-between mb-4">
                <div className="item-info">
                  <span className="item-label">Discrepancia Ambiental</span>
                </div>
                <div className="item-controls d-flex align-items-center gap-3">
                  <span className="priority-tag p3">PRIORIDAD 3</span>
                  <Form.Check 
                    type="switch"
                    id="discrepancy-switch"
                    checked={thresholds.discrepancy}
                    onChange={() => setThresholds({...thresholds, discrepancy: !thresholds.discrepancy})}
                    className="cyber-switch"
                  />
                </div>
              </div>

              <div className="threshold-item d-flex align-items-center justify-content-between mb-4">
                <div className="item-info">
                  <span className="item-label">Latencia del Nodo de Red</span>
                </div>
                <div className="item-controls d-flex align-items-center gap-3">
                  <span className="priority-tag p5">PRIORIDAD 5</span>
                  <Form.Check 
                    type="switch"
                    id="latency-switch"
                    checked={thresholds.latency}
                    onChange={() => setThresholds({...thresholds, latency: !thresholds.latency})}
                    className="cyber-switch"
                  />
                </div>
              </div>
            </div>

            <div className="vibration-pattern mt-5">
              <span className="label-sm d-block mb-3">PATRÓN DE VIBRACIÓN DE ALERTA</span>
              <div className="pattern-selector">
                <div className="pattern-option active">
                   <div className="pattern-visual p-rect"></div>
                </div>
                <div className="pattern-option">
                   <div className="pattern-visual p-dots"></div>
                </div>
              </div>
            </div>
          </div>
        </Col>

        {/* Interface Customization */}
        <Col lg={6}>
          <div className="cyber-card settings-card customization-card">
            <div className="card-header-cyber">
              <Palette size={20} className="text-cyan me-2" />
              <h5 className="m-0 text-cyan">PERSONALIZACIÓN DE INTERFAZ</h5>
            </div>

            <div className="custom-control mb-5 mt-4">
              <div className="d-flex justify-content-between mb-2">
                <span className="label-sm">INTENSIDAD NEÓN</span>
                <span className="label-sm text-cyan">MÁX</span>
              </div>
              <div className="range-slider-wrapper">
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={neonIntensity} 
                  onChange={(e) => setNeonIntensity(e.target.value)}
                  className="cyber-range-input"
                />
                <div className="range-glow" style={{ width: `${neonIntensity}%` }}></div>
              </div>
            </div>

            <div className="custom-control mb-5">
              <span className="label-sm d-block mb-3">ESQUEMA VISUAL</span>
              <div className="schema-selector d-flex gap-4">
                <div 
                  className={`schema-option pink ${visualSchema === 'pink' ? 'active' : ''}`}
                  onClick={() => setVisualSchema('pink')}
                >
                  <div className="color-strip"></div>
                </div>
                <div 
                  className={`schema-option cyan ${visualSchema === 'cyan' ? 'active' : ''}`}
                  onClick={() => setVisualSchema('cyan')}
                >
                  <div className="color-strip"></div>
                </div>
                <div 
                  className={`schema-option yellow ${visualSchema === 'yellow' ? 'active' : ''}`}
                  onClick={() => setVisualSchema('yellow')}
                >
                  <div className="color-strip"></div>
                </div>
              </div>
            </div>

            <div className="alert-box-info">
              <Info size={16} className="text-cyan me-3 flex-shrink-0" />
              <p className="m-0 small">
                Las intensidades de neón más altas pueden afectar la fatiga sináptica durante ciclos operativos prolongados.
              </p>
            </div>
          </div>
        </Col>
      </Row>

      <footer className="settings-footer mt-5">
        <div className="footer-status-item">
          <div className="status-dot green"></div>
          <span>SINCRONIZACIÓN NUBE: SINCRONIZADO</span>
        </div>
        <div className="footer-status-item">
          <Clock size={14} />
          <span>ÚLTIMO CAMBIO: 12.04.2044 // 04:32</span>
        </div>
        <div className="footer-status-item">
          <Lock size={14} />
          <span>SESIÓN: CAPA ENCRIPTADA 7</span>
        </div>
      </footer>
    </div>
  );
}
