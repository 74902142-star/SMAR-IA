/* eslint-disable react-refresh/only-export-components */
import { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const AuthContext = createContext();
const API_BASE_URL = 'http://127.0.0.1:8000';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(() => !!localStorage.getItem('token'));
  const navigate = useNavigate();

  // Validar token real contra el backend al iniciar
  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        localStorage.removeItem('token');
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
          const body = await response.text();
          console.warn('Token validation failed', response.status, body);
          throw new Error('Token inválido');
        }

        const data = await response.json();
        setUser({ username: data.username });
        localStorage.setItem('token', token);
      } catch (error) {
        console.error('Token validation error', error);
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };

    validateToken();
  }, [token]);

  const login = async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      if (!response.ok) {
        const body = await response.text();
        console.warn('Login failed', response.status, body);
        return false;
      }

      const data = await response.json();
      if (!data.access_token) {
        console.warn('Login response missing access token', data);
        return false;
      }

      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      setUser({ username: data.username || username });
      return true;
    } catch (error) {
      console.error('Login error', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    setLoading(false);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

