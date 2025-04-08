"""
@file generation.py
@description 代码生成服务，处理从期望到代码的生成
"""

import uuid
import datetime
import os
import json
import shutil
from typing import Dict, List, Optional, Any

class GenerationTask:
    """代码生成任务实例"""
    
    def __init__(self, expectation, task_id=None, output_dir=None):
        """
        初始化生成任务
        
        Args:
            expectation: 期望对象
            task_id: 任务ID，如不提供则自动生成
            output_dir: 输出目录，如不提供则根据ID自动生成
        """
        self.id = task_id or f"gen_{uuid.uuid4()}"
        self.expectation_id = expectation.get("id")
        self.expectation = expectation
        self.status = "pending"
        self.progress = 0
        self.files = []
        self.output_dir = output_dir or f"generations/{self.id}"
        self.error = None
        self.timestamp = datetime.datetime.now().isoformat()
        
    def update_progress(self, progress):
        """
        更新进度
        
        Args:
            progress: 进度百分比 (0-100)
        """
        self.progress = min(max(0, progress), 100)
        
        if self.progress > 0 and self.status == "pending":
            self.status = "generating"
            
        if self.progress >= 100:
            self.status = "completed"
            
    def set_failed(self, error_message):
        """
        标记任务失败
        
        Args:
            error_message: 错误信息
        """
        self.status = "failed"
        self.error = error_message
        
    def add_file(self, path, content, language=None):
        """
        添加生成的文件
        
        Args:
            path: 文件路径
            content: 文件内容
            language: 编程语言
        """
        file_info = {
            "path": path,
            "content": content
        }
        
        if language:
            file_info["language"] = language
            
        # 检查是否已存在同路径文件
        existing_index = next((i for i, f in enumerate(self.files) if f["path"] == path), None)
        if existing_index is not None:
            self.files[existing_index] = file_info
        else:
            self.files.append(file_info)
            
    def to_dict(self):
        """
        转换为字典表示
        
        Returns:
            dict: 任务字典表示
        """
        return {
            "id": self.id,
            "expectation_id": self.expectation_id,
            "status": self.status,
            "progress": self.progress,
            "files": self.files,
            "output_dir": self.output_dir,
            "error": self.error,
            "timestamp": self.timestamp
        }


class CodeProcessor:
    """代码处理器，处理生成的代码"""
    
    def __init__(self, storage_service=None):
        """
        初始化代码处理器
        
        Args:
            storage_service: 存储服务
        """
        self.storage_service = storage_service
        
    def process_generated_code(self, task, generated_code):
        """
        处理生成的代码
        
        Args:
            task: 生成任务
            generated_code: 生成的代码
            
        Returns:
            bool: 处理是否成功
        """
        if not generated_code:
            task.set_failed("生成的代码为空")
            return False
            
        # 处理生成的文件
        try:
            if isinstance(generated_code, dict):
                # 处理包含多个文件的对象
                files = generated_code.get("files", [])
                language = generated_code.get("language")
                
                for file in files:
                    task.add_file(
                        file.get("path", "unknown.txt"),
                        file.get("content", ""),
                        language or file.get("language")
                    )
            elif isinstance(generated_code, str):
                # 单个文件内容
                task.add_file("main.txt", generated_code)
            else:
                task.set_failed("无法识别的代码格式")
                return False
                
            # 保存到存储服务
            if self.storage_service:
                self.storage_service.store_generation(task)
                
            task.update_progress(100)
            return True
        except Exception as e:
            task.set_failed(f"处理代码失败: {str(e)}")
            return False


class GenerationManager:
    """生成任务管理器"""
    
    def __init__(self, generator=None, storage_service=None):
        """
        初始化生成任务管理器
        
        Args:
            generator: 代码生成组件
            storage_service: 存储服务
        """
        self.tasks = {}
        self.generator = generator
        self.code_processor = CodeProcessor(storage_service)
        
    def create_task(self, expectation):
        """
        创建生成任务
        
        Args:
            expectation: 期望对象
            
        Returns:
            GenerationTask: 创建的任务
        """
        task = GenerationTask(expectation)
        self.tasks[task.id] = task
        return task
        
    def get_task(self, task_id):
        """
        获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            GenerationTask: 任务对象，不存在则返回None
        """
        return self.tasks.get(task_id)
        
    def generate(self, expectation):
        """
        生成代码
        
        Args:
            expectation: 期望对象
            
        Returns:
            dict: 生成结果
        """
        # 创建任务
        task = self.create_task(expectation)
        
        # 如果没有生成器，返回模拟结果
        if not self.generator:
            # 模拟生成过程
            task.add_file("src/main.js", "// 这是模拟生成的代码\nconsole.log('Hello world!');", "javascript")
            task.add_file("src/utils.js", "// 工具函数\nexport function greet(name) {\n  return `Hello, ${name}!`;\n}", "javascript")
            task.add_file("README.md", "# 示例项目\n\n这是一个模拟生成的项目。", "markdown")
            task.update_progress(100)
            
            return task.to_dict()
            
        # 使用生成器生成代码
        try:
            # 开始生成
            task.status = "generating"
            
            # 实际调用生成器
            result = self.generator.generate(expectation)
            
            # 处理生成结果
            self.code_processor.process_generated_code(task, result)
            
            return task.to_dict()
        except Exception as e:
            task.set_failed(f"生成失败: {str(e)}")
            return task.to_dict()
