"""
@file storage.py
@description 文件存储服务，处理生成代码的存储和访问
"""

import os
import shutil
import zipfile
import datetime
import json
from typing import Dict, List, Optional, Any

class FileStorage:
    """文件存储管理器"""
    
    def __init__(self, base_dir="generations"):
        """
        初始化文件存储
        
        Args:
            base_dir: 基础目录
        """
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
    def store_generation(self, generation):
        """
        存储生成结果
        
        Args:
            generation: 生成任务或结果对象
            
        Returns:
            str: 输出目录
        """
        # 确保是字典形式
        if hasattr(generation, "to_dict"):
            generation_data = generation.to_dict()
        else:
            generation_data = generation
            
        # 创建输出目录
        output_dir = generation_data.get("output_dir") or os.path.join(self.base_dir, generation_data.get("id"))
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存元数据
        metadata = {
            "id": generation_data.get("id"),
            "expectation_id": generation_data.get("expectation_id"),
            "status": generation_data.get("status"),
            "timestamp": generation_data.get("timestamp"),
            "files": [f.get("path") for f in generation_data.get("files", [])]
        }
        
        with open(os.path.join(output_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
            
        # 存储文件
        for file_info in generation_data.get("files", []):
            self._store_file(output_dir, file_info)
            
        return output_dir
        
    def _store_file(self, base_dir, file_info):
        """
        存储单个文件
        
        Args:
            base_dir: 基础目录
            file_info: 文件信息
        """
        path = file_info.get("path")
        content = file_info.get("content", "")
        
        if not path:
            return
            
        # 创建目录
        file_path = os.path.join(base_dir, path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    def get_generation(self, generation_id):
        """
        获取生成结果
        
        Args:
            generation_id: 生成ID
            
        Returns:
            dict: 生成结果
        """
        # 构建路径
        dir_path = os.path.join(self.base_dir, generation_id)
        
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"生成结果不存在: {generation_id}")
            
        # 读取元数据
        try:
            with open(os.path.join(dir_path, "metadata.json"), "r") as f:
                metadata = json.load(f)
        except:
            metadata = {
                "id": generation_id,
                "files": []
            }
            
        # 读取文件
        files = []
        for root, _, filenames in os.walk(dir_path):
            for filename in filenames:
                if filename == "metadata.json":
                    continue
                    
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, dir_path)
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        files.append({
                            "path": rel_path,
                            "content": content
                        })
                except Exception as e:
                    print(f"读取文件失败: {file_path}, 错误: {str(e)}")
            
        return {
            "id": metadata["id"],
            "expectation_id": metadata["expectation_id"],
            "status": metadata["status"],
            "timestamp": metadata["timestamp"],
            "files": files
        }

    def create_zip_archive(self, generation_id):
        """
        创建生成结果的ZIP压缩包
        
        Args:
            generation_id: 生成ID
            
        Returns:
            str: 压缩包路径
        """
        # 构建路径
        dir_path = os.path.join(self.base_dir, generation_id)
        zip_path = f"{dir_path}.zip"
        
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"生成结果不存在: {generation_id}")
            
        # 创建压缩包
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, dir_path)
                    zipf.write(file_path, rel_path)
                    
        return zip_path
        
    def delete_generation(self, generation_id):
        """
        删除生成结果
        
        Args:
            generation_id: 生成ID
            
        Returns:
            bool: 是否成功删除
        """
        # 构建路径
        dir_path = os.path.join(self.base_dir, generation_id)
        zip_path = f"{dir_path}.zip"
        
        # 删除目录
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
            except Exception as e:
                print(f"删除目录失败: {dir_path}, 错误: {str(e)}")
                return False
                
        # 删除压缩包
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except Exception as e:
                print(f"删除压缩包失败: {zip_path}, 错误: {str(e)}")
                
        return True
        
    def list_generations(self):
        """
        列出所有生成结果
        
        Returns:
            list: 生成结果元数据列表
        """
        results = []
        
        # 遍历目录
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            
            # 只处理目录
            if os.path.isdir(item_path):
                # 读取元数据
                metadata_path = os.path.join(item_path, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                            results.append(metadata)
                    except Exception as e:
                        print(f"读取元数据失败: {metadata_path}, 错误: {str(e)}")
                        
        # 按时间排序
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results


class GenerationStorage:
    """生成结果存储"""
    
    def __init__(self, file_storage=None):
        """
        初始化生成结果存储
        
        Args:
            file_storage: 文件存储服务
        """
        self.file_storage = file_storage or FileStorage()
        
    def store(self, generation):
        """
        存储生成结果
        
        Args:
            generation: 生成任务或结果对象
            
        Returns:
            str: 输出目录
        """
        return self.file_storage.store_generation(generation)
        
    def get(self, generation_id):
        """
        获取生成结果
        
        Args:
            generation_id: 生成ID
            
        Returns:
            dict: 生成结果
        """
        return self.file_storage.get_generation(generation_id)
        
    def download(self, generation_id):
        """
        下载生成结果
        
        Args:
            generation_id: 生成ID
            
        Returns:
            str: 压缩包路径
        """
        return self.file_storage.create_zip_archive(generation_id)
        
    def delete(self, generation_id):
        """
        删除生成结果
        
        Args:
            generation_id: 生成ID
            
        Returns:
            bool: 是否成功删除
        """
        return self.file_storage.delete_generation(generation_id)
        
    def list(self):
        """
        列出所有生成结果
        
        Returns:
            list: 生成结果元数据列表
        """
        return self.file_storage.list_generations()
