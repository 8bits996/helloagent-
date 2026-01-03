import pytest
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.llm_provider import LLMProvider
from app.agents.base_agent import AgentConfig

@pytest.fixture
def llm_provider():
    return LLMProvider(use_mock=True)

@pytest.fixture
def contract_markdown():
    return """
# 软件开发合同

**甲方**：科技创新有限公司
**乙方**：未来软件工作室

## 一、 项目内容
乙方负责开发智能客户管理系统。

## 二、 费用与支付
合同总金额为人民币500,000.00元。
1. 签订后支付30%。
2. 验收合格支付60%。
3. 一年维保期满支付10%。

## 三、 知识产权
本项目的知识产权归乙方所有，甲方拥有永久使用权。

## 四、 违约责任
任何一方违约，需支付合同金额5%的违约金。
"""
