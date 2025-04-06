# Expeta 2.0 使用指南：如何使用期望（Expectations）创建新模型

本指南将详细介绍如何使用Expeta 2.0系统中的期望（Expectations）来创建和测试新模型。我们将通过一个完整的示例来展示整个流程。

## 目录

1. [Expeta 2.0 系统概述](#1-expeta-20-系统概述)
2. [环境设置](#2-环境设置)
3. [定义期望（Expectations）](#3-定义期望expectations)
4. [使用期望创建新模型](#4-使用期望创建新模型)
5. [测试和验证模型](#5-测试和验证模型)
6. [完整示例：创建一个文本分类模型](#6-完整示例创建一个文本分类模型)
7. [常见问题解答](#7-常见问题解答)

## 1. Expeta 2.0 系统概述

Expeta 2.0是一个语义驱动的软件开发系统，它可以将自然语言需求转化为结构化的期望（Expectations），并基于这些期望生成代码。系统的核心组件包括：

- **Clarifier**：将自然语言需求转化为结构化的期望
- **Generator**：基于期望生成代码
- **Validator**：验证生成的代码是否满足期望
- **LLM Router**：管理与大型语言模型的交互
- **Memory System**：存储和检索期望、代码和验证结果

## 2. 环境设置

首先，确保您已经设置好环境变量，特别是LLM提供商的API密钥：

```bash
# 创建.env文件
cat > .env << EOL
# OpenAI API密钥
OPENAI_API_KEY=your_openai_api_key
OPENAI_PROJECT=your_openai_project_id
OPENAI_ORGANIZATION=your_openai_org_id

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key
EOL
```

安装必要的依赖：

```bash
pip install -r requirements.txt
```

## 3. 定义期望（Expectations）

期望（Expectations）是Expeta系统的核心概念，它们定义了您希望模型实现的功能和行为。期望可以通过两种方式创建：

### 3.1 通过自然语言需求创建期望

使用Clarifier组件将自然语言需求转化为结构化的期望：

```python
from expeta.clarifier.clarifier import Clarifier
from expeta.llm_router.llm_router import LLMRouter

# 创建LLM Router和Clarifier
llm_router = LLMRouter()
clarifier = Clarifier(llm_router=llm_router)

# 定义自然语言需求
requirement = """
创建一个文本分类模型，能够将输入的文本分类为'积极'、'中性'或'消极'情感。
模型应该能够处理中文和英文输入，并返回分类结果和置信度分数。
"""

# 使用Clarifier转化需求
expectation_result = clarifier.clarify_requirement(requirement)

# 获取顶层期望和子期望
top_level_expectation = expectation_result["top_level_expectation"]
sub_expectations = expectation_result["sub_expectations"]

print(f"顶层期望: {top_level_expectation['name']}")
for sub_exp in sub_expectations:
    print(f"子期望: {sub_exp['name']}")
```

### 3.2 直接定义结构化期望

您也可以直接定义结构化的期望，而不通过Clarifier：

```python
# 直接定义顶层期望
top_level_expectation = {
    "id": "exp-12345678",
    "name": "情感分类模型",
    "description": "创建一个能够分类文本情感的模型",
    "level": "top",
    "acceptance_criteria": [
        "能够将文本分类为'积极'、'中性'或'消极'",
        "支持中文和英文输入",
        "返回分类结果和置信度分数"
    ],
    "constraints": [
        "模型响应时间应小于500毫秒",
        "模型大小应小于100MB"
    ]
}

# 定义子期望
sub_expectations = [
    {
        "id": "exp-abcdef01",
        "name": "文本预处理",
        "description": "实现文本清洗和标准化功能",
        "level": "sub",
        "parent_id": "exp-12345678",
        "acceptance_criteria": [
            "移除特殊字符和多余空格",
            "转换为小写",
            "支持中英文字符"
        ],
        "constraints": []
    },
    {
        "id": "exp-abcdef02",
        "name": "情感分类",
        "description": "实现情感分类功能",
        "level": "sub",
        "parent_id": "exp-12345678",
        "acceptance_criteria": [
            "准确分类为'积极'、'中性'或'消极'",
            "提供置信度分数"
        ],
        "constraints": [
            "分类准确率应大于85%"
        ]
    }
]
```

## 4. 使用期望创建新模型

一旦定义了期望，您可以使用Generator组件基于这些期望创建新模型：

```python
from expeta.generator.generator import Generator

# 创建Generator
generator = Generator(llm_router=llm_router)

# 使用顶层期望生成代码
generation_result = generator.generate(top_level_expectation)

# 查看生成的代码
for file_info in generation_result["files"]:
    print(f"文件: {file_info['path']}")
    print(f"内容:\n{file_info['content']}\n")
```

生成的代码通常包括模型定义、训练脚本和使用示例。

## 5. 测试和验证模型

使用Validator组件验证生成的代码是否满足期望：

```python
from expeta.validator.validator import Validator

# 创建Validator
validator = Validator(llm_router=llm_router)

# 验证生成的代码
validation_result = validator.validate(generation_result, top_level_expectation)

# 查看验证结果
print(f"验证通过: {validation_result['passed']}")
print(f"语义匹配分数: {validation_result['semantic_match']['match_score']}")
print(f"测试结果: {validation_result['test_results']}")
```

## 6. 完整示例：创建一个文本分类模型

以下是一个完整的示例，展示如何使用Expeta 2.0创建一个文本分类模型：

```python
import json
from expeta.llm_router.llm_router import LLMRouter
from expeta.enhanced_clarifier.enhanced_clarifier import EnhancedClarifier
from expeta.generator.generator import Generator
from expeta.validator.validator import Validator
from expeta.memory.memory_system import MemorySystem
from expeta.utils.env_loader import load_dotenv

# 加载环境变量
load_dotenv()

# 创建组件
llm_router = LLMRouter()  # 默认使用Anthropic作为提供商
memory_system = MemorySystem()
clarifier = EnhancedClarifier(llm_router=llm_router)
generator = Generator(llm_router=llm_router)
validator = Validator(llm_router=llm_router)

# 定义自然语言需求
requirement = """
创建一个文本分类模型，能够将输入的文本分类为'积极'、'中性'或'消极'情感。
模型应该能够处理中文和英文输入，并返回分类结果和置信度分数。
"""

# 步骤1：使用Clarifier转化需求为期望
print("步骤1：转化需求为期望...")
expectation_result = clarifier.clarify_requirement(requirement)
top_level_expectation = expectation_result["top_level_expectation"]
sub_expectations = expectation_result["sub_expectations"]

# 保存期望到文件
with open("sentiment_model_expectations.json", "w", encoding="utf-8") as f:
    json.dump(expectation_result, f, ensure_ascii=False, indent=2)

print(f"顶层期望: {top_level_expectation['name']}")
for sub_exp in sub_expectations:
    print(f"子期望: {sub_exp['name']}")

# 步骤2：使用Generator基于期望生成代码
print("\n步骤2：生成代码...")
generation_result = generator.generate(top_level_expectation)

# 保存生成的代码到文件
for file_info in generation_result["files"]:
    file_path = file_info["path"]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_info["content"])
    print(f"已创建文件: {file_path}")

# 步骤3：使用Validator验证生成的代码
print("\n步骤3：验证代码...")
validation_result = validator.validate(generation_result, top_level_expectation)

# 保存验证结果到文件
with open("sentiment_model_validation.json", "w", encoding="utf-8") as f:
    json.dump(validation_result, f, ensure_ascii=False, indent=2)

print(f"验证通过: {validation_result['passed']}")
print(f"语义匹配分数: {validation_result['semantic_match']['match_score']}")

# 步骤4：同步到Memory System
print("\n步骤4：同步到Memory System...")
clarifier.sync_to_memory(memory_system)
generator.sync_to_memory(memory_system)
validator.sync_to_memory(memory_system)

print("\n完成！您现在可以使用生成的模型了。")

# 步骤5：查看Token使用情况
print("\n步骤5：查看Token使用情况...")
token_report = clarifier.get_token_usage_report()
print(f"总Token使用量: {token_report['total_tokens']}")
print(f"Anthropic Token使用量: {token_report['provider_tokens'].get('anthropic', 0)}")
print(f"OpenAI Token使用量: {token_report['provider_tokens'].get('openai', 0)}")
```

### 6.1 生成的模型示例

以下是可能生成的模型代码示例：

```python
# sentiment_classifier.py
import re
import jieba
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SentimentClassifier:
    """情感分类模型，支持中文和英文输入"""
    
    def __init__(self, model_name="bert-base-multilingual-cased"):
        """初始化情感分类器
        
        Args:
            model_name: 预训练模型名称
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=3
        )
        self.labels = ["消极", "中性", "积极"]
        
    def preprocess_text(self, text):
        """预处理文本
        
        Args:
            text: 输入文本
            
        Returns:
            预处理后的文本
        """
        # 移除特殊字符和多余空格
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 判断是否为中文
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            # 中文分词
            words = jieba.cut(text)
            text = ' '.join(words)
        
        return text.lower()
    
    def classify(self, text):
        """对文本进行情感分类
        
        Args:
            text: 输入文本
            
        Returns:
            字典，包含分类结果和置信度
        """
        # 预处理文本
        processed_text = self.preprocess_text(text)
        
        # 编码文本
        inputs = self.tokenizer(
            processed_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        )
        
        # 预测
        outputs = self.model(**inputs)
        logits = outputs.logits.detach().numpy()[0]
        
        # 计算概率
        probabilities = np.exp(logits) / np.sum(np.exp(logits))
        
        # 获取最高概率的类别
        predicted_class = np.argmax(probabilities)
        confidence = probabilities[predicted_class]
        
        return {
            "text": text,
            "sentiment": self.labels[predicted_class],
            "confidence": float(confidence),
            "probabilities": {
                label: float(prob) for label, prob in zip(self.labels, probabilities)
            }
        }
```

### 6.2 使用生成的模型

```python
# 使用示例
from sentiment_classifier import SentimentClassifier

# 初始化分类器
classifier = SentimentClassifier()

# 测试中文文本
chinese_text = "这个产品非常好用，我很满意！"
result = classifier.classify(chinese_text)
print(f"文本: {result['text']}")
print(f"情感: {result['sentiment']}")
print(f"置信度: {result['confidence']:.2f}")

# 测试英文文本
english_text = "This product is amazing, I'm very satisfied!"
result = classifier.classify(english_text)
print(f"文本: {result['text']}")
print(f"情感: {result['sentiment']}")
print(f"置信度: {result['confidence']:.2f}")
```

## 7. 常见问题解答

### 7.1 如何调整LLM提供商的优先级？

默认情况下，Expeta 2.0使用Anthropic作为首选LLM提供商，OpenAI作为备选。您可以通过修改LLMRouter的配置来调整优先级：

```python
from expeta.llm_router.llm_router import LLMRouter

# 创建自定义配置
config = {
    "default_provider": "anthropic",  # 或 "openai"
    "fallback_order": ["anthropic", "openai"],  # 调整备选顺序
    "providers": {
        "anthropic": {
            "model": "claude-3-sonnet-20240229"  # 指定模型版本
        },
        "openai": {
            "model": "gpt-4"  # 指定模型版本
        }
    }
}

# 使用自定义配置创建LLM Router
llm_router = LLMRouter(config=config)
```

### 7.2 如何监控Token使用情况？

使用EnhancedClarifier可以跟踪Token使用情况：

```python
from expeta.enhanced_clarifier.enhanced_clarifier import EnhancedClarifier

# 创建EnhancedClarifier
clarifier = EnhancedClarifier(llm_router=llm_router)

# 使用Clarifier...

# 获取Token使用报告
token_report = clarifier.get_token_usage_report()
print(f"总Token使用量: {token_report['total_tokens']}")
print(f"按提供商Token使用量: {token_report['provider_tokens']}")
```

### 7.3 如何保存和加载期望？

您可以使用JSON格式保存和加载期望：

```python
import json

# 保存期望到文件
with open("expectations.json", "w", encoding="utf-8") as f:
    json.dump(expectation_result, f, ensure_ascii=False, indent=2)

# 从文件加载期望
with open("expectations.json", "r", encoding="utf-8") as f:
    loaded_expectations = json.load(f)

top_level_expectation = loaded_expectations["top_level_expectation"]
sub_expectations = loaded_expectations["sub_expectations"]
```

### 7.4 如何使用Memory System检索历史期望和生成结果？

```python
from expeta.memory.memory_system import MemorySystem

# 创建Memory System
memory_system = MemorySystem()

# 检索期望
expectation = memory_system.get_expectation("exp-12345678")

# 检索生成的代码
code = memory_system.get_code_for_expectation("exp-12345678")

# 检索验证结果
validation = memory_system.get_validation_results(expectation_id="exp-12345678")
```

---

通过本指南，您应该能够使用Expeta 2.0系统中的期望（Expectations）来创建和测试新模型。如果您有任何问题，请参考系统文档或联系支持团队。
