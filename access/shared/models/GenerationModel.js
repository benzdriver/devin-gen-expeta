/**
 * @file GenerationModel.js
 * @description 代码生成(Generation)的共享数据模型定义
 * 
 * 需求:
 * 1. 定义代码生成结果的完整数据结构
 * 2. 包含id, expectationId, files, status, timestamp等字段
 * 3. 支持生成进度跟踪
 * 4. 确保与存储服务和UI展示需求兼容
 * 
 * 输出示例:
 * {
 *   id: "gen_12345",
 *   expectationId: "exp_12345",
 *   status: "completed",
 *   progress: 100,
 *   timestamp: "2023-06-15T10:30:00Z",
 *   outputDir: "generations/gen_12345",
 *   files: [
 *     {
 *       path: "src/auth.js",
 *       content: "// 文件内容...",
 *       language: "javascript"
 *     }
 *   ]
 * }
 */

class GenerationModel {
  /**
   * 创建新的代码生成模型实例
   * @param {Object} data 代码生成数据
   */
  constructor(data = {}) {
    this.id = data.id || `gen_${Date.now().toString(36)}`;
    this.expectationId = data.expectationId || null;
    this.status = data.status || 'pending'; // pending, generating, completed, failed
    this.progress = data.progress || 0;
    this.timestamp = data.timestamp || new Date().toISOString();
    this.outputDir = data.outputDir || `generations/${this.id}`;
    this.files = data.files || [];
    this.error = data.error || null;
  }

  /**
   * 验证模型数据是否有效
   * @returns {Object} 包含isValid和errors属性的对象
   */
  validate() {
    const errors = {};

    // 验证expectationId
    if (!this.expectationId) {
      errors.expectationId = '必须关联一个期望ID';
    }

    // 验证status
    const validStatuses = ['pending', 'generating', 'completed', 'failed'];
    if (!validStatuses.includes(this.status)) {
      errors.status = `状态必须是以下之一: ${validStatuses.join(', ')}`;
    }

    // 验证progress
    if (typeof this.progress !== 'number' || this.progress < 0 || this.progress > 100) {
      errors.progress = '进度必须是0-100之间的数字';
    }

    // 验证files (如果状态是已完成)
    if (this.status === 'completed' && (!this.files || this.files.length === 0)) {
      errors.files = '已完成的生成必须包含至少一个文件';
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }

  /**
   * 更新生成进度
   * @param {number} progress 进度百分比 (0-100)
   */
  updateProgress(progress) {
    this.progress = Math.min(Math.max(0, progress), 100);
    if (this.progress > 0 && this.status === 'pending') {
      this.status = 'generating';
    }
    if (this.progress === 100) {
      this.status = 'completed';
    }
  }

  /**
   * 添加生成的文件
   * @param {Object} file 文件对象，包含path, content和language属性
   */
  addFile(file) {
    if (!file || !file.path || !file.content) {
      throw new Error('文件必须包含path和content属性');
    }
    
    // 检查是否已存在同路径文件，存在则替换
    const existingIndex = this.files.findIndex(f => f.path === file.path);
    if (existingIndex >= 0) {
      this.files[existingIndex] = file;
    } else {
      this.files.push(file);
    }
  }

  /**
   * 标记生成失败
   * @param {string} errorMessage 错误信息
   */
  setFailed(errorMessage) {
    this.status = 'failed';
    this.error = errorMessage;
  }

  /**
   * 转换为可序列化对象
   * @returns {Object} 纯对象表示
   */
  toJSON() {
    return {
      id: this.id,
      expectationId: this.expectationId,
      status: this.status,
      progress: this.progress,
      timestamp: this.timestamp,
      outputDir: this.outputDir,
      files: this.files,
      error: this.error
    };
  }

  /**
   * 从JSON对象创建代码生成模型实例
   * @param {Object} json JSON对象
   * @returns {GenerationModel} 代码生成模型实例
   */
  static fromJSON(json) {
    return new GenerationModel(json);
  }
}

export default GenerationModel;
