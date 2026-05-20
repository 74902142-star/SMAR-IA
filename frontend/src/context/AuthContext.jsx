import { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Validar token real contra el backend al iniciar
  useEffect(() => {
    if (token) {
      fetch('http://localhost:8000/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => {
          if (res.ok) return res.json();
          throw new Error('Token inválido');
        })
        .then(data => {
          setUser({ username: data.username });
          localStorage.setItem('token', token);
        })
        .catch(() => {
          // Token expirado o inválido → limpiar
          setToken(null);
          setUser(null);
          localStorage.removeItem('token');
        })
        .finally(() => setLoading(false));
    } else {
      setUser(null);
      localStorage.removeItem('token');
      setLoading(false);
    }
  }, [token]);

  const login = async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        navigate('/');
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error', error);
      return false;
    }
  };

  const logout = () => {
    setToken(null);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
