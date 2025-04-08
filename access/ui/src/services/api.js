/**
 * @file api.js
 * @description API服务，处理HTTP请求
 * 
 * 需求:
 * 1. 更新现有API服务，支持新的会话和生成功能
 * 2. 保留认证相关功能
 * 3. 增加会话管理和消息发送API
 * 4. 支持代码生成和存储相关API
 * 5. 添加澄清器服务，处理需求澄清和期望生成
 * 
 * 主要服务:
 * - authService: 认证相关API
 * - conversationService: 会话管理API
 * - expectationService: 期望管理API
 * - generationService: 代码生成API
 * - clarifierService: 需求澄清API
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

export const clarifierService = {
  clarifyRequirement: (requirementText) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const userInputLower = requirementText.toLowerCase();
        
        let topLevelExpectation = {
          name: "Software Project",
          description: "A software solution based on the provided requirements.",
          acceptance_criteria: [
            "Must solve the core problem described",
            "Should be user-friendly and intuitive"
          ],
          constraints: [
            "Must be completed within reasonable timeframe",
            "Should follow industry best practices"
          ],
          id: "exp-" + Math.random().toString(36).substring(2, 10),
          level: "top",
          source_text: requirementText
        };
        
        let subExpectations = [];
        
        if (userInputLower.includes('website') || userInputLower.includes('web app') || userInputLower.includes('homepage')) {
          topLevelExpectation = {
            name: "Website Development",
            description: "A responsive website that serves the specific needs and target audience.",
            acceptance_criteria: [
              "Responsive design that works on mobile and desktop",
              "Clear navigation and user interface",
              "Content management capabilities"
            ],
            constraints: [
              "Must follow web accessibility guidelines",
              "Should load quickly on various devices and connections"
            ],
            id: "exp-" + Math.random().toString(36).substring(2, 10),
            level: "top",
            source_text: requirementText
          };
          
          subExpectations = [
            {
              name: "Frontend UI Components",
              description: "User interface components for the website.",
              acceptance_criteria: [
                "Responsive layout that adapts to different screen sizes",
                "Consistent design language across all pages",
                "Interactive elements with appropriate feedback"
              ],
              constraints: [
                "Must be accessible according to WCAG standards",
                "Should be cross-browser compatible"
              ],
              id: "exp-" + Math.random().toString(36).substring(2, 10),
              level: "sub",
              parent_id: topLevelExpectation.id
            },
            {
              name: "Content Management",
              description: "System for managing website content.",
              acceptance_criteria: [
                "Ability to add, edit, and delete content",
                "Support for different content types (text, images, etc.)",
                "Preview functionality before publishing"
              ],
              constraints: [
                "Must be user-friendly for non-technical users",
                "Should support content versioning"
              ],
              id: "exp-" + Math.random().toString(36).substring(2, 10),
              level: "sub",
              parent_id: topLevelExpectation.id
            },
            {
              name: "Performance Optimization",
              description: "Optimizations to ensure fast loading and smooth operation.",
              acceptance_criteria: [
                "Page load time under 3 seconds on average connections",
                "Optimized assets (images, scripts, styles)",
                "Caching strategy for improved performance"
              ],
              constraints: [
                "Must maintain visual quality while optimizing",
                "Should not sacrifice functionality for speed"
              ],
              id: "exp-" + Math.random().toString(36).substring(2, 10),
              level: "sub",
              parent_id: topLevelExpectation.id
            }
          ];
        } else if (userInputLower.includes('app') || userInputLower.includes('mobile')) {
          topLevelExpectation = {
            name: "Mobile Application",
            description: "A mobile app that delivers value to users on iOS and/or Android platforms.",
            acceptance_criteria: [
              "Intuitive user interface",
              "Core functionality works offline",
              "Efficient performance on target devices"
            ],
            constraints: [
              "Must comply with app store guidelines",
              "Should minimize battery usage"
            ],
            id: "exp-" + Math.random().toString(36).substring(2, 10),
            level: "top",
            source_text: requirementText
          };
          
          subExpectations = [
            {
              name: "User Interface Design",
              description: "Design of the app's user interface and experience.",
              acceptance_criteria: [
                "Follows platform design guidelines (Material Design/Human Interface)",
                "Consistent visual language throughout the app",
                "Intuitive navigation and interaction patterns"
              ],
              constraints: [
                "Must be accessible to users with disabilities",
                "Should support different device sizes and orientations"
              ],
              id: "exp-" + Math.random().toString(36).substring(2, 10),
              level: "sub",
              parent_id: topLevelExpectation.id
            },
            {
              name: "Offline Functionality",
              description: "Features that work without an internet connection.",
              acceptance_criteria: [
                "Core features available offline",
                "Data synchronization when connection is restored",
                "Clear indication of online/offline status"
              ],
              constraints: [
                "Must handle conflict resolution during sync",
                "Should minimize storage usage"
              ],
              id: "exp-" + Math.random().toString(36).substring(2, 10),
              level: "sub",
              parent_id: topLevelExpectation.id
            },
            {
              name: "Performance Optimization",
              description: "Optimizations for smooth operation and battery efficiency.",
              acceptance_criteria: [
                "App launches within 3 seconds",
                "Smooth scrolling and transitions (60fps)",
                "Minimal battery impact during normal usage"
              ],
              constraints: [
                "Must work on devices up to 3 years old",
                "Should not exceed reasonable memory usage"
              ],
              id: "exp-" + Math.random().toString(36).substring(2, 10),
              level: "sub",
              parent_id: topLevelExpectation.id
            }
          ];
        } else if (userInputLower.includes('api') || userInputLower.includes('backend')) {
          topLevelExpectation = {
            name: "API/Backend System",
            description: "A robust backend system to support application needs with secure and efficient data processing.",
            acceptance_criteria: [
              "Secure authentication and authorization",
              "Well-documented API endpoints",
              "Efficient data processing"
            ],
            constraints: [
              "Must handle expected load",
              "Should implement proper error handling"
            ],
            id: "exp-" + Math.random().toString(36).substring(2, 10),
            level: "top",
            source_text: requirementText
          };
          
          subExpectations = [
            {
              name: "Authentication System",
              description: "System for user authentication and authorization.",
              acceptance_criteria: [
                "Secure user registration and login",
                "Role-based access control",
                "Token-based authentication with refresh capability"
              ],
              constraints: [
                "Must follow security best practices (OWASP)",
                "Should support multiple authentication methods"
              ],
              id: "exp-" + Math.random().toString(36).substring(2, 10),
              level: "sub",
              parent_id: topLevelExpectation.id
            },
            {
              name: "API Design",
              description: "Design and implementation of API endpoints.",
              acceptance_criteria: [
                "RESTful or GraphQL API following best practices",
                "Consistent response format",
                "Comprehensive error handling"
              ],
              constraints: [
                "Must be versioned for future compatibility",
                "Should be rate-limited to prevent abuse"
              ],
              id: "exp-" + Math.random().toString(36).substring(2, 10),
              level: "sub",
              parent_id: topLevelExpectation.id
            },
            {
              name: "Data Processing",
              description: "Systems for processing and storing data.",
              acceptance_criteria: [
                "Efficient database queries and operations",
                "Data validation and sanitization",
                "Backup and recovery procedures"
              ],
              constraints: [
                "Must ensure data integrity",
                "Should optimize for query performance"
              ],
              id: "exp-" + Math.random().toString(36).substring(2, 10),
              level: "sub",
              parent_id: topLevelExpectation.id
            }
          ];
        }
        
        resolve({
          data: {
            top_level_expectation: topLevelExpectation,
            sub_expectations: subExpectations,
            process_metadata: {
              timestamp: new Date().toISOString(),
              version: "1.0"
            }
          }
        });
      }, 1000);
    });
  },
  
  getClarificationHistory: () => {
    return api.get('/api/clarifier/history');
  }
};

export default api;
