import { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Shield, User, Lock, ArrowRight, Wifi, AlertTriangle } from 'lucide-react';
import { toast } from 'react-toastify';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, token } = useContext(AuthContext);
  const navigate = useNavigate();
  const [time, setTime] = useState('');

  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString('es-PE', { hour12: false }));
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const success = await login(username, password);
      if (success) {
        toast.success('Acceso concedido', { position: 'top-center', autoClose: 2000 });
        navigate('/');
      } else {
        toast.error('Credenciales inválidas', { position: 'top-center' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-grid-overlay" />

      {/* Floating status bottom-left */}
      <div style={{ position:'fixed', bottom:24, left:28, display:'flex', alignItems:'center', gap:8, fontSize:'0.68rem', fontFamily:"'Space Mono',monospace", color:'var(--text-muted)' }}>
        <span className="status-dot green pulse" />
        SISTEMA ACTIVO · {time}
      </div>

      {/* Floating label bottom-right */}
      <div style={{ position:'fixed', bottom:24, right:28, fontSize:'0.68rem', fontFamily:"'Space Mono',monospace", color:'var(--text-muted)', textAlign:'right' }}>
        NODO: CORE_CENTRAL_01<br />
        <span style={{color:'var(--text-muted)'}}>v1.0.0 · ENCRIPTADO</span>
      </div>

      <div className="login-center">
        {/* Brand */}
        <div className="login-brand">
          <div className="login-brand-logo">
            <Shield size={30} />
          </div>
          <div className="login-brand-title">SMAR<span>-IA</span></div>
          <div className="login-brand-sub">INTRUSION DETECTION SYSTEM</div>
        </div>

        {/* Card */}
        <div className="login-card">
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="login-field-label">ID de Operador</label>
              <div className="login-input-group">
                <User size={16} className="icon" />
                <input
                  id="login-username"
                  type="text"
                  placeholder="admin"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="mb-5">
              <label className="login-field-label">Contraseña</label>
              <div className="login-input-group">
                <Lock size={16} className="icon" />
                <input
                  id="login-password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
              </div>
            </div>

            <button
              id="login-submit"
              type="submit"
              className="login-submit-btn"
              disabled={loading}
            >
              {loading ? 'AUTENTICANDO...' : (
                <>INICIAR SESIÓN <ArrowRight size={15} style={{marginLeft:6}} /></>
              )}
            </button>

            <div className="login-status-row">
              <span className="status-dot green" />
              <span>CONEXIÓN SEGURA · TLS 1.3</span>
              <Wifi size={12} style={{marginLeft:'auto'}} />
            </div>
          </form>
        </div>

        <div className="login-warning">
          <AlertTriangle size={13} style={{color:'var(--amber)', flexShrink:0, marginTop:1}} />
          <span>El acceso no autorizado está prohibido y será registrado. Solo personal autorizado.</span>
        </div>
      </div>
    </div>
  );
}
