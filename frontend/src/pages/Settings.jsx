import { useState, useEffect, useContext } from 'react';
import { Cpu, Save, Clock, Shield, Activity, Target, Database, Play, RefreshCw, BarChart } from 'lucide-react';
import { toast } from 'react-toastify';
import { AuthContext } from '../context/AuthContext';
import { apiUrl } from '../api';

export default function Settings() {
  const { token } = useContext(AuthContext);
  const [loading, setLoading] = useState(false);
  const [learningRate, setLearningRate] = useState(0.0012);
  const [batchSize, setBatchSize] = useState('64 Muestras');
  const [optimizer, setOptimizer] = useState('AdamW');
  const [dropout, setDropout] = useState(0.25);

  const handleRetrain = () => {
    setLoading(true);
    toast.info("Iniciando reentrenamiento del modelo cognitivo...", { position: "top-center" });
    setTimeout(() => {
      setLoading(false);
      toast.success("Modelo reentrenado con éxito. F1-Score: 0.979", { position: "top-center" });
    }, 2500);
  };

  const handleUpdateThresholds = () => {
    toast.success("Umbrales de clasificación neuronal actualizados correctamente.", { position: "top-center" });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }} className="campus-dashboard">
      
      {/* ── Header ── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 className="white-widget-title" style={{ fontSize: '1.8rem', marginBottom: 4 }}>Configuración del Modelo ML</h1>
          <p className="white-widget-subtitle">Parámetros del modelo, monitoreo de rendimiento y gestión de datos.</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="white-widget-tab" style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 16px', borderRadius: '6px' }} onClick={handleUpdateThresholds}>
            <Settings2Icon size={16} />
            Actualizar Umbrales
          </button>
          <button 
            className="integrity-btn-primary" 
            style={{ display: 'flex', alignItems: 'center', gap: 6, margin: 0, padding: '10px 16px', borderRadius: '6px', background: '#2b0075' }}
            onClick={handleRetrain}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'spin' : ''} />
            Reentrenar Modelo
          </button>
        </div>
      </div>

      {/* ── TOP SECTION: Training Progress & Confusion Matrix ── */}
      <div className="dashboard-layout-row" style={{ gridTemplateColumns: '1.8fr 1fr' }}>
        {/* Left: Progreso de Entrenamiento */}
        <div className="white-widget">
          <div className="white-widget-header">
            <div>
              <h3 className="white-widget-title">Progreso de Entrenamiento</h3>
            </div>
            <div style={{ display: 'flex', gap: 16, fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span className="topology-legend-dot purple" /> Precisión</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span className="topology-legend-dot purple" style={{ opacity: 0.5 }} /> Pérdida</div>
            </div>
          </div>

          {/* Simple custom styled bars representing training epochs */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', height: 180, gap: 12, padding: '10px 0', borderBottom: '1px solid #e2e8f0' }}>
            {[45, 65, 60, 75, 90, 85, 95, 100, 98, 110].map((h, i) => (
              <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'flex-end', gap: 2 }}>
                <div style={{ height: `${h}%`, backgroundColor: i % 2 === 0 ? '#d8b4fe' : '#c084fc', borderRadius: '4px 4px 0 0' }} />
              </div>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginTop: 20, textAlign: 'center' }}>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748b', marginBottom: 4 }}>Época Actual</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1e293b' }}>142<span style={{ fontSize: '0.8rem', color: '#94a3b8' }}> / 200</span></div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748b', marginBottom: 4 }}>Prec. Validación</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1e293b' }}>98.4%</div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748b', marginBottom: 4 }}>Pérdida Global</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#7c3aed' }}>0.024</div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748b', marginBottom: 4 }}>ETA Finalización</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1e293b' }}>14m 20s</div>
            </div>
          </div>
        </div>

        {/* Right: Matriz de Confusión */}
        <div className="white-widget">
          <div className="white-widget-header" style={{ marginBottom: 12 }}>
            <h3 className="white-widget-title">Matriz de Confusión</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, flex: 1, justifyContent: 'center' }}>
            {/* Headers */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', textAlign: 'center', fontSize: '0.72rem', fontWeight: 700, color: '#64748b', marginBottom: -4 }}>
              <div />
              <div>Predicho Pos</div>
              <div>Predicho Neg</div>
            </div>

            {/* Row 1 */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', alignItems: 'center', gap: 10 }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748b', textAlign: 'right', paddingRight: 8 }}>Real Pos</div>
              <div style={{ background: '#2b0075', color: '#ffffff', padding: 12, borderRadius: 6, textAlign: 'center' }}>
                <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>942</div>
                <div style={{ fontSize: '0.55rem', opacity: 0.8, letterSpacing: '0.5px' }}>VERD. POS</div>
              </div>
              <div style={{ background: '#f3f0ff', color: '#7c3aed', padding: 12, borderRadius: 6, textAlign: 'center' }}>
                <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>12</div>
                <div style={{ fontSize: '0.55rem', opacity: 0.8, letterSpacing: '0.5px' }}>FALSO NEG</div>
              </div>
            </div>

            {/* Row 2 */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', alignItems: 'center', gap: 10 }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748b', textAlign: 'right', paddingRight: 8 }}>Real Neg</div>
              <div style={{ background: '#f3f0ff', color: '#7c3aed', padding: 12, borderRadius: 6, textAlign: 'center' }}>
                <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>28</div>
                <div style={{ fontSize: '0.55rem', opacity: 0.8, letterSpacing: '0.5px' }}>FALSO POS</div>
              </div>
              <div style={{ background: '#2b0075', color: '#ffffff', padding: 12, borderRadius: 6, textAlign: 'center' }}>
                <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>1,840</div>
                <div style={{ fontSize: '0.55rem', opacity: 0.8, letterSpacing: '0.5px' }}>VERD. NEG</div>
              </div>
            </div>

            <div style={{ borderTop: '1px solid #cbd5e1', paddingTop: 12, marginTop: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 700, color: '#334155', marginBottom: 4 }}>
                <span>F1-Score</span>
                <span style={{ color: '#2b0075' }}>0.979</span>
              </div>
              <div className="prog-bar-track" style={{ height: 6, backgroundColor: '#f1f5f9' }}>
                <div className="prog-bar-fill" style={{ width: '97.9%', height: '100%', backgroundColor: '#2b0075', borderRadius: '3px' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── MIDDLE SECTION: ML Analysis & Data Management ── */}
      <div className="dashboard-layout-row" style={{ gridTemplateColumns: '1fr 1.8fr' }}>
        {/* Left: Deep Purple ML Analysis Card */}
        <div className="white-widget" style={{ background: '#2b0075', color: '#ffffff', gap: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={18} style={{ color: '#c084fc' }} />
            <h3 className="white-widget-title" style={{ color: '#ffffff', margin: 0 }}>Análisis ML</h3>
          </div>

          <p style={{ fontSize: '0.82rem', color: '#d8b4fe', lineHeight: 1.6, margin: 0 }}>
            "El modelo actual muestra alta sensibilidad a <strong>patrones DDoS</strong> pero presenta una regresión menor en detección de <strong>Inyección SQL</strong> comparado con v2.4. Se recomienda aumentar muestras sintéticas en el próximo ciclo."
          </p>

          <div style={{ marginTop: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#d8b4fe', marginBottom: 6 }}>
              <span>PRECISIÓN</span>
              <span style={{ fontWeight: 700, color: '#ffffff' }}>99.1%</span>
            </div>
            <div className="prog-bar-track" style={{ height: 4, backgroundColor: 'rgba(255,255,255,0.1)' }}>
              <div className="prog-bar-fill" style={{ width: '99.1%', height: '100%', backgroundColor: '#ffffff' }} />
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#d8b4fe', marginBottom: 6 }}>
              <span>EXHAUSTIVIDAD (RECALL)</span>
              <span style={{ fontWeight: 700, color: '#ffffff' }}>96.8%</span>
            </div>
            <div className="prog-bar-track" style={{ height: 4, backgroundColor: 'rgba(255,255,255,0.1)' }}>
              <div className="prog-bar-fill" style={{ width: '96.8%', height: '100%', backgroundColor: '#ffffff' }} />
            </div>
          </div>
        </div>

        {/* Right: Data Management Table */}
        <div className="white-widget">
          <div className="white-widget-header">
            <div>
              <h3 className="white-widget-title">Gestión de Conjuntos de Datos</h3>
            </div>
            <button className="integrity-btn-primary" style={{ margin: 0, padding: '8px 14px' }} onClick={() => toast.success("Módulo de importación de dataset activado.", { position: "top-center" })}>
              Añadir Dataset
            </button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Nombre</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Estado</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Muestras</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Último Uso</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: 'Global_Threat_v12', desc: 'Conjunto de Producción Validado', badge: 'ACTIVO', color: 'green', rows: '1.2M filas', time: 'Hace 2h' },
                  { name: 'L7_Anomalies_Archive', desc: 'Registros Históricos 2023', badge: 'ARCHIVADO', color: 'gray', rows: '450K filas', time: 'Hace 14d' },
                  { name: 'Realtime_Ingest_Feed', desc: 'Búfer de streaming en vivo', badge: 'STREAMING', color: 'purple', rows: '--', time: 'Ahora' },
                ].map((dataset, idx) => (
                  <tr key={idx}>
                    <td style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <Database size={16} style={{ color: '#7c3aed' }} />
                      <div>
                        <span style={{ fontWeight: 700, color: '#334155' }}>{dataset.name}</span>
                        <span style={{ display: 'block', fontSize: '0.7rem', color: '#94a3b8', fontWeight: 500 }}>{dataset.desc}</span>
                      </div>
                    </td>
                    <td>
                      <span className="badge-pill" style={{ 
                        background: dataset.color === 'green' ? '#f0fdf4' : dataset.color === 'purple' ? '#f3f0ff' : '#f1f5f9', 
                        color: dataset.color === 'green' ? '#16a34a' : dataset.color === 'purple' ? '#6d28d9' : '#475569',
                        fontSize: '0.65rem',
                        fontWeight: 700 
                      }}>
                        {dataset.badge}
                      </span>
                    </td>
                    <td style={{ color: '#475569', fontWeight: 600 }}>{dataset.rows}</td>
                    <td style={{ color: '#64748b' }}>{dataset.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ── BOTTOM SECTION: Hyperparameter Optimization ── */}
      <div className="white-widget" style={{ padding: 24 }}>
        <div className="white-widget-header" style={{ marginBottom: 20 }}>
          <h3 className="white-widget-title" style={{ fontSize: '1rem' }}>Optimización de Hiperparámetros</h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24, alignItems: 'center' }}>
          {/* LR slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 8, fontWeight: 700, color: '#334155' }}>
              <span>Tasa de aprendizaje</span>
              <span style={{ color: '#7c3aed' }}>{learningRate}</span>
            </div>
            <div className="range-track-custom" style={{ height: 4 }}>
              <input 
                type="range" min="0.0001" max="0.1" step="0.0001" value={learningRate} 
                onChange={(e) => setLearningRate(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: '#7c3aed' }} 
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.62rem', color: '#94a3b8', marginTop: 4 }}>
              <span>0.0001</span>
              <span>0.1</span>
            </div>
          </div>

          {/* Batch Size select */}
          <div>
            <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: 8 }}>Tamaño de lote</label>
            <select 
              className="terminal-input" 
              value={batchSize} 
              onChange={e => setBatchSize(e.target.value)}
              style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '6px', color: '#1e293b', padding: '8px 12px', width: '100%' }}
            >
              <option value="32 Muestras">32 Muestras</option>
              <option value="64 Muestras">64 Muestras</option>
              <option value="128 Muestras">128 Muestras</option>
            </select>
          </div>

          {/* Optimizer tabs */}
          <div>
            <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: 8 }}>Optimizador</label>
            <div style={{ display: 'flex', gap: 8 }}>
              {['AdamW', 'SGD'].map(opt => (
                <button
                  key={opt}
                  className={`white-widget-tab ${optimizer === opt ? 'active' : ''}`}
                  onClick={() => setOptimizer(opt)}
                  style={{ flex: 1, border: '1px solid #cbd5e1', padding: '8px 12px', borderRadius: '6px' }}
                >
                  {opt}
                </button>
              ))}
            </div>
          </div>

          {/* Dropout */}
          <div>
            <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: 8 }}>Dropout</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <input 
                type="number" step="0.05" min="0" max="0.9" value={dropout}
                onChange={e => setDropout(parseFloat(e.target.value) || 0)}
                style={{ width: 80, border: '1px solid #cbd5e1', padding: '8px 10px', borderRadius: '6px' }} 
              />
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Factor de probabilidad</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

function Settings2Icon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="lucide lucide-settings-2"
    >
      <path d="M20 7h-9" />
      <path d="M14 17H5" />
      <circle cx="17" cy="17" r="3" />
      <circle cx="7" cy="7" r="3" />
    </svg>
  );
}
