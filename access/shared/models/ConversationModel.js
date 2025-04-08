/**
 * @file ConversationModel.js
 * @description 对话(Conversation)的共享数据模型定义
 * 
 * 需求:
 * 1. 定义对话会话的完整数据结构
 * 2. 包含id, state, messages, currentExpectation等字段
 * 3. 支持消息历史记录和状态转换
 * 4. 确保与WebSocket通信和UI展示需求兼容
 * 
 * 输出示例:
 * {
 *   id: "conv_12345",
 *   state: "clarifying",
 *   messages: [
 *     {
 *       id: "msg_1",
 *       sender: "user",
 *       content: "我需要一个用户认证系统",
 *       timestamp: "2023-06-15T10:25:00Z"
 *     },
 *     {
 *       id: "msg_2",
 *       sender: "system",
 *       content: "您需要支持哪些登录方式?",
 *       timestamp: "2023-06-15T10:25:05Z"
 *     }
 *   ],
 *   currentExpectation: { * 期望对象 * }
 * }
 */

class ConversationModel {
  /**
   * 创建新的对话模型实例
   * @param {Object} data 对话数据
   */
  constructor(data = {}) {
    this.id = data.id || `conv_${Date.now().toString(36)}`;
    this.state = data.state || 'initial';
    this.messages = data.messages || [];
    this.currentExpectation = data.currentExpectation || null;
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || new Date().toISOString();
    this.userId = data.userId || null;
  }

  /**
   * 添加新消息
   * @param {string} sender 发送者 ('user' 或 'system')
   * @param {string} content 消息内容
   * @returns {Object} 新增的消息对象
   */
  addMessage(sender, content) {
    const message = {
      id: `msg_${Date.now().toString(36)}`,
      sender,
      content,
      timestamp: new Date().toISOString()
    };
    
    this.messages.push(message);
    this.updatedAt = message.timestamp;
    
    return message;
  }

  /**
   * 更新会话状态
   * @param {string} newState 新状态
   */
  updateState(newState) {
    const validStates = [
      'initial',
      'collecting_requirement',
      'clarifying',
      'expectation_draft',
      'expectation_confirmed',
      'generating',
      'reviewing',
      'completed'
    ];
    
    if (!validStates.includes(newState)) {
      throw new Error(`无效的状态: ${newState}`);
    }
    
    this.state = newState;
    this.updatedAt = new Date().toISOString();
  }

  /**
   * 设置当前期望
   * @param {Object} expectation 期望对象
   */
  setExpectation(expectation) {
    this.currentExpectation = expectation;
    this.updatedAt = new Date().toISOString();
    
    // 如果期望已确认，更新状态
    if (expectation && expectation.status === 'confirmed') {
      this.updateState('expectation_confirmed');
    } else if (expectation) {
      this.updateState('expectation_draft');
    }
  }

  /**
   * 获取最后一条消息
   * @returns {Object|null} 最后一条消息或null
   */
  getLastMessage() {
    return this.messages.length > 0 ? this.messages[this.messages.length - 1] : null;
  }

  /**
   * 验证模型数据是否有效
   * @returns {Object} 包含isValid和errors属性的对象
   */
  validate() {
    const errors = {};

    // 验证state
    const validStates = [
      'initial',
      'collecting_requirement',
      'clarifying',
      'expectation_draft',
      'expectation_confirmed',
      'generating',
      'reviewing',
      'completed'
    ];
    
    if (!validStates.includes(this.state)) {
      errors.state = `状态必须是以下之一: ${validStates.join(', ')}`;
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }

  /**
   * 转换为可序列化对象
   * @returns {Object} 纯对象表示
   */
  toJSON() {
    return {
      id: this.id,
      state: this.state,
      messages: this.messages,
      currentExpectation: this.currentExpectation,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
      userId: this.userId
    };
  }

  /**
   * 从JSON对象创建对话模型实例
   * @param {Object} json JSON对象
   * @returns {ConversationModel} 对话模型实例
   */
  static fromJSON(json) {
    return new ConversationModel(json);
  }
}

export default ConversationModel;
