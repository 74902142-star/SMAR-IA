import { useState, useEffect, useContext, useCallback } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Plus, Trash2, Edit3, Save, ShieldCheck, ScrollText, Shield, Play, Settings2, Globe, AlertCircle } from 'lucide-react';
import { toast } from 'react-toastify';
import { apiUrl } from '../api';

const ACTIONS = ['BLOCK', 'ALERT'];
const CONDITIONS_HELP = `Ejemplos:
- attack_type == 'Brute Force' and confidence > 0.8
- attack_type == 'DDoS SYN Flood' or attack_type == 'DDoS UDP Flood'
- confidence > 0.95
- ip == '192.168.1.100'`;

const VALID_VARS = ['attack_type', 'confidence', 'ip'];

function validateCondition(condition) {
  if (!condition || condition.trim() === '') return 'La condición está vacía';
  if (condition.includes('__') || condition.includes('import') || condition.includes('exec'))
    return 'Caracteres no permitidos';
  const vars = condition.match(/[a-zA-Z_][a-zA-Z0-9_]*/g) || [];
  for (const v of vars) {
    if (!VALID_VARS.includes(v) && !['and', 'or', 'not', 'in', 'is'].includes(v) && v !== v.toUpperCase() && !v.startsWith('_'))
      return `Variable desconocida: "${v}". Use solo: ${VALID_VARS.join(', ')}`;
  }
  try {
    new Function(`"use strict"; return (${condition.replace(/attack_type|confidence|ip/g, '"test"')});`);
  } catch (e) {
    return `Error de sintaxis: ${e.message}`;
  }
  return null;
}

export default function RuleManager() {
  const { token } = useContext(AuthContext);
  const [rules, setRules] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', condition: '', action: 'BLOCK', duration_minutes: 60, enabled: true });
  const [testResult, setTestResult] = useState(null);

  const fetchRules = useCallback(async () => {
    try {
      const r = await fetch(apiUrl('/api/rules/'), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) setRules(await r.json());
    } catch {}
  }, [token]);

  useEffect(() => { fetchRules(); }, [fetchRules]);

  const handleSave = async () => {
    if (!form.name || !form.condition) { toast.error('Nombre y condición son requeridos'); return; }
    const err = validateCondition(form.condition);
    if (err) { toast.error(err); return; }
    try {
      const url = editing
        ? apiUrl(`/api/rules/${editing}`)
        : apiUrl('/api/rules/');
      const method = editing ? 'PUT' : 'POST';
      const r = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(form),
      });
      if (r.ok) {
        toast.success(editing ? 'Regla actualizada' : 'Regla creada');
        setShowForm(false); setEditing(null);
        setForm({ name: '', condition: '', action: 'BLOCK', duration_minutes: 60, enabled: true });
        fetchRules();
      } else {
        const err = await r.json();
        toast.error(err.detail || 'Error al guardar');
      }
    } catch { toast.error('Error de conexión'); }
  };

  const handleDelete = async (id) => {
    try {
      const r = await fetch(apiUrl(`/api/rules/${id}`), {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) { toast.success('Regla eliminada'); fetchRules(); }
    } catch { toast.error('Error de conexión'); }
  };

  const handleToggle = async (rule) => {
    try {
      const r = await fetch(apiUrl(`/api/rules/${rule.id}`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ enabled: !rule.enabled }),
      });
      if (r.ok) { toast.info(`Regla ${rule.enabled ? 'desactivada' : 'activada'}`); fetchRules(); }
    } catch { toast.error('Error de conexión'); }
  };

  const handleEdit = (rule) => {
    setForm({ name: rule.name, condition: rule.condition, action: rule.action, duration_minutes: rule.duration_minutes || 60, enabled: rule.enabled });
    setEditing(rule.id);
    setShowForm(true);
  };

  const testCondition = () => {
    if (!form.condition) { toast.error('Escribe una condición primero'); return; }
    const err = validateCondition(form.condition);
    if (err) {
      setTestResult(`✗ ${err}`);
    } else {
      setTestResult('✓ Sintaxis válida');
    }
    setTimeout(() => setTestResult(null), 4000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }} className="campus-dashboard">
      
      {/* ── Header ── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 className="white-widget-title" style={{ fontSize: '1.8rem', marginBottom: 4 }}>Reglas de Mitigación</h1>
          <p className="white-widget-subtitle">Gestión de reglas de flujo SDN y respuestas automáticas.</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="white-widget-tab" style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 16px', borderRadius: '6px' }}>
            <Settings2 size={16} />
            Ajustes de Auto-Mitigación
          </button>
          <button 
            className="integrity-btn-primary" 
            style={{ display: 'flex', alignItems: 'center', gap: 6, margin: 0, padding: '10px 16px', borderRadius: '6px' }}
            onClick={() => { setShowForm(!showForm); setEditing(null); setForm({ name: '', condition: '', action: 'BLOCK', duration_minutes: 60, enabled: true }); }}
          >
            <Plus size={16} />
            {showForm ? 'Cerrar Formulario' : 'Nueva Regla'}
          </button>
        </div>
      </div>

      {/* ── ML Recommendations Banner ── */}
      <div style={{
        background: '#fffafb',
        border: '1px solid #fee2e2',
        borderRadius: '12px',
        padding: '20px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ width: 44, height: 44, borderRadius: '50%', backgroundColor: '#fee2e2', color: '#dc2626', display: 'flex', alignItems: 'center', justify: 'center', flexShrink: 0 }}>
            <AlertCircle size={22} style={{ margin: '0 auto' }} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>Recomendaciones de ML</h4>
            <p style={{ fontSize: '0.82rem', color: '#64748b', margin: 0, lineHeight: 1.4 }}>
              Basado en picos de tráfico recientes en el Sector-7, NetGuard recomienda implementar un límite de tasa de 500 req/s en la subred 192.168.1.0/24.
            </p>
          </div>
        </div>
        <button className="integrity-btn-primary" style={{ margin: 0, background: '#2b0075' }} onClick={() => toast.info("Revisando cambios de políticas...", { position: "top-center" })}>
          Revisar Cambios
        </button>
      </div>

      {/* ── New Rule Form Panel ── */}
      {showForm && (
        <div className="white-widget" style={{ padding: 24 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 20, color: '#1e1b4b' }}>
            {editing ? 'Editar Regla de Mitigación' : 'Crear Nueva Regla de Mitigación'}
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: '#475569', display: 'block', marginBottom: 6, fontWeight: 600 }}>NOMBRE DE REGLA</label>
              <input className="terminal-input" style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '6px', color: '#1e293b' }} value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Ej: Bloquear DDoS en WebServer" />
            </div>
            <div>
              <label style={{ fontSize: '0.8rem', color: '#475569', display: 'block', marginBottom: 6, fontWeight: 600 }}>ACCIÓN</label>
              <select className="terminal-input" style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '6px', color: '#1e293b' }} value={form.action} onChange={e => setForm({ ...form, action: e.target.value })}>
                {ACTIONS.map(a => <option key={a} value={a}>{a === 'BLOCK' ? 'DESCARTAR (BLOQUEAR)' : 'ALERTAR'}</option>)}
              </select>
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={{ fontSize: '0.8rem', color: '#475569', display: 'block', marginBottom: 6, fontWeight: 600 }}>CONDICIÓN (Sintaxis Lógica)</label>
              <textarea className="terminal-input" style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '6px', color: '#1e293b', fontFamily: 'monospace' }} value={form.condition} onChange={e => setForm({ ...form, condition: e.target.value })} placeholder="attack_type == 'DDoS SYN Flood' and confidence > 0.8" rows={2} />
              <details style={{ marginTop: 6, fontSize: '0.75rem', color: '#64748b' }}>
                <summary style={{ cursor: 'pointer', fontWeight: 600 }}>Ver ejemplos de sintaxis</summary>
                <pre style={{ marginTop: 4, background: '#f8fafc', padding: 8, borderRadius: '6px', fontSize: '0.75rem', border: '1px solid #e2e8f0', whiteSpace: 'pre-wrap' }}>{CONDITIONS_HELP}</pre>
              </details>
            </div>
            <div>
              <label style={{ fontSize: '0.8rem', color: '#475569', display: 'block', marginBottom: 6, fontWeight: 600 }}>DURACIÓN (Minutos, 0 = Permanente)</label>
              <input className="terminal-input" style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '6px', color: '#1e293b' }} type="number" value={form.duration_minutes} onChange={e => setForm({ ...form, duration_minutes: parseInt(e.target.value) || 0 })} />
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12, paddingBottom: 4 }}>
              <button className="integrity-btn-primary" style={{ margin: 0, padding: '10px 18px' }} onClick={handleSave}>
                <Save size={15} style={{ marginRight: 6 }} /> Guardar Regla
              </button>
              <button className="white-widget-tab" style={{ border: '1px solid #cbd5e1', padding: '10px 14px', borderRadius: '6px' }} onClick={testCondition}>
                Probar Sintaxis
              </button>
              {testResult && <span style={{ fontSize: '0.8rem', color: testResult.startsWith('✓') ? '#16a34a' : '#ef4444', fontWeight: 600 }}>{testResult}</span>}
            </div>
          </div>
        </div>
      )}

      {/* ── MIDDLE ROW: Rules Table & Right Sidebar widgets ── */}
      <div className="dashboard-layout-row" style={{ gridTemplateColumns: '1.8fr 1fr' }}>
        {/* Left: Active Rules Table */}
        <div className="white-widget">
          <div className="white-widget-header">
            <div>
              <h3 className="white-widget-title">Reglas de Mitigación Activas</h3>
            </div>
            <button className="white-widget-tab" style={{ border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '0.8rem' }}>Filtros</button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Nombre y Tipo</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Condición (Objetivo)</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Acción</th>
                  <th style={{ background: '#f8fafc', color: '#64748b' }}>Impacto (24h)</th>
                  <th style={{ background: '#f8fafc', color: '#64748b', textAlign: 'center' }}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {/* Real-time rules from FastAPI SQLite DB combined with visual mockup entries */}
                {rules.map((rule) => (
                  <tr key={rule.id}>
                    <td style={{ fontWeight: 600, color: '#334155' }}>
                      {rule.name}
                      <span style={{ display: 'block', fontSize: '0.7rem', color: '#94a3b8', fontWeight: 500 }}>ID: #{rule.id} · Duración: {rule.duration_minutes || 'Permanente'}</span>
                    </td>
                    <td style={{ fontFamily: 'monospace', color: '#7c3aed', fontSize: '0.78rem' }}>if ({rule.condition})</td>
                    <td>
                      <span className="badge-pill" style={{ background: rule.action === 'BLOCK' ? '#fef2f2' : '#fef3c7', color: rule.action === 'BLOCK' ? '#dc2626' : '#d97706', fontSize: '0.65rem', fontWeight: 700 }}>
                        {rule.action === 'BLOCK' ? 'DESCARTAR' : 'ALERTAR'}
                      </span>
                    </td>
                    <td style={{ color: '#64748b', fontWeight: 600 }}>0 flujos</td>
                    <td style={{ textAlign: 'center' }}>
                      <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
                        <button className="white-widget-tab" style={{ padding: '4px 6px', border: '1px solid #cbd5e1', borderRadius: '4px' }} onClick={() => handleToggle(rule)}>
                          {rule.enabled ? 'Desactivar' : 'Activar'}
                        </button>
                        <button className="white-widget-tab" style={{ padding: '4px 6px', border: '1px solid #cbd5e1', borderRadius: '4px' }} onClick={() => handleEdit(rule)}>
                          <Edit3 size={12} />
                        </button>
                        <button className="white-widget-tab" style={{ padding: '4px 6px', border: '1px solid #fee2e2', color: '#ef4444', borderRadius: '4px' }} onClick={() => handleDelete(rule.id)}>
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {/* Mock rules for default visual layout matching the image */}
                {[
                  { name: 'Supresión DDoS Alpha', type: 'Límite de Tasa', target: '0.0.0.0 → 80.45.1.2', action: 'LIMITAR TASA', color: 'purple', impact: '1.2M', active: true },
                  { name: 'Bloqueo de Bot Malicioso', type: 'Descartar Paquetes', target: '114.23.0.0/16', action: 'DESCARTAR', color: 'red', impact: '84k', active: true },
                  { name: 'Redirección Honeypot', type: 'Redireccionamiento', target: 'Cualquiera → Puerto 445', action: 'REDIRIGIR', color: 'purple', impact: '12k', active: false },
                  { name: 'Bloqueo Escaneo Interno', type: 'Descartar Paquetes', target: 'VLAN 40 → Core DB', action: 'DESCARTAR', color: 'red', impact: '0', active: true },
                ].map((item, idx) => (
                  <tr key={`mock-${idx}`}>
                    <td style={{ fontWeight: 600, color: '#334155' }}>
                      {item.name}
                      <span style={{ display: 'block', fontSize: '0.7rem', color: '#94a3b8', fontWeight: 500 }}>{item.type}</span>
                    </td>
                    <td style={{ fontFamily: 'monospace', color: '#475569', fontSize: '0.78rem' }}>{item.target}</td>
                    <td>
                      <span className="badge-pill" style={{ 
                        background: item.color === 'red' ? '#fef2f2' : '#f3f0ff', 
                        color: item.color === 'red' ? '#dc2626' : '#6d28d9',
                        fontSize: '0.65rem', 
                        fontWeight: 700 
                      }}>
                        {item.action}
                      </span>
                    </td>
                    <td style={{ color: '#64748b', fontWeight: 600 }}>{item.impact}</td>
                    <td style={{ textAlign: 'center' }}>
                      <input 
                        type="checkbox" 
                        checked={item.active} 
                        onChange={() => toast.info(`Estado de regla ${item.name} modificado.`)}
                        style={{ cursor: 'pointer', accentColor: '#2b0075', width: 16, height: 16 }}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: 24 }}>
            <a href="#rules" onClick={e => { e.preventDefault(); toast.info("Mostrando todas las reglas del sistema."); }} style={{ fontSize: '0.85rem', color: '#2b0075', fontWeight: 700, textDecoration: 'none' }}>
              Ver Todas las Reglas ▾
            </a>
          </div>
        </div>

        {/* Right Widgets: Integrity & Mitigation efficiency */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          
          {/* Widget 1: Integridad Asegurada */}
          <div className="white-widget" style={{ alignItems: 'center', textAlign: 'center' }}>
            <div className="integrity-shield-container" style={{ width: 64, height: 64, marginBottom: 16 }}>
              <ShieldCheck size={28} />
            </div>
            <h3 className="integrity-title" style={{ fontSize: '1.1rem', marginBottom: 8 }}>Integridad Asegurada</h3>
            <p className="integrity-subtitle" style={{ fontSize: '0.8rem', marginBottom: 20, maxWidth: '240px' }}>
              98.2% de las amenazas mitigadas automáticamente en los últimos 60 minutos.
            </p>
            <div style={{ background: '#f3f0ff', color: '#2b0075', fontSize: '0.75rem', fontWeight: 700, padding: '8px 16px', borderRadius: '20px' }}>
              Latencia SDN: 4.2ms
            </div>
          </div>

          {/* Widget 2: Eficiencia de Mitigación */}
          <div className="white-widget">
            <div className="white-widget-header" style={{ marginBottom: 16 }}>
              <h3 className="white-widget-title" style={{ fontSize: '0.95rem' }}>EFICIENCIA DE MITIGACIÓN</h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[
                { label: 'Límite de Tasa', val: 65, color: '#7c3aed' },
                { label: 'Descarte de Paquetes', val: 22, color: '#ef4444' },
                { label: 'Honeypots', val: 13, color: '#7c3aed' },
              ].map((eff, i) => (
                <div key={i}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 6 }}>
                    <span style={{ fontWeight: 600, color: '#475569' }}>{eff.label}</span>
                    <span style={{ fontWeight: 700, color: eff.color }}>{eff.val}%</span>
                  </div>
                  <div className="prog-bar-track" style={{ height: 6, backgroundColor: '#f1f5f9' }}>
                    <div className="prog-bar-fill" style={{ width: `${eff.val}%`, height: '100%', backgroundColor: eff.color, borderRadius: '3px' }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* ── BOTTOM SECTION: Global Map Topology ── */}
      <div className="white-widget">
        <div className="white-widget-header" style={{ marginBottom: 8 }}>
          <div>
            <h3 className="white-widget-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Globe size={18} /> Topología de Flujos en Tiempo Real
            </h3>
            <p className="white-widget-subtitle">Nodos de ejecución de reglas SDN activos en la infraestructura global.</p>
          </div>
          <div style={{ display: 'flex', gap: 16, fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span className="topology-legend-dot purple" /> Nodo Activo
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span className="topology-legend-dot red" /> Evento de Mitigación
            </div>
          </div>
        </div>

        <div className="topology-map-container" style={{ minHeight: 250 }}>
          <div className="topology-grid-overlay" />
          <div className="topology-floorplan" style={{ 
            minHeight: 250, 
            backgroundImage: "radial-gradient(circle, rgba(124, 58, 237, 0.08) 0%, transparent 80%)",
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {/* World map stylized vectors represented as CSS coordinates */}
            {/* North America */}
            <div style={{ position: 'absolute', left: '20%', top: '35%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="topology-dot purple" />
            </div>
            
            {/* Europe / London */}
            <div style={{ position: 'absolute', left: '48%', top: '28%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="topology-dot purple" />
            </div>

            {/* West Africa */}
            <div style={{ position: 'absolute', left: '50%', top: '55%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="topology-dot purple" />
            </div>

            {/* Singapore / Southeast Asia */}
            <div style={{ position: 'absolute', right: '25%', top: '65%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="topology-dot red" style={{ animation: 'pulse 1.5s infinite' }} />
            </div>

            {/* Brazil */}
            <div style={{ position: 'absolute', left: '33%', top: '70%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="topology-dot purple" />
            </div>

            <div style={{ color: 'rgba(255, 255, 255, 0.15)', fontSize: '1.2rem', fontWeight: 800, fontFamily: 'monospace', letterSpacing: '4px', textAlign: 'center' }}>
              INFRAESTRUCTURA SDN GLOBAL
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
