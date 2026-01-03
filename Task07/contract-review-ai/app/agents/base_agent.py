from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Agent配置"""
    name: str
    display_name: str
    role: str
    system_prompt: str
    capabilities: List[str]
    knowledge_bases: List[str]
    input_schema: Dict
    output_schema: Dict
    model: str = "claude-3-5-sonnet"  # 默认模型
    temperature: float = 0.0

@dataclass
class AgentResult:
    """Agent执行结果"""
    agent_name: str
    status: str  # "completed", "failed"
    output: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, config: AgentConfig, llm_provider):
        self.config = config
        self.llm = llm_provider
        self.name = config.name
        self.display_name = config.display_name
        self.logger = logging.getLogger(f"agent.{self.name}")
    
    @abstractmethod
    async def execute(self, input_data: Dict, context: Dict) -> AgentResult:
        """执行Agent任务
        
        Args:
            input_data: 当前任务的输入数据
            context: 上下文信息（包括其他Agent的输出、全局配置等）
            
        Returns:
            AgentResult: 执行结果
        """
        pass
    
    def get_info(self) -> Dict:
        """获取Agent信息"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "role": self.config.role,
            "capabilities": self.config.capabilities
        }
    
    def _validate_input(self, input_data: Dict) -> bool:
        """简单的输入验证 (可扩展为JSON Schema验证)"""
        # 这里可以实现基于 input_schema 的验证逻辑
        return True

    def _format_prompt(self, template: str, **kwargs) -> str:
        """格式化Prompt"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"Prompt formatting error: missing key {e}")
            raise
