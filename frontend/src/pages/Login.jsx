import { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Container, Form, Button } from 'react-bootstrap';
import { Shield, User, Fingerprint, Zap, AlertTriangle, Radio, QrCode, Smile } from 'lucide-react';
import { toast } from 'react-toastify';
import { useEffect } from 'react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);

  const [time, setTime] = useState('23:59:04');

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setTime(now.toLocaleTimeString('en-GB', { hour12: false }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(username, password);
    if (success) {
      toast.success("ACCESO CONCEDIDO: ENLACE ESTABLECIDO", {
        theme: "dark",
        position: "top-center",
        autoClose: 2000,
      });
    } else {
      toast.error("ACCESO DENEGADO: CREDENCIALES INVÁLIDAS", { 
        theme: "dark",
        position: "top-center",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    }
  };

  return (
    <div className="login-container">
      {/* Header Logo Section */}
      <div className="login-header-logo">
        <h1 className="main-logo">SMAR-<span className="pink-text">IA</span></h1>
        <div className="secure-access-divider">
          <div className="line"></div>
          <span className="secure-text">ACCESO SEGURO</span>
          <div className="line"></div>
        </div>
      </div>

      <div className="login-wrapper">
        <div className="cyber-card login-card">
          {/* Corner accents */}
          <div className="corner-accent top-left"></div>
          <div className="corner-accent top-right"></div>
          <div className="corner-accent bottom-left"></div>
          <div className="corner-accent bottom-right"></div>

          <Form onSubmit={handleSubmit} className="cyber-form">
            <Form.Group className="mb-4">
              <Form.Label className="cyber-label">ID DE OPERADOR</Form.Label>
              <div className="cyber-input-wrapper">
                <User size={18} className="input-icon" />
                <Form.Control 
                  type="text" 
                  className="cyber-input" 
                  placeholder="USUARIO_NEON_88" 
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required 
                />
              </div>
            </Form.Group>

            <Form.Group className="mb-4">
              <Form.Label className="cyber-label">CONTRASEÑA</Form.Label>
              <div className="cyber-input-wrapper">
                <Fingerprint size={18} className="input-icon" />
                <Form.Control 
                  type="password" 
                  className="cyber-input" 
                  placeholder="••••••••••••" 
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required 
                />
              </div>
            </Form.Group>

            <div className="form-options mb-4">
              <div className="cyber-toggle">
                <div className="toggle-switch"></div>
                <span className="toggle-label">SESIÓN ENCRIPTADA</span>
              </div>
              <a href="#" className="emergency-link">¿PROTOCOLO DE EMERGENCIA?</a>
            </div>

            <Button type="submit" className="cyber-btn-primary">
              INICIALIZAR ENLACE <Zap size={18} className="ms-2" />
            </Button>

            <div className="card-footer-status mt-4">
              <div className="status-indicator">
                <span className="status-label">ESTADO DE TERMINAL</span>
                <div className="status-value">
                  <div className="status-dot-auth"></div>
                  LISTO_PARA_CONECTAR
                </div>
              </div>
              <div className="footer-icons">
                <QrCode size={18} />
                <Smile size={18} className="ms-3" />
              </div>
            </div>
          </Form>
        </div>

        {/* Warning and Node info */}
        <div className="login-bottom-info">
          <div className="warning-text">
            <AlertTriangle size={14} className="me-2" />
            EL ACCESO NO AUTORIZADO ACTIVARÁ PROTOCOLOS DE MITIGACIÓN FÍSICA.
          </div>
          <div className="node-info mt-2">
            <Radio size={14} className="me-2" />
            NODO DEL SISTEMA: CORE_CENTRAL_TOKYO_B4
          </div>
        </div>
      </div>

      {/* Bottom status bars */}
      <div className="bottom-status-bar left">
        <div className="progress-track">
          <div className="progress-fill"></div>
        </div>
        <span className="status-text">FLUJO_DE_DATOS: ACTIVO</span>
      </div>

      <div className="bottom-status-bar right">
        <span className="status-label">HORA_LOCAL</span>
        <span className="time-value">{time}</span>
      </div>
    </div>
  );
}
