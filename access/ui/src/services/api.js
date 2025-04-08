/**
 * @file api.js
 * @description API服务，处理HTTP请求
 * 
 * 需求:
 * 1. 更新现有API服务，支持新的会话和生成功能
 * 2. 保留认证相关功能
 * 3. 增加会话管理和消息发送API
 * 4. 支持代码生成和存储相关API
 * 
 * 主要服务:
 * - authService: 认证相关API
 * - conversationService: 会话管理API
 * - expectationService: 期望管理API
 * - generationService: 代码生成API
 */

import axios from 'axios';
// 导入其他必要依赖

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证信息
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('authToken');
      // 如果有路由，可以重定向到登录页
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 处理用户认证相关的API
export const authService = {
  // 用户登录
  login: (credentials) => {
    return api.post('/api/auth/login', credentials);
  },
  
  // 用户注册
  register: (userData) => {
    return api.post('/api/auth/register', userData);
  },
  
  // 获取当前用户信息
  getCurrentUser: () => {
    return api.get('/api/auth/me');
  },
  
  // 退出登录
  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('mockUser');
    return Promise.resolve();
  },
};

// 处理会话相关的API
export const conversationService = {
  // 创建新会话
  createConversation: () => {
    return api.post('/api/conversations');
  },
  
  // 获取会话
  getConversation: (id) => {
    return api.get(`/api/conversations/${id}`);
  },
  
  // 发送消息
  sendMessage: (conversationId, content) => {
    return api.post(`/api/conversations/${conversationId}/messages`, { content });
  },
  
  // 确认期望
  confirmExpectation: (conversationId, expectationId) => {
    return api.post(`/api/conversations/${conversationId}/confirm`, { expectationId });
  },
  
  // 生成代码
  generateCode: (conversationId, expectationId) => {
    return api.post(`/api/conversations/${conversationId}/generate`, { expectationId });
  },
  
  // 获取会话列表
  getConversations: () => {
    return api.get('/api/conversations');
  },
};

// 处理期望相关的API
export const expectationService = {
  // 获取所有期望
  getExpectations: () => {
    return api.get('/api/expectations');
  },
  
  // 获取单个期望详情
  getExpectation: (id) => {
    return api.get(`/api/expectations/${id}`);
  },
  
  // 创建新期望
  createExpectation: (data) => {
    return api.post('/api/expectations', data);
  },
  
  // 更新期望
  updateExpectation: (id, data) => {
    return api.put(`/api/expectations/${id}`, data);
  },
  
  // 删除期望
  deleteExpectation: (id) => {
    return api.delete(`/api/expectations/${id}`);
  },
};

// 处理代码生成相关的API
export const generationService = {
  // 获取生成结果
  getGeneration: (id) => {
    return api.get(`/api/generations/${id}`);
  },
  
  // 获取生成历史
  getGenerations: () => {
    return api.get('/api/generations');
  },
  
  // 下载生成的代码
  downloadGeneration: (id) => {
    return api.get(`/api/generations/${id}/download`, {
      responseType: 'blob'
    });
  },
};

export default api;
