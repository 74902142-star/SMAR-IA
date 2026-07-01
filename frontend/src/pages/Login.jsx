import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Shield, User, Lock, Eye, EyeOff, Building, Key } from 'lucide-react';
import { toast } from 'react-toastify';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

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
    <div className="login-split-container">
      {/* Left Purple Panel */}
      <div className="login-left-panel">
        <div className="login-left-content">
          <div className="login-left-icon-container">
            <Shield size={36} strokeWidth={2} />
          </div>

          <h1 className="login-left-title">UNIVERSIDAD CONTINENTAL</h1>

          <p className="login-left-desc">
            Protección de Red Inteligente. Gestión de SDN y ML para detección de amenazas en tiempo real.
          </p>

          <div className="login-left-footer">
            <div className="login-avatars">
              <span className="login-avatar" />
              <span className="login-avatar" />
              <span className="login-avatar" />
            </div>
            <span className="login-left-footer-text">
              Utilizado por más de 2,000 empresas
            </span>
          </div>
        </div>
      </div>

      {/* Right Form Panel */}
      <div className="login-right-panel">
        <div className="login-right-top" />

        <div className="login-right-middle">
          <div className="login-form-box">
            <h2 className="login-right-title">Acceso Seguro</h2>
            <p className="login-right-subtitle">
              Ingrese sus credenciales para acceder al panel de control.
            </p>

            <form onSubmit={handleSubmit}>
              {/* Username Field */}
              <div className="login-field-row">
                <div className="login-label-row">
                  <label htmlFor="login-username" className="login-label-text">
                    ID Corporativo
                  </label>
                </div>
                <div className="login-input-wrapper">
                  <span className="login-input-icon-left">
                    <User size={18} />
                  </span>
                  <input
                    id="login-username"
                    type="text"
                    placeholder="ej. j.perez@deepshield.net"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    autoComplete="username"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="login-field-row">
                <div className="login-label-row">
                  <label htmlFor="login-password" className="login-label-text">
                    Contraseña
                  </label>
                  <a href="#forgot" className="login-forgot-link" onClick={(e) => e.preventDefault()}>
                    ¿Olvidó su contraseña?
                  </a>
                </div>
                <div className="login-input-wrapper">
                  <span className="login-input-icon-left">
                    <Lock size={18} />
                  </span>
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    className="login-input-icon-right"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              {/* Remember Me Checkbox */}
              <div className="login-checkbox-row">
                <input
                  id="remember-station"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <label htmlFor="remember-station" className="login-checkbox-label">
                  Recordar estación por 30 días
                </label>
              </div>

              {/* Submit Button */}
              <button
                id="login-submit"
                type="submit"
                className="login-btn-primary"
                disabled={loading}
              >
                <Shield size={18} />
                {loading ? 'Entrando...' : 'Entrar'}
              </button>

              {/* Divider */}
              <div className="login-divider-row">O autorice mediante</div>

              {/* Alternative Auth Methods */}
              <div className="login-oauth-row">
                <button type="button" className="login-btn-oauth">
                  <Building size={16} />
                  SSO
                </button>
                <button type="button" className="login-btn-oauth">
                  <Key size={16} />
                  FIDO2
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Footer */}
        <div className="login-right-footer">
          <div className="login-env-status">
            <Shield size={14} className="icon" style={{ marginRight: 6 }} />
            <span>Entorno: Cluster de Producción SDN (US-East-1)</span>
          </div>
          <div className="login-footer-links">
            <a href="#privacy" className="login-footer-link" onClick={(e) => e.preventDefault()}>
              Política de Privacidad
            </a>
            <span>|</span>
            <a href="#terms" className="login-footer-link" onClick={(e) => e.preventDefault()}>
              Acuerdo de Uso
            </a>
            <span>|</span>
            <a href="#support" className="login-footer-link" onClick={(e) => e.preventDefault()}>
              Centro de Soporte
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
