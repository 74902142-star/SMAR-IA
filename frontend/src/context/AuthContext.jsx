/* eslint-disable react-refresh/only-export-components */
import { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiUrl } from '../api';

const IS_DEV = import.meta.env.DEV;

function devLog(...args) {
  if (IS_DEV) {
    if (args[0]?.startsWith?.('LOGIN') || args[0]?.startsWith?.('TOKEN')) {
      console.warn(...args);
    }
  }
}

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(() => !!localStorage.getItem('token'));
  const navigate = useNavigate();

  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        localStorage.removeItem('token');
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const response = await fetch(apiUrl('/api/auth/me'), {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
          const body = await response.text();
          devLog('TOKEN validation failed', response.status, body);
          throw new Error('Token inválido');
        }

        const data = await response.json();
        setUser({ username: data.username });
        localStorage.setItem('token', token);
      } catch (error) {
        devLog('TOKEN validation error', error);
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
      const response = await fetch(apiUrl('/api/auth/login'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      if (!response.ok) {
        const body = await response.text();
        devLog('LOGIN failed', response.status);
        return false;
      }

      const data = await response.json();
      if (!data.access_token) {
        devLog('LOGIN response missing access token');
        return false;
      }

      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      setUser({ username: data.username || username });
      return true;
    } catch (error) {
      devLog('LOGIN error', error);
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

