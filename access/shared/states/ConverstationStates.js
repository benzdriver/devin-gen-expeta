/**
 * @file ConversationStates.js
 * @description 对话状态的共享定义
 * 
 * 需求:
 * 1. 定义对话的所有可能状态
 * 2. 描述状态间的有效转换
 * 3. 为每个状态提供清晰的描述
 * 4. 确保前后端使用一致的状态定义
 * 
 * 对话状态必须包括:
 * - INITIAL: 初始状态，会话刚创建
 * - COLLECTING_REQUIREMENT: 收集用户初始需求
 * - CLARIFYING: 澄清需求细节
 * - EXPECTATION_DRAFT: 期望草稿已形成
 * - EXPECTATION_CONFIRMED: 期望已确认
 * - GENERATING: 正在生成代码
 * - REVIEWING: 审核生成的代码
 * - COMPLETED: 流程完成
 */

/**
 * 对话状态常量
 */
const ConversationStates = {
  /**
   * 初始状态，会话刚创建
   */
  INITIAL: 'initial',
  
  /**
   * 收集用户初始需求
   */
  COLLECTING_REQUIREMENT: 'collecting_requirement',
  
  /**
   * 澄清需求细节
   */
  CLARIFYING: 'clarifying',
  
  /**
   * 期望草稿已形成
   */
  EXPECTATION_DRAFT: 'expectation_draft',
  
  /**
   * 期望已确认
   */
  EXPECTATION_CONFIRMED: 'expectation_confirmed',
  
  /**
   * 正在生成代码
   */
  GENERATING: 'generating',
  
  /**
   * 审核生成的代码
   */
  REVIEWING: 'reviewing',
  
  /**
   * 流程完成
   */
  COMPLETED: 'completed'
};

/**
 * 状态转换规则，定义了从每个状态可以转换到哪些状态
 */
const StateTransitions = {
  [ConversationStates.INITIAL]: [
    ConversationStates.COLLECTING_REQUIREMENT
  ],
  [ConversationStates.COLLECTING_REQUIREMENT]: [
    ConversationStates.CLARIFYING,
    ConversationStates.EXPECTATION_DRAFT
  ],
  [ConversationStates.CLARIFYING]: [
    ConversationStates.CLARIFYING,
    ConversationStates.EXPECTATION_DRAFT
  ],
  [ConversationStates.EXPECTATION_DRAFT]: [
    ConversationStates.CLARIFYING,
    ConversationStates.EXPECTATION_CONFIRMED
  ],
  [ConversationStates.EXPECTATION_CONFIRMED]: [
    ConversationStates.GENERATING,
    ConversationStates.CLARIFYING
  ],
  [ConversationStates.GENERATING]: [
    ConversationStates.REVIEWING
  ],
  [ConversationStates.REVIEWING]: [
    ConversationStates.COMPLETED,
    ConversationStates.GENERATING,
    ConversationStates.CLARIFYING
  ],
  [ConversationStates.COMPLETED]: [
    ConversationStates.INITIAL
  ]
};

/**
 * 状态描述，提供每个状态的可读描述
 */
const StateDescriptions = {
  [ConversationStates.INITIAL]: '会话初始化',
  [ConversationStates.COLLECTING_REQUIREMENT]: '收集需求中',
  [ConversationStates.CLARIFYING]: '澄清需求细节中',
  [ConversationStates.EXPECTATION_DRAFT]: '期望草稿已形成',
  [ConversationStates.EXPECTATION_CONFIRMED]: '期望已确认',
  [ConversationStates.GENERATING]: '生成代码中',
  [ConversationStates.REVIEWING]: '代码审核中',
  [ConversationStates.COMPLETED]: '流程已完成'
};

/**
 * 检查状态转换是否有效
 * @param {string} fromState 当前状态
 * @param {string} toState 目标状态
 * @returns {boolean} 状态转换是否有效
 */
const isValidTransition = (fromState, toState) => {
  if (!StateTransitions[fromState]) {
    return false;
  }
  return StateTransitions[fromState].includes(toState);
};

/**
 * 获取状态描述
 * @param {string} state 状态
 * @returns {string} 状态描述
 */
const getStateDescription = (state) => {
  return StateDescriptions[state] || '未知状态';
};

export {
  ConversationStates,
  StateTransitions,
  StateDescriptions,
  isValidTransition,
  getStateDescription
};

export default ConversationStates;
