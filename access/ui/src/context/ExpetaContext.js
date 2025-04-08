/**
 * @file ExpetaContext.js
 * @description Expeta功能上下文，管理全局状态和操作
 * 
 * 需求:
 * 1. 简化现有ExpetaContext，专注于全局状态
 * 2. 提供对期望和生成结果的访问
 * 3. 管理系统级操作和状态
 * 4. 与ConversationContext协作
 * 
 * 提供的上下文值:
 * - expectations: 已确认的期望列表
 * - generations: 代码生成结果列表
 * - generateCode: 从期望生成代码的函数
 * - loadExpectations: 加载期望的函数
 * - loadGenerations: 加载生成结果的函数
 */

import React, { createContext, useState, useEffect, useContext } from 'react';
import { expectationService, generationService } from '../services/api';
// 导入其他必要依赖

// Devin: 请在此实现ExpetaContext

// 创建上下文
const ExpetaContext = createContext();

// 上下文Provider组件
export const ExpetaProvider = ({ children }) => {
  // 基础状态
  const [expectations, setExpectations] = useState([]);
  const [generations, setGenerations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 加载期望列表
  const loadExpectations = async () => {
    try {
      setLoading(true);
      const response = await expectationService.getExpectations();
      setExpectations(response.data);
      return response.data;
    } catch (err) {
      setError(err.message || '加载期望失败');
      console.error('加载期望失败:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // 加载生成历史
  const loadGenerations = async () => {
    try {
      setLoading(true);
      const response = await generationService.getGenerations();
      setGenerations(response.data);
      return response.data;
    } catch (err) {
      setError(err.message || '加载生成历史失败');
      console.error('加载生成历史失败:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // 提供的上下文值
  const value = {
    expectations,
    generations,
    loading,
    error,
    loadExpectations,
    loadGenerations
  };

  return <ExpetaContext.Provider value={value}>{children}</ExpetaContext.Provider>;
};

// 自定义hook
export const useExpeta = () => {
  const context = useContext(ExpetaContext);
  if (!context) {
    throw new Error('useExpeta必须在ExpetaProvider内部使用');
  }
  return context;
};

export default ExpetaContext;
