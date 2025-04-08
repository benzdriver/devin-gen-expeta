/**
 * @file useGeneration.js
 * @description 代码生成的自定义Hook
 * 
 * 需求:
 * 1. 封装代码生成逻辑，简化组件代码
 * 2. 管理生成状态和结果
 * 3. 处理生成请求和结果获取
 * 4. 提供进度更新通知
 * 
 * 返回值:
 * - generation: 当前生成结果
 * - generateCode: 生成代码的函数
 * - progress: 生成进度
 * - downloadCode: 下载代码的函数
 * - loading: 加载状态
 * - error: 错误信息
 */

import { useState, useEffect, useCallback } from 'react';
import { generationService, expectationService } from '../services/api';
import webSocketService from '../services/WebSocketService';
// 导入其他必要依赖

/**
 * 代码生成的自定义Hook
 * @param {string} generationId 生成ID
 */
const useGeneration = (generationId) => {
  const [generation, setGeneration] = useState(null);
  const [expectation, setExpectation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 加载生成结果
  const loadGeneration = useCallback(async (id) => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await generationService.getGeneration(id);
      setGeneration(response.data);
      
      // 如果有关联的期望ID，加载期望信息
      if (response.data.expectationId) {
        try {
          const expResponse = await expectationService.getExpectation(response.data.expectationId);
          setExpectation(expResponse.data);
        } catch (expError) {
          console.error('加载期望信息失败:', expError);
        }
      }
      
      return response.data;
    } catch (err) {
      setError(err.message || '加载生成结果失败');
      console.error('加载生成结果失败:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 加载生成历史
  const loadGenerations = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await generationService.getGenerations();
      return response.data;
    } catch (err) {
      setError(err.message || '加载生成历史失败');
      console.error('加载生成历史失败:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 下载代码
  const downloadCode = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await generationService.downloadGeneration(id || generationId);
      
      // 处理下载
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `generation-${id || generationId}.zip`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      return true;
    } catch (err) {
      setError(err.message || '下载代码失败');
      console.error('下载代码失败:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, [generationId]);

  // 自动加载生成结果
  useEffect(() => {
    if (generationId) {
      loadGeneration(generationId);
    }
  }, [generationId, loadGeneration]);

  return {
    generation,
    expectation,
    loading,
    error,
    loadGeneration,
    loadGenerations,
    downloadCode
  };
};

export default useGeneration;
