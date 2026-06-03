import { useState, useEffect, useContext, useCallback } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Plus, Trash2, Edit3, Save, ToggleLeft, ToggleRight, Shield } from 'lucide-react';
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
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1>Reglas Dinámicas</h1>
          <p>Motor de reglas con acción automática (BLOCK / ALERT) basado en condiciones</p>
        </div>
        <button className="btn-ghost-blue" style={{ padding: '10px 20px', display: 'flex', alignItems: 'center', gap: 8 }} onClick={() => { setShowForm(!showForm); setEditing(null); setForm({ name: '', condition: '', action: 'BLOCK', duration_minutes: 60, enabled: true }); }}>
          <Plus size={16} /> {showForm ? 'Cancelar' : 'Nueva Regla'}
        </button>
      </div>

      {showForm && (
        <div className="rule-form-panel">
          <h3 style={{ fontSize: '0.85rem', marginBottom: 16, color: 'var(--text-white)', letterSpacing: '1px' }}>{editing ? 'EDITAR REGLA' : 'NUEVA REGLA'}</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>NOMBRE</label>
              <input className="terminal-input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Ej: Bloquear Brute Force" />
            </div>
            <div>
              <label style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>ACCIÓN</label>
              <select className="terminal-input" value={form.action} onChange={e => setForm({ ...form, action: e.target.value })}>
                {ACTIONS.map(a => <option key={a} value={a}>{a === 'BLOCK' ? 'BLOQUEAR' : 'ALERTAR'}</option>)}
              </select>
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>CONDICIÓN</label>
              <textarea className="terminal-input" value={form.condition} onChange={e => setForm({ ...form, condition: e.target.value })} placeholder="attack_type == 'Brute Force' and confidence > 0.8" rows={2} style={{ fontFamily: "'Space Mono',monospace", fontSize: '0.78rem' }} />
              <details style={{ marginTop: 4, fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <summary style={{ cursor: 'pointer' }}>Variables disponibles</summary>
                <pre style={{ marginTop: 4, background: 'var(--input-bg)', padding: 8, borderRadius: 'var(--radius-sm)', fontSize: '0.7rem', whiteSpace: 'pre-wrap' }}>{CONDITIONS_HELP}</pre>
              </details>
            </div>
            <div>
              <label style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>DURACIÓN (minutos, 0 = permanente)</label>
              <input className="terminal-input" type="number" value={form.duration_minutes} onChange={e => setForm({ ...form, duration_minutes: parseInt(e.target.value) || 0 })} />
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, paddingBottom: 4 }}>
              <button className="btn-ghost-blue" style={{ padding: '8px 20px', display: 'flex', alignItems: 'center', gap: 6 }} onClick={handleSave}>
                <Save size={15} /> {editing ? 'Actualizar' : 'Crear Regla'}
              </button>
              <button className="btn-outline" style={{ padding: '8px 14px', fontSize: '0.72rem' }} onClick={testCondition}>
                Probar Sintaxis
              </button>
              {testResult && <span style={{ fontSize: '0.72rem', color: testResult.startsWith('✓') ? 'var(--emerald)' : 'var(--rose)' }}>{testResult}</span>}
            </div>
          </div>
        </div>
      )}

      {rules.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          <Shield size={48} style={{ opacity: 0.2, marginBottom: 16 }} />
          <p>No hay reglas configuradas</p>
          <p style={{ fontSize: '0.75rem' }}>Crea una regla para automatizar el bloqueo de amenazas</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {rules.map(rule => (
            <div key={rule.id} className={`rule-card ${rule.enabled ? '' : 'disabled'}`}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <strong style={{ fontSize: '0.85rem', color: 'var(--text-white)' }}>{rule.name}</strong>
                    <span className={`badge-pill ${rule.action === 'BLOCK' ? 'rose' : 'amber'}`} style={{ fontSize: '0.6rem' }}>{rule.action}</span>
                    {!rule.enabled && <span className="badge-pill" style={{ background: 'rgba(100,100,100,0.2)', color: 'var(--text-muted)', fontSize: '0.6rem' }}>DESACTIVADA</span>}
                  </div>
                  <div style={{ fontFamily: "'Space Mono',monospace", fontSize: '0.75rem', color: 'var(--cyan)', marginBottom: 4 }}>if ({rule.condition})</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Duración: {rule.duration_minutes || 'Permanente'} · ID: #{rule.id}</div>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <button className="btn-ghost-blue" style={{ padding: '6px 10px' }} onClick={() => handleToggle(rule)} title={rule.enabled ? 'Desactivar' : 'Activar'}>
                    {rule.enabled ? <ToggleRight size={16} /> : <ToggleLeft size={16} />}
                  </button>
                  <button className="btn-ghost-blue" style={{ padding: '6px 10px' }} onClick={() => handleEdit(rule)} title="Editar">
                    <Edit3 size={14} />
                  </button>
                  <button className="btn-ghost-blue" style={{ padding: '6px 10px', color: 'var(--rose)' }} onClick={() => handleDelete(rule.id)} title="Eliminar">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
