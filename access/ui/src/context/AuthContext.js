import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/api';

// 创建认证上下文
const AuthContext = createContext();

// 认证Provider组件
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 加载时检查登录状态
  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (token) {
          try {
            // 尝试从API获取用户信息
            const response = await authService.getCurrentUser();
            setCurrentUser(response.data);
          } catch (apiErr) {
            // 如果API调用失败，尝试从localStorage读取模拟用户
            const mockUserStr = localStorage.getItem('mockUser');
            if (mockUserStr) {
              try {
                const mockUser = JSON.parse(mockUserStr);
                setCurrentUser(mockUser);
              } catch (parseErr) {
                // 解析失败，清除localStorage
                localStorage.removeItem('authToken');
                localStorage.removeItem('mockUser');
              }
            } else {
              // 如果没有模拟用户数据，清除authToken
              localStorage.removeItem('authToken');
            }
          }
        }
      } catch (err) {
        console.error('Failed to load user:', err);
        localStorage.removeItem('authToken');
        localStorage.removeItem('mockUser');
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  // 登录
  const login = async (credentials) => {
    setError(null);
    try {
      const response = await authService.login(credentials);
      const { token, user } = response.data;
      
      // 保存认证令牌和用户信息
      localStorage.setItem('authToken', token);
      setCurrentUser(user);
      return user;
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
      throw err;
    }
  };

  // 注册
  const register = async (userData) => {
    setError(null);
    try {
      const response = await authService.register(userData);
      const { token, user } = response.data;
      
      // 保存认证令牌和用户信息
      localStorage.setItem('authToken', token);
      setCurrentUser(user);
      return user;
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
      throw err;
    }
  };

  // 退出登录
  const logout = async () => {
    try {
      await authService.logout();
    } finally {
      // 无论API调用是否成功，都清除本地数据
      localStorage.removeItem('authToken');
      localStorage.removeItem('mockUser');
      setCurrentUser(null);
    }
  };

  // 提供的上下文值
  const value = {
    currentUser,
    setCurrentUser,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!currentUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// 自定义hook，方便获取认证上下文
export const useAuth = () => {
  return useContext(AuthContext);
};

export default AuthContext; 