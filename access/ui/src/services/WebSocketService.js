/**
 * @file WebSocketService.js
 * @description WebSocket服务，处理实时通信
 * 
 * 需求:
 * 1. 建立和维护WebSocket连接
 * 2. 处理消息发送和接收
 * 3. 实现断线重连和心跳检测
 * 4. 提供会话状态变化的通知
 * 5. 支持生成进度的实时更新
 * 
 * 主要方法:
 * - connect(token): 建立连接
 * - disconnect(): 断开连接
 * - sendMessage(message): 发送消息
 * - subscribe(eventType, callback): 订阅事件
 * - unsubscribe(subscription): 取消订阅
 */

/**
 * WebSocket服务类
 */
class WebSocketService {
  constructor(baseUrl) {
    this.baseUrl = baseUrl || 'ws://localhost:8000/ws';
    this.connection = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = null;
    this.pingInterval = null;
    this.subscriptions = new Map();
    this.eventListeners = new Map();
    this.connectionPromise = null;
    this.isConnecting = false;
    this.token = null;
  }

  /**
   * 初始化连接
   * @param {string} token 认证令牌
   * @returns {Promise} 连接Promise
   */
  connect(token) {
    // 如果已连接或正在连接，返回现有Promise
    if (this.connection && this.connection.readyState === WebSocket.OPEN) {
      return Promise.resolve(this.connection);
    }
    
    if (this.isConnecting) {
      return this.connectionPromise;
    }
    
    this.token = token;
    this.isConnecting = true;
    
    // 创建连接Promise
    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        const url = `${this.baseUrl}?token=${token}`;
        this.connection = new WebSocket(url);
        
        this.connection.onopen = () => {
          console.log('WebSocket连接已建立');
          this.reconnectAttempts = 0;
          this.startPingInterval();
          this.isConnecting = false;
          resolve(this.connection);
        };
        
        this.connection.onclose = (event) => {
          console.log(`WebSocket连接已关闭: ${event.code} ${event.reason}`);
          this.stopPingInterval();
          this.handleReconnect();
          
          // 触发关闭事件
          this.dispatchEvent('close', event);
        };
        
        this.connection.onerror = (error) => {
          console.error('WebSocket错误:', error);
          this.isConnecting = false;
          reject(error);
          
          // 触发错误事件
          this.dispatchEvent('error', error);
        };
        
        this.connection.onmessage = (event) => {
          this.handleMessage(event);
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
    
    return this.connectionPromise;
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.connection) {
      this.connection.close();
      this.connection = null;
    }
    
    this.stopPingInterval();
    this.clearReconnectTimeout();
    this.subscriptions.clear();
    this.isConnecting = false;
    this.connectionPromise = null;
  }

  /**
   * 发送消息
   * @param {Object} message 消息对象
   * @returns {Promise} 发送Promise
   */
  sendMessage(message) {
    return this.ensureConnected().then(() => {
      const messageString = typeof message === 'string' ? 
        message : JSON.stringify(message);
      
      this.connection.send(messageString);
      return true;
    });
  }

  /**
   * 确保已连接
   * @returns {Promise} 连接Promise
   */
  ensureConnected() {
    if (this.connection && this.connection.readyState === WebSocket.OPEN) {
      return Promise.resolve(this.connection);
    }
    
    return this.connect(this.token);
  }

  /**
   * 处理接收到的消息
   * @param {MessageEvent} event WebSocket消息事件
   */
  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      
      // 处理不同类型的消息
      if (data.type === 'ping') {
        // 响应ping消息
        this.sendMessage({ type: 'pong' });
        return;
      }
      
      // 触发消息事件
      this.dispatchEvent('message', data);
      
      // 处理特定类型的消息
      if (data.type) {
        this.dispatchEvent(data.type, data);
      }
      
      // 通知订阅者
      if (data.subscriptionId && this.subscriptions.has(data.subscriptionId)) {
        const callback = this.subscriptions.get(data.subscriptionId);
        callback(data);
      }
    } catch (error) {
      console.error('处理消息失败:', error);
    }
  }

  /**
   * 处理重连
   */
  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('达到最大重连次数，停止重连');
      this.dispatchEvent('reconnectFailed');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    
    console.log(`尝试重连 #${this.reconnectAttempts}，${delay}ms后...`);
    this.clearReconnectTimeout();
    
    this.reconnectTimeout = setTimeout(() => {
      console.log(`开始第${this.reconnectAttempts}次重连尝试`);
      this.connect(this.token).catch(() => {
        // 重连失败，将由onclose事件触发下一次重连
      });
    }, delay);
  }

  /**
   * 启动定时ping
   */
  startPingInterval() {
    this.stopPingInterval();
    this.pingInterval = setInterval(() => {
      if (this.connection && this.connection.readyState === WebSocket.OPEN) {
        this.sendMessage({ type: 'ping' }).catch(() => {
          // 发送ping失败，可能连接已断开
          this.connection.close();
        });
      }
    }, 30000); // 每30秒发送一次ping
  }

  /**
   * 停止定时ping
   */
  stopPingInterval() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * 清除重连定时器
   */
  clearReconnectTimeout() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  /**
   * 订阅特定事件
   * @param {string} eventType 事件类型
   * @param {Function} callback 回调函数
   * @returns {Object} 订阅对象
   */
  addEventListener(eventType, callback) {
    if (!this.eventListeners.has(eventType)) {
      this.eventListeners.set(eventType, new Set());
    }
    
    const listeners = this.eventListeners.get(eventType);
    listeners.add(callback);
    
    return {
      remove: () => {
        listeners.delete(callback);
        if (listeners.size === 0) {
          this.eventListeners.delete(eventType);
        }
      }
    };
  }

  /**
   * 触发事件
   * @param {string} eventType 事件类型
   * @param {any} data 事件数据
   */
  dispatchEvent(eventType, data) {
    if (this.eventListeners.has(eventType)) {
      const listeners = this.eventListeners.get(eventType);
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`事件处理器错误 (${eventType}):`, error);
        }
      });
    }
  }

  /**
   * 订阅会话更新
   * @param {string} conversationId 会话ID
   * @param {Function} callback 回调函数
   * @returns {Object} 订阅对象
   */
  subscribeToConversation(conversationId, callback) {
    const subscriptionId = `conversation:${conversationId}`;
    return this.subscribe(subscriptionId, callback);
  }

  /**
   * 订阅生成进度
   * @param {string} generationId 生成ID
   * @param {Function} callback 回调函数
   * @returns {Object} 订阅对象
   */
  subscribeToGeneration(generationId, callback) {
    const subscriptionId = `generation:${generationId}`;
    return this.subscribe(subscriptionId, callback);
  }

  /**
   * 订阅事件
   * @param {string} subscriptionId 订阅ID
   * @param {Function} callback 回调函数
   * @returns {Object} 订阅对象
   */
  subscribe(subscriptionId, callback) {
    this.subscriptions.set(subscriptionId, callback);
    
    // 发送订阅消息
    this.ensureConnected().then(() => {
      this.sendMessage({
        type: 'subscribe',
        subscriptionId
      });
    });
    
    return {
      subscriptionId,
      unsubscribe: () => this.unsubscribe(subscriptionId)
    };
  }

  /**
   * 取消订阅
   * @param {string} subscriptionId 订阅ID
   */
  unsubscribe(subscriptionId) {
    if (this.subscriptions.has(subscriptionId)) {
      this.subscriptions.delete(subscriptionId);
      
      // 发送取消订阅消息
      if (this.connection && this.connection.readyState === WebSocket.OPEN) {
        this.sendMessage({
          type: 'unsubscribe',
          subscriptionId
        }).catch(() => {
          // 忽略错误
        });
      }
    }
  }
}

// 创建全局单例
const webSocketService = new WebSocketService();

export default webSocketService;
