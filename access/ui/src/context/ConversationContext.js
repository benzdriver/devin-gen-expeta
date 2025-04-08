/**
 * @file ConversationContext.js
 * @description 对话上下文管理，处理会话状态和消息
 * 
 * 需求:
 * 1. 提供当前会话状态和消息的访问
 * 2. 实现发送消息和接收响应的逻辑
 * 3. 管理会话状态转换
 * 4. 连接WebSocket服务，实现实时更新
 * 5. 处理会话数据的持久化
 * 
 * 提供的上下文值:
 * - currentConversation: 当前会话对象
 * - messages: 当前会话的消息列表
 * - conversationState: 当前会话状态
 * - sendMessage: 发送消息的函数
 * - startNewConversation: 开始新会话的函数
 * - loading: 加载状态
 * - error: 错误信息
 */

import React, { createContext, useState, useEffect, useContext } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
// 导入其他必要依赖

// Devin: 请在此实现ConversationContext
