"""
Mock LLM Provider for Expeta 2.0

This module provides a mock implementation of an LLM provider for testing purposes.
It returns predefined responses based on the input prompt.
"""

class MockProvider:
    """Mock LLM provider for testing"""

    def __init__(self, config=None):
        """Initialize the mock provider
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.model = self.config.get("model", "mock-model")
        
    def send_request(self, request):
        """Send request to the mock provider
        
        Args:
            request: Request data dictionary
            
        Returns:
            Response dictionary
        """
        prompt = request.get("prompt", "")
        
        if "Yes, that's correct" in prompt or "confirm" in prompt.lower() or "确认" in prompt or "正确" in prompt:
            print(f"DEBUG: Mock provider detected confirmation message in prompt")
            response_text = """非常感谢您的确认和补充信息！我已经理解了您的需求，并创建了相应的期望模型。您的个人网站将包含以下功能：

1. 响应式设计，适配移动端和桌面端
2. 无障碍设计，确保所有用户都能访问
3. 作品集展示区，用于展示您的设计作品
4. 博客系统，支持分类和评论功能
5. 联系表单，方便访客与您沟通

我们将使用现代化的技术栈来实现这些功能，确保网站性能优良且易于维护。您可以在"代码生成"页面查看和下载生成的代码。

expectation_id: test-creative-portfolio"""
            
            return {
                "text": response_text,
                "content": response_text,
                "provider": "mock",
                "model": self.model,
                "error": False,
                "expectation_id": "test-creative-portfolio",  # Add explicit expectation_id field
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": len(prompt.split()) + len(response_text.split())
                }
            }
        
        if "uncertainty" in prompt.lower() or "detect_uncertainty" in prompt.lower():
            response_text = self._generate_uncertainty_response(prompt)
        elif "extract" in prompt.lower() or "expectation" in prompt.lower():
            response_text = self._generate_expectation_response(prompt)
        elif "decompose" in prompt.lower() or "sub-expectations" in prompt.lower():
            response_text = self._generate_sub_expectations_response(prompt)
        elif "clarify" in prompt.lower() or "follow-up" in prompt.lower():
            response_text = self._generate_clarification_response(prompt)
        else:
            response_text = "This is a mock response for testing purposes."
            
        return {
            "text": response_text,
            "content": response_text,  # Add content field for compatibility
            "provider": "mock",
            "model": self.model,
            "error": False,
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(prompt.split()) + len(response_text.split())
            }
        }
        
    def _generate_uncertainty_response(self, prompt):
        """Generate response for uncertainty detection
        
        Args:
            prompt: Input prompt
            
        Returns:
            Response text
        """
        return """
[
  {
    "field": "description",
    "issue": "vague_term",
    "message": "博客功能描述不够具体，需要明确具体特性",
    "question": "您能详细描述博客功能需要包含哪些具体特性吗？例如文章发布、评论系统、分类标签等。"
  },
  {
    "field": "constraints",
    "issue": "missing_information",
    "message": "缺少性能和兼容性要求",
    "question": "您对网站的性能、安全性或兼容性有什么特殊要求吗？"
  }
]
        """
        
    def _generate_expectation_response(self, prompt):
        """Generate response for expectation extraction
        
        Args:
            prompt: Input prompt
            
        Returns:
            Response text
        """
        return """
{
  "top_level_expectation": {
    "id": "exp-12345",
    "name": "个人网站带博客功能",
    "description": "一个现代化的个人网站，包含博客系统，允许发布文章、添加评论和管理内容。",
    "acceptance_criteria": [
      "网站应有响应式设计，适配移动端和桌面端",
      "博客系统应支持文章发布、编辑和删除",
      "应有评论功能允许访客留言",
      "应有简单的内容管理系统"
    ],
    "constraints": [
      "使用React和Node.js技术栈",
      "部署简单，易于维护"
    ]
  }
}
        """
        
    def _generate_sub_expectations_response(self, prompt):
        """Generate response for sub-expectations decomposition
        
        Args:
            prompt: Input prompt
            
        Returns:
            Response text
        """
        return """
        {
          "sub_expectations": [
            {
              "id": "sub-exp-1",
              "name": "前端用户界面",
              "description": "响应式设计的前端界面，包括首页、关于页和博客页面",
              "acceptance_criteria": [
                "首页展示个人简介和最新博客文章",
                "关于页详细介绍个人经历和技能",
                "博客页面列出所有文章，支持分页和搜索"
              ]
            },
            {
              "id": "sub-exp-2",
              "name": "博客系统",
              "description": "完整的博客功能，支持文章管理和评论",
              "acceptance_criteria": [
                "支持Markdown格式编写文章",
                "文章可分类和添加标签",
                "评论系统支持嵌套回复"
              ]
            },
            {
              "id": "sub-exp-3",
              "name": "内容管理系统",
              "description": "简单的后台管理系统，用于管理博客内容",
              "acceptance_criteria": [
                "提供登录认证功能",
                "支持文章草稿和发布状态管理",
                "提供简单的数据统计功能"
              ]
            }
          ]
        }
        """
        
    def _generate_clarification_response(self, prompt):
        """Generate response for clarification questions
        
        Args:
            prompt: Input prompt
            
        Returns:
            Response text with expectation ID for testing
        """
        if "Yes, that's correct" in prompt or "确认" in prompt or "正确" in prompt or "confirm" in prompt.lower():
            return """非常感谢您的确认和补充信息！我已经理解了您的需求，并创建了相应的期望模型。您的个人网站将包含以下功能：

1. 响应式设计，适配移动端和桌面端
2. 无障碍设计，确保所有用户都能访问
3. 作品集展示区，用于展示您的设计作品
4. 博客系统，支持分类和评论功能
5. 联系表单，方便访客与您沟通

我们将使用现代化的技术栈来实现这些功能，确保网站性能优良且易于维护。您可以在"代码生成"页面查看和下载生成的代码。

expectation_id: test-creative-portfolio"""
        else:
            return """作为您的产品经理，我需要更深入地了解您的需求，以便为您提供最佳的解决方案。

首先，请告诉我这个项目属于哪个行业或领域？了解行业背景将帮助我提供更相关的建议和参考。

请帮我澄清以下几点：

1. 您能为这个需求提供一个更具体的名称吗？这将帮助我们更清晰地定义项目范围。

2. 在您看来，什么样的标准可以表明这个需求已经被成功实现了？用户应该能够完成哪些操作？

此外，您是否了解行业内类似的解决方案？它们有哪些值得借鉴的地方，或者有哪些不足之处需要我们改进？

您的详细反馈将帮助我更准确地理解您的需求，并设计出最符合您期望的解决方案。"""
