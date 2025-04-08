/**
 * @file ExpectationModel.js
 * @description 期望(Expectation)的共享数据模型定义
 * 
 * 需求:
 * 1. 定义期望的完整数据结构，确保前后端一致
 * 2. 包含id, name, description, acceptance_criteria, constraints等字段
 * 3. 提供验证和序列化/反序列化方法
 * 4. 确保与GraphQL schema和UI展示需求兼容
 * 
 * 输出示例:
 * {
 *   id: "exp_12345",
 *   name: "用户认证模块",
 *   description: "实现安全的用户认证和会话管理",
 *   acceptanceCriteria: ["支持邮箱登录", "实现多因素认证", "防止暴力破解"],
 *   constraints: ["使用JWT令牌", "密码必须加密存储"],
 *   level: "top",
 *   parentId: null,
 *   status: "confirmed"
 * }
 */

class ExpectationModel {
  /**
   * 创建新的期望模型实例
   * @param {Object} data 期望数据
   */
  constructor(data = {}) {
    this.id = data.id || `exp_${Date.now().toString(36)}`;
    this.name = data.name || '';
    this.description = data.description || '';
    this.acceptanceCriteria = data.acceptanceCriteria || [];
    this.constraints = data.constraints || [];
    this.level = data.level || 'top';
    this.parentId = data.parentId || null;
    this.status = data.status || 'draft';
  }

  /**
   * 验证模型数据是否有效
   * @returns {Object} 包含isValid和errors属性的对象
   */
  validate() {
    const errors = {};

    // 验证name
    if (!this.name) {
      errors.name = '期望名称不能为空';
    } else if (this.name.length < 3 || this.name.length > 100) {
      errors.name = '期望名称长度必须在3-100字符之间';
    }

    // 验证description
    if (this.description && this.description.length > 1000) {
      errors.description = '期望描述长度不能超过1000字符';
    }

    // 验证acceptanceCriteria
    if (!this.acceptanceCriteria || this.acceptanceCriteria.length === 0) {
      errors.acceptanceCriteria = '必须至少有一条验收标准';
    } else {
      const invalidCriteria = this.acceptanceCriteria.filter(
        item => !item || item.length < 5 || item.length > 200
      );
      if (invalidCriteria.length > 0) {
        errors.acceptanceCriteria = '验收标准长度必须在5-200字符之间';
      }
    }

    // 验证constraints (可选)
    if (this.constraints && this.constraints.length > 0) {
      const invalidConstraints = this.constraints.filter(
        item => !item || item.length < 5 || item.length > 200
      );
      if (invalidConstraints.length > 0) {
        errors.constraints = '约束条件长度必须在5-200字符之间';
      }
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
      name: this.name,
      description: this.description,
      acceptanceCriteria: this.acceptanceCriteria,
      constraints: this.constraints,
      level: this.level,
      parentId: this.parentId,
      status: this.status
    };
  }

  /**
   * 从JSON对象创建期望模型实例
   * @param {Object} json JSON对象
   * @returns {ExpectationModel} 期望模型实例
   */
  static fromJSON(json) {
    return new ExpectationModel(json);
  }
}

export default ExpectationModel;
