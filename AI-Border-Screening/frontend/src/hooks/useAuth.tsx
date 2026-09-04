import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { Officer } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  officer: Officer | null;
  loading: boolean;
  login: (officerId: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [officer, setOfficer] = useState<Officer | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (api.isAuthenticated()) {
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL || '/api/v1'}/auth/me`, {
            headers: { Authorization: `Bearer ${api.getToken()}` },
          });
          if (response.ok) {
            const data = await response.json();
            setOfficer(data);
          } else {
            api.clearToken();
          }
        } catch {
          api.clearToken();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (officerId: string, password: string) => {
    const response = await api.login({ officer_id: officerId, password });
    const meResponse = await fetch(`${import.meta.env.VITE_API_URL || '/api/v1'}/auth/me`, {
      headers: { Authorization: `Bearer ${response.access_token}` },
    });
    if (meResponse.ok) {
      const data = await meResponse.json();
      setOfficer(data);
    }
  };

  const logout = async () => {
    await api.logout();
    setOfficer(null);
  };

  return (
    <AuthContext.Provider value={{ officer, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}