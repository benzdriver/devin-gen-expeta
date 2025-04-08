/**
 * @file ExpectationValidator.js
 * @description 期望数据的验证逻辑
 * 
 * 需求:
 * 1. 实现验证期望数据有效性的函数
 * 2. 验证必填字段存在且格式正确
 * 3. 验证字段间的逻辑关系
 * 4. 返回详细的验证错误信息
 * 
 * 验证规则包括:
 * - name: 非空，长度在3-100字符之间
 * - description: 可选，长度不超过1000字符
 * - acceptanceCriteria: 至少包含1项，每项长度在5-200字符之间
 * - constraints: 可选，每项长度在5-200字符之间
 */

/**
 * 验证期望数据
 * @param {Object} expectation 期望数据对象
 * @returns {Object} 包含isValid和errors属性的对象
 */
const validateExpectation = (expectation) => {
  const errors = {};

  // 验证name
  if (!expectation.name) {
    errors.name = '期望名称不能为空';
  } else if (expectation.name.length < 3 || expectation.name.length > 100) {
    errors.name = '期望名称长度必须在3-100字符之间';
  }

  // 验证description
  if (expectation.description && expectation.description.length > 1000) {
    errors.description = '期望描述长度不能超过1000字符';
  }

  // 验证acceptanceCriteria
  if (!expectation.acceptanceCriteria || expectation.acceptanceCriteria.length === 0) {
    errors.acceptanceCriteria = '必须至少有一条验收标准';
  } else {
    const invalidCriteria = expectation.acceptanceCriteria.filter(
      item => !item || item.length < 5 || item.length > 200
    );
    if (invalidCriteria.length > 0) {
      errors.acceptanceCriteria = '验收标准长度必须在5-200字符之间';
    }
  }

  // 验证constraints (可选)
  if (expectation.constraints && expectation.constraints.length > 0) {
    const invalidConstraints = expectation.constraints.filter(
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
};

/**
 * 验证单个验收标准
 * @param {string} criterion 验收标准文本
 * @returns {Object} 包含isValid和error属性的对象
 */
const validateAcceptanceCriterion = (criterion) => {
  if (!criterion) {
    return { isValid: false, error: '验收标准不能为空' };
  }
  
  if (criterion.length < 5) {
    return { isValid: false, error: '验收标准太短，至少需要5个字符' };
  }
  
  if (criterion.length > 200) {
    return { isValid: false, error: '验收标准太长，不能超过200个字符' };
  }
  
  return { isValid: true, error: null };
};

/**
 * 验证单个约束条件
 * @param {string} constraint 约束条件文本
 * @returns {Object} 包含isValid和error属性的对象
 */
const validateConstraint = (constraint) => {
  if (!constraint) {
    return { isValid: false, error: '约束条件不能为空' };
  }
  
  if (constraint.length < 5) {
    return { isValid: false, error: '约束条件太短，至少需要5个字符' };
  }
  
  if (constraint.length > 200) {
    return { isValid: false, error: '约束条件太长，不能超过200个字符' };
  }
  
  return { isValid: true, error: null };
};

export {
  validateExpectation,
  validateAcceptanceCriterion,
  validateConstraint
};

export default validateExpectation;
