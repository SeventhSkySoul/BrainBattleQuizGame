import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { storage, STORAGE_KEYS, API } from '../utils';
import axios from 'axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = storage.get(STORAGE_KEYS.TOKEN);
    const savedUser = storage.get(STORAGE_KEYS.USER);
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(savedUser);
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await axios.post(`${API}/auth/login`, { email, password });
    const { token: t, user: u } = res.data;
    setToken(t);
    setUser(u);
    storage.set(STORAGE_KEYS.TOKEN, t);
    storage.set(STORAGE_KEYS.USER, u);
    return u;
  }, []);

  const register = useCallback(async (username, email, password) => {
    const res = await axios.post(`${API}/auth/register`, { username, email, password });
    const { token: t, user: u } = res.data;
    setToken(t);
    setUser(u);
    storage.set(STORAGE_KEYS.TOKEN, t);
    storage.set(STORAGE_KEYS.USER, u);
    return u;
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    storage.remove(STORAGE_KEYS.TOKEN);
    storage.remove(STORAGE_KEYS.USER);
  }, []);

  const getAuthHeader = useCallback(() => {
    return token ? { Authorization: `Bearer ${token}` } : {};
  }, [token]);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, getAuthHeader }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
