"""
@file conversation.py
@description 会话管理服务，处理用户与系统的对话
"""

import uuid
import datetime
import json
from typing import Dict, List, Optional, Any

class MessageProcessor:
    """消息处理器，处理会话中的消息"""
    
    def __init__(self, clarifier=None):
        """
        初始化消息处理器
        
        Args:
            clarifier: 需求澄清组件
        """
        self.clarifier = clarifier
        
    def process_message(self, session, message):
        """
        处理用户消息
        
        Args:
            session: 会话对象
            message: 消息对象
            
        Returns:
            dict: 处理结果
        """
        if not self.clarifier:
            # 模拟响应
            return {
                "type": "system_message",
                "content": f"收到您的消息: {message['content']}",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        # 根据会话状态处理消息
        state = session.get("state", "initial")
        
        if state == "initial":
            # 首次输入需求
            clarification_result = self.clarifier.process_input(message["content"])
            return {
                "type": "system_message",
                "content": clarification_result.get("message", "请告诉我更多关于您的需求"),
                "new_state": "collecting_requirement",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        elif state == "collecting_requirement" or state == "clarifying":
            # 继续澄清需求
            clarification_result = self.clarifier.process_input(message["content"])
            
            # 判断是否已形成期望草稿
            if clarification_result.get("expectation_draft"):
                return {
                    "type": "expectation_draft",
                    "content": "我已经理解了您的需求，以下是期望草稿:",
                    "expectation": clarification_result["expectation_draft"],
                    "new_state": "expectation_draft",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            else:
                return {
                    "type": "system_message",
                    "content": clarification_result.get("message", "请提供更多信息"),
                    "new_state": "clarifying",
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
        elif state == "expectation_draft":
            # 用户对期望草稿的反馈
            if "confirm" in message["content"].lower():
                return {
                    "type": "expectation_confirmed",
                    "content": "期望已确认，您可以开始生成代码",
                    "new_state": "expectation_confirmed",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            else:
                # 继续修改期望
                clarification_result = self.clarifier.refine_expectation(
                    session.get("current_expectation"), 
                    message["content"]
                )
                return {
                    "type": "expectation_updated",
                    "content": "我已更新期望草稿:",
                    "expectation": clarification_result["expectation_draft"],
                    "new_state": "expectation_draft",
                    "timestamp": datetime.datetime.now().isoformat()
                }
        
        # 默认响应
        return {
            "type": "system_message",
            "content": "我不确定您想做什么，请提供更多信息",
            "timestamp": datetime.datetime.now().isoformat()
        }


class ConversationSession:
    """会话实例，表示用户与系统的一次完整对话"""
    
    def __init__(self, session_id=None, user_id=None):
        """
        初始化会话实例
        
        Args:
            session_id: 会话ID，如不提供则自动生成
            user_id: 用户ID
        """
        self.id = session_id or f"conv_{uuid.uuid4()}"
        self.user_id = user_id
        self.state = "initial"
        self.messages = []
        self.current_expectation = None
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        
    def add_message(self, sender, content):
        """
        添加消息
        
        Args:
            sender: 消息发送者 ('user' 或 'system')
            content: 消息内容
            
        Returns:
            dict: 添加的消息对象
        """
        message = {
            "id": f"msg_{uuid.uuid4()}",
            "sender": sender,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        self.messages.append(message)
        self.updated_at = message["timestamp"]
        
        return message
        
    def update_state(self, new_state):
        """
        更新会话状态
        
        Args:
            new_state: 新状态
        """
        valid_states = [
            "initial", 
            "collecting_requirement", 
            "clarifying", 
            "expectation_draft", 
            "expectation_confirmed", 
            "generating", 
            "reviewing", 
            "completed"
        ]
        
        if new_state not in valid_states:
            raise ValueError(f"无效的状态: {new_state}")
            
        self.state = new_state
        self.updated_at = datetime.datetime.now().isoformat()
        
    def set_expectation(self, expectation):
        """
        设置当前期望
        
        Args:
            expectation: 期望对象
        """
        self.current_expectation = expectation
        self.updated_at = datetime.datetime.now().isoformat()
        
        # 如果期望已确认，更新状态
        if expectation and expectation.get("status") == "confirmed":
            self.update_state("expectation_confirmed")
            
    def to_dict(self):
        """
        转换为字典表示
        
        Returns:
            dict: 会话字典表示
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "state": self.state,
            "messages": self.messages,
            "current_expectation": self.current_expectation,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class ConversationManager:
    """会话管理器，管理多个会话"""
    
    def __init__(self, clarifier=None, generator=None):
        """
        初始化会话管理器
        
        Args:
            clarifier: 需求澄清组件
            generator: 代码生成组件
        """
        self.sessions = {}
        self.message_processor = MessageProcessor(clarifier)
        self.clarifier = clarifier
        self.generator = generator
        
    def create_session(self, user_id=None):
        """
        创建新会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            ConversationSession: 新创建的会话
        """
        session = ConversationSession(user_id=user_id)
        self.sessions[session.id] = session
        return session
        
    def get_session(self, session_id):
        """
        获取会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            ConversationSession: 会话对象，不存在则返回None
        """
        return self.sessions.get(session_id)
        
    def send_message(self, session_id, content, sender="user"):
        """
        发送消息
        
        Args:
            session_id: 会话ID
            content: 消息内容
            sender: 消息发送者，默认为"user"
            
        Returns:
            dict: 包含新消息和响应的结果
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")
            
        # 添加用户消息
        user_message = session.add_message(sender, content)
        
        # 处理消息并生成响应
        if sender == "user":
            response = self.message_processor.process_message(
                session.to_dict(), 
                user_message
            )
            
            # 添加系统响应
            system_message = session.add_message("system", response.get("content", ""))
            
            # 更新会话状态
            if "new_state" in response:
                session.update_state(response["new_state"])
                
            # 更新期望
            if "expectation" in response:
                session.set_expectation(response["expectation"])
                
            return {
                "user_message": user_message,
                "system_message": system_message,
                "session": session.to_dict(),
                "response_type": response.get("type")
            }
        
        return {
            "user_message": user_message,
            "session": session.to_dict()
        }
        
    def confirm_expectation(self, session_id, expectation_id):
        """
        确认期望
        
        Args:
            session_id: 会话ID
            expectation_id: 期望ID
            
        Returns:
            dict: 确认结果
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")
            
        if not session.current_expectation:
            raise ValueError("当前会话没有待确认的期望")
            
        if expectation_id != session.current_expectation.get("id"):
            raise ValueError(f"期望ID不匹配: {expectation_id}")
            
        # 更新期望状态
        session.current_expectation["status"] = "confirmed"
        session.update_state("expectation_confirmed")
        
        # 添加系统消息
        system_message = session.add_message(
            "system", 
            "期望已确认，您可以开始生成代码"
        )
        
        return {
            "success": True,
            "message": "期望已确认",
            "session": session.to_dict(),
            "system_message": system_message
        }
        
    def generate_code(self, session_id, expectation_id):
        """
        生成代码
        
        Args:
            session_id: 会话ID
            expectation_id: 期望ID
            
        Returns:
            dict: 生成结果
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")
            
        if not session.current_expectation:
            raise ValueError("当前会话没有已确认的期望")
            
        if expectation_id != session.current_expectation.get("id"):
            raise ValueError(f"期望ID不匹配: {expectation_id}")
            
        if session.current_expectation.get("status") != "confirmed":
            raise ValueError("期望尚未确认")
            
        # 更新会话状态
        session.update_state("generating")
        
        # 添加系统消息
        system_message = session.add_message(
            "system", 
            "开始生成代码，请稍候..."
        )
        
        # 如果没有生成器，返回模拟结果
        if not self.generator:
            generation_id = f"gen_{uuid.uuid4()}"
            return {
                "success": True,
                "message": "代码生成已开始",
                "generation_id": generation_id,
                "session": session.to_dict(),
                "system_message": system_message
            }
            
        # 使用生成器生成代码
        try:
            result = self.generator.generate(session.current_expectation)
            generation_id = result.get("id", f"gen_{uuid.uuid4()}")
            
            # 更新会话状态
            session.update_state("reviewing")
            
            # 添加系统消息
            completion_message = session.add_message(
                "system", 
                "代码生成完成，您可以查看结果"
            )
            
            return {
                "success": True,
                "message": "代码生成完成",
                "generation_id": generation_id,
                "generation_result": result,
                "session": session.to_dict(),
                "system_message": completion_message
            }
        except Exception as e:
            # 生成失败
            error_message = session.add_message(
                "system", 
                f"代码生成失败: {str(e)}"
            )
            
            return {
                "success": False,
                "message": f"代码生成失败: {str(e)}",
                "session": session.to_dict(),
                "system_message": error_message
            }
