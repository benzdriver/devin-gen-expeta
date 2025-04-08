/**
 * @file useConversation.js
 * @description 对话管理的自定义Hook
 * 
 * 需求:
 * 1. 封装对话操作逻辑，简化组件代码
 * 2. 管理会话状态和消息
 * 3. 处理消息发送和接收
 * 4. 提供状态更新通知
 * 
 * 返回值:
 * - conversation: 当前会话对象
 * - messages: 消息列表
 * - sendMessage: 发送消息的函数
 * - startNewConversation: 开始新会话的函数
 * - loading: 加载状态
 * - error: 错误信息
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { ConversationStates } from '../../shared/states/ConversationStates';
import { conversationService } from '../services/api';

/**
 * 对话管理Hook
 * @param {string} conversationId 会话ID
 */
const useConversation = (conversationId) => {
  const [conversation, setConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  // 加载会话
  const loadConversation = useCallback(async (id) => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await conversationService.getConversation(id);
      setConversation(response.data);
      setMessages(response.data.messages || []);
    } catch (err) {
      setError(err.message || '加载会话失败');
      console.error('加载会话失败:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始化WebSocket连接
  const initWebSocket = useCallback((id) => {
    // 关闭现有连接
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    // 模拟WebSocket服务，实际项目中应连接到真实服务
    const mockWs = {
      close: () => console.log('关闭WebSocket连接'),
      onmessage: null,
      send: (data) => {
        console.log('WebSocket发送消息:', data);
        // 模拟消息回复
        setTimeout(() => {
          if (mockWs.onmessage) {
            const response = {
              type: 'message',
              data: JSON.stringify({
                message: {
                  id: `msg_${Date.now()}`,
                  sender: 'system',
                  content: '这是系统的自动回复',
                  timestamp: new Date().toISOString()
                }
              })
            };
            mockWs.onmessage(response);
          }
        }, 1000);
      }
    };
    
    wsRef.current = mockWs;
    console.log(`WebSocket连接已建立: ${id}`);
    
    // 设置消息处理函数
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.message) {
          setMessages(prev => [...prev, data.message]);
        }
        
        if (data.conversation) {
          setConversation(data.conversation);
        }
      } catch (err) {
        console.error('处理WebSocket消息失败:', err);
      }
    };
    
    return mockWs;
  }, []);

  // 会话ID变化时加载会话
  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
      initWebSocket(conversationId);
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [conversationId, loadConversation, initWebSocket]);

  // 发送消息
  const sendMessage = useCallback(async (content) => {
    if (!conversationId || !content) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // 通过WebSocket发送消息
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'message',
          conversationId,
          content
        }));
      }
      
      // 同时通过API发送以确保可靠性
      const response = await conversationService.sendMessage(conversationId, content);
      return response.data;
    } catch (err) {
      setError(err.message || '发送消息失败');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  // 开始新会话
  const startNewConversation = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await conversationService.createConversation();
      setConversation(response.data);
      setMessages([]);
      return response.data;
    } catch (err) {
      setError(err.message || '创建会话失败');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 确认期望
  const confirmExpectation = useCallback(async (expectationId) => {
    if (!conversationId || !expectationId) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await conversationService.confirmExpectation(
        conversationId, 
        expectationId
      );
      
      // 更新会话状态
      if (response.data) {
        setConversation(prev => ({
          ...prev,
          state: ConversationStates.EXPECTATION_CONFIRMED,
          currentExpectation: {
            ...prev.currentExpectation,
            status: 'confirmed'
          }
        }));
      }
      
      return response.data;
    } catch (err) {
      setError(err.message || '确认期望失败');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  // 生成代码
  const generateCode = useCallback(async (expectationId) => {
    if (!conversationId || !expectationId) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // 更新会话状态
      setConversation(prev => ({
        ...prev,
        state: ConversationStates.GENERATING
      }));
      
      const response = await conversationService.generateCode(
        conversationId, 
        expectationId
      );
      
      return response.data;
    } catch (err) {
      setError(err.message || '生成代码失败');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  return {
    conversation,
    messages,
    sendMessage,
    startNewConversation,
    confirmExpectation,
    generateCode,
    loading,
    error
  };
};

export default useConversation;
