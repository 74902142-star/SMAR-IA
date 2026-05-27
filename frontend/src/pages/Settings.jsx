import { useState, useContext } from 'react';
import { Row, Col } from 'react-bootstrap';
import { Cpu, Bell, Palette, RefreshCcw, Save, Clock, Lock, Info, Shield, Activity, Moon, Sun } from 'lucide-react';
import { toast } from 'react-toastify';
import { ThemeContext } from '../context/ThemeContext';

export default function Settings() {
  const [autonomy, setAutonomy]       = useState(78);
  const [neon, setNeon]               = useState(80);
  const [schema, setSchema]           = useState('blue');
  const [adaptiveReasoning, setAdaptive] = useState(true);
  const [predictiveDeletion, setPredictive] = useState(false);
  const [thresholds, setThresholds] = useState({ breaches: true, discrepancy: false, latency: true });

  const { theme, setTheme } = useContext(ThemeContext);

  const handleSave = () => {
    toast.success('Configuración guardada correctamente', {
      position: 'bottom-right', autoClose: 3000,
    });
  };

  const handleReset = () => {
    setAutonomy(78); setNeon(80); setSchema('blue');
    setAdaptive(true); setPredictive(false);
    setThresholds({ breaches: true, discrepancy: false, latency: true });
    toast.info('Valores restablecidos', { position: 'bottom-right' });
  };

  const autonomyLabel =
    autonomy >= 95 ? 'ILIMITADO' :
    autonomy >= 66 ? 'AUTÓNOMO'  :
    autonomy >= 33 ? 'SUPERVISADO' : 'PASIVO';

  const autonomyColor =
    autonomy >= 95 ? 'var(--rose)' :
    autonomy >= 66 ? 'var(--blue)' :
    autonomy >= 33 ? 'var(--cyan)' : 'var(--emerald)';

  const colors = ['blue', 'rose', 'amber', 'emerald', 'cyan'];

  return (
    <div className="settings-page">
      {/* ── Header ── */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1>Configuración</h1>
          <p>Parámetros de comportamiento del motor cognitivo SMAR-IA</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn-outline" onClick={handleReset}>
            <RefreshCcw size={14} /> Restablecer
          </button>
          <button className="btn-primary-custom" onClick={handleSave}>
            <Save size={14} /> Guardar Cambios
          </button>
        </div>
      </div>

      <Row className="g-3">
        {/* ── Theme Control ── */}
        <Col lg={12}>
          <div className="settings-card">
            <div className="settings-card-header">
              <Palette size={17} style={{ color: 'var(--cyan)' }} />
              <h5 style={{ color: 'var(--cyan)' }}>Modo de Tema</h5>
            </div>
            <div className="settings-card-body" style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
              {[
                { value: 'dark', icon: Moon, label: 'Oscuro' },
                { value: 'light', icon: Sun, label: 'Claro' },
              ].map(({ value, icon: Icon, label }) => (
                <button
                  key={value}
                  type="button"
                  className={`theme-option ${theme === value ? 'active' : ''}`}
                  onClick={() => setTheme(value)}
                >
                  <Icon size={18} />
                  {label}
                </button>
              ))}
            </div>
          </div>
        </Col>

        {/* ── AI Autonomy ── */}
        <Col lg={8}>
          <div className="settings-card">
            <div className="settings-card-header">
              <Cpu size={17} style={{ color: 'var(--blue)' }} />
              <h5>Nivel de Autonomía IA</h5>
              <span className="badge-pill blue" style={{ marginLeft: 'auto' }}>
                {autonomy}% · {autonomyLabel}
              </span>
            </div>
            <div className="settings-card-body">
              {/* Autonomy slider */}
              <div style={{ marginBottom: 32 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, fontSize: '0.75rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Nivel de agencia neural</span>
                  <span style={{ color: autonomyColor, fontFamily: "'Space Mono',monospace", fontWeight: 700 }}>
                    {autonomy}%
                  </span>
                </div>
                <div className="range-track-custom">
                  <div className="range-fill" style={{ width: `${autonomy}%` }} />
                  <input
                    type="range" min="0" max="100" value={autonomy}
                    onChange={e => setAutonomy(Number(e.target.value))}
                    className="styled-range"
                  />
                </div>
                {/* Markers */}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
                  {[
                    { label: 'PASIVO', pos: 0 },
                    { label: 'SUPERVISADO', pos: 33 },
                    { label: 'AUTÓNOMO', pos: 66 },
                    { label: 'ILIMITADO', pos: 95, danger: true },
                  ].map(({ label, pos, danger }) => (
                    <div key={label} style={{ textAlign: 'center' }}>
                      <div style={{
                        width: 6, height: 6, borderRadius: '50%', margin: '0 auto 4px',
                        background: autonomy >= pos ? (danger ? 'var(--rose)' : 'var(--blue)') : 'rgba(255,255,255,0.15)',
                        boxShadow: autonomy >= pos ? `0 0 8px ${danger ? 'var(--rose-glow)' : 'var(--blue-glow)'}` : 'none',
                      }} />
                      <span style={{ fontSize: '0.6rem', color: danger ? 'var(--rose)' : 'var(--text-muted)', letterSpacing: '0.5px' }}>{label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Feature toggles */}
              <div style={{ fontSize: '0.68rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 12, fontWeight: 700 }}>
                CARACTERÍSTICAS AVANZADAS
              </div>
              <Row className="g-3">
                {[
                  {
                    key: 'adaptive', label: 'Razonamiento Adaptativo',
                    desc: 'Permite recalibrar rutas lógicas basadas en metadatos ambientales entrantes.',
                    value: adaptiveReasoning, toggle: () => setAdaptive(v => !v),
                  },
                  {
                    key: 'predictive', label: 'Eliminación Predictiva',
                    desc: 'Habilita la purga automática de logs de baja prioridad sin aviso al operador.',
                    value: predictiveDeletion, toggle: () => setPredictive(v => !v),
                  },
                ].map(({ key, label, desc, value, toggle }) => (
                  <Col key={key} md={6}>
                    <div className={`feature-toggle-box ${value ? 'active' : ''}`} onClick={toggle}>
                      <label className="toggle-wrapper" onClick={e => e.stopPropagation()}>
                        <input type="checkbox" checked={value} onChange={toggle} />
                        <span className="toggle-slider" />
                      </label>
                      <div className="feature-toggle-box-info">
                        <h6>{label}</h6>
                        <p>{desc}</p>
                      </div>
                    </div>
                  </Col>
                ))}
              </Row>

              {/* Decorative CPU icon */}
              <div style={{ position: 'absolute', right: 24, bottom: 24, opacity: 0.04 }}>
                <Cpu size={120} strokeWidth={0.5} />
              </div>
            </div>
          </div>
        </Col>

        {/* ── Core Diagnostics ── */}
        <Col lg={4}>
          <div className="settings-card" style={{ height: '100%' }}>
            <div className="settings-card-header">
              <Shield size={17} style={{ color: 'var(--cyan)' }} />
              <h5 style={{ color: 'var(--cyan)' }}>Diagnóstico Núcleo</h5>
            </div>
            <div className="settings-card-body" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div className="diag-gauge-outer">
                <div className="diag-gauge-inner">
                  <div className="diag-score">99.8</div>
                  <div className="diag-score-label">COHERENCIA</div>
                </div>
              </div>

              <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 10 }}>
                {[
                  { icon: Activity, label: 'Motor Neural',   status: 'ACTIVO',      color: 'emerald' },
                  { icon: Shield,   label: 'Módulo ML',      status: 'CARGADO',     color: 'blue' },
                  { icon: Activity, label: 'API Backend',    status: 'EN LÍNEA',    color: 'emerald' },
                ].map(({ icon: Icon, label, status, color }) => (
                  <div key={label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(0,0,0,0.2)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.78rem' }}>
                      <Icon size={14} style={{ color: `var(--${color})` }} />
                      <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
                    </div>
                    <span className={`badge-pill ${color}`}>{status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Col>

        {/* ── Notification Thresholds ── */}
        <Col lg={6}>
          <div className="settings-card">
            <div className="settings-card-header">
              <Bell size={17} style={{ color: 'var(--amber)' }} />
              <h5>Umbrales de Notificación</h5>
            </div>
            <div className="settings-card-body">
              <div style={{ marginBottom: 20 }}>
                {[
                  { key: 'breaches',    label: 'Brechas Críticas del Sistema',   priority: 'p1' },
                  { key: 'discrepancy', label: 'Discrepancia Ambiental',         priority: 'p3' },
                  { key: 'latency',     label: 'Latencia del Nodo de Red',       priority: 'p5' },
                ].map(({ key, label, priority }) => (
                  <div key={key} className="threshold-row">
                    <span className="threshold-name">{label}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                      <span className={`threshold-priority ${priority}`}>
                        {priority === 'p1' ? 'PRIORIDAD 1' : priority === 'p3' ? 'PRIORIDAD 3' : 'PRIORIDAD 5'}
                      </span>
                      <label className="toggle-wrapper">
                        <input
                          type="checkbox"
                          checked={thresholds[key]}
                          onChange={() => setThresholds(prev => ({ ...prev, [key]: !prev[key] }))}
                        />
                        <span className="toggle-slider" />
                      </label>
                    </div>
                  </div>
                ))}
              </div>

              {/* Alert pattern */}
              <div style={{ fontSize: '0.68rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 12, fontWeight: 700 }}>
                PATRÓN DE ALERTA
              </div>
              <div style={{ display: 'flex', gap: 10 }}>
                {['CONTINUO', 'PULSO', 'RÁFAGA'].map((p, i) => (
                  <div
                    key={p}
                    style={{
                      flex: 1, padding: '10px', textAlign: 'center',
                      background: i === 0 ? 'rgba(59,130,246,0.1)' : 'rgba(0,0,0,0.2)',
                      border: `1px solid ${i === 0 ? 'rgba(59,130,246,0.3)' : 'var(--border-subtle)'}`,
                      borderRadius: 'var(--radius-sm)', fontSize: '0.65rem', letterSpacing: '1px',
                      color: i === 0 ? 'var(--blue)' : 'var(--text-muted)', cursor: 'pointer',
                      fontWeight: i === 0 ? 700 : 400,
                    }}
                  >
                    {p}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Col>

        {/* ── Interface Customization ── */}
        <Col lg={6}>
          <div className="settings-card">
            <div className="settings-card-header">
              <Palette size={17} style={{ color: 'var(--cyan)' }} />
              <h5 style={{ color: 'var(--cyan)' }}>Personalización de Interfaz</h5>
            </div>
            <div className="settings-card-body">
              {/* Neon intensity */}
              <div style={{ marginBottom: 28 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10, fontSize: '0.75rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Intensidad de Neón</span>
                  <span style={{ color: 'var(--cyan)', fontFamily: "'Space Mono',monospace", fontWeight: 700 }}>{neon}%</span>
                </div>
                <div className="range-track-custom">
                  <div className="range-fill" style={{ width: `${neon}%`, background: 'linear-gradient(90deg, var(--cyan), var(--blue))' }} />
                  <input
                    type="range" min="0" max="100" value={neon}
                    onChange={e => setNeon(Number(e.target.value))}
                    className="styled-range"
                  />
                </div>
              </div>

              {/* Color schema */}
              <div style={{ marginBottom: 24 }}>
                <div style={{ fontSize: '0.68rem', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 14, fontWeight: 700 }}>
                  ESQUEMA DE COLOR
                </div>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                  {colors.map(c => (
                    <div
                      key={c}
                      className={`color-swatch ${c} ${schema === c ? 'active' : ''}`}
                      onClick={() => setSchema(c)}
                      title={c.charAt(0).toUpperCase() + c.slice(1)}
                    />
                  ))}
                  <span style={{ marginLeft: 8, fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                    {schema}
                  </span>
                </div>
              </div>

              {/* Info note */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, padding: '12px 14px', background: 'rgba(6,182,212,0.05)', border: '1px solid rgba(6,182,212,0.15)', borderRadius: 'var(--radius-sm)' }}>
                <Info size={15} style={{ color: 'var(--cyan)', flexShrink: 0, marginTop: 1 }} />
                <p style={{ margin: 0, fontSize: '0.73rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  Intensidades de neón más altas pueden afectar la fatiga visual durante ciclos operativos prolongados.
                </p>
              </div>
            </div>
          </div>
        </Col>
      </Row>

      {/* ── Footer ── */}
      <div className="settings-footer">
        <div className="settings-footer-item">
          <span className="status-dot green" />
          <span>SINCRONIZACIÓN NUBE: ACTIVA</span>
        </div>
        <div className="settings-footer-item">
          <Clock size={13} />
          <span>ÚLTIMO CAMBIO: {new Date().toLocaleDateString('es-PE')} · {new Date().toLocaleTimeString('es-PE', { hour12: false })}</span>
        </div>
        <div className="settings-footer-item">
          <Lock size={13} />
          <span>SESIÓN: CAPA ENCRIPTADA TLS 1.3</span>
        </div>
      </div>
    </div>
  );
}
