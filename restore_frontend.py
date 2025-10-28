#!/usr/bin/env python3
"""
Quick frontend restoration script
Restores all deleted frontend files
"""
import os

FRONTEND_FILES = {
    "frontend/src/services/api.js": """import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {'Content-Type': 'application/json'},
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  getMe: () => api.get('/api/auth/me'),
};

export const chatAPI = {
  createSession: (data) => api.post('/api/chat/sessions', data),
  getSessions: () => api.get('/api/chat/sessions'),
  getSession: (sessionId) => api.get(`/api/chat/sessions/${sessionId}`),
  sendMessage: (sessionId, message) => api.post(`/api/chat/sessions/${sessionId}/messages`, message),
  deleteSession: (sessionId) => api.delete(`/api/chat/sessions/${sessionId}`),
};

export const teacherAPI = {
  getAllStudentsHistory: () => api.get('/api/teacher/students'),
  getStudentSessions: (studentId) => api.get(`/api/teacher/students/${studentId}/sessions`),
  getSessionDetails: (sessionId) => api.get(`/api/teacher/sessions/${sessionId}`),
};

export const documentAPI = {
  upload: (formData) => api.post('/api/documents/upload', formData, {
    headers: {'Content-Type': 'multipart/form-data'},
  }),
  getDocuments: () => api.get('/api/documents'),
};

export default api;
""",
    
    "frontend/src/context/AuthContext.js": """import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await authAPI.getMe();
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const login = async (credentials) => {
    const response = await authAPI.login(credentials);
    localStorage.setItem('token', response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const register = async (userData) => {
    const response = await authAPI.register(userData);
    localStorage.setItem('token', response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>;
};
"""
}

def create_file(path, content):
    full_path = f"/home/xoai/Chatbot/{path}"
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
    print(f"✅ Created: {path}")

if __name__ == "__main__":
    print("🔄 Restoring frontend files...\n")
    for path, content in FRONTEND_FILES.items():
        create_file(path, content)
    print("\n✅ Frontend files restored!")
    print("📝 Note: Still need to restore pages/*.js files manually")

