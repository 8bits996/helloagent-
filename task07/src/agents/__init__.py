"""
智能体相关代码
"""

from .agent_universal import UniversalAgent
from .enhanced_universal_agent import (
    EnhancedUniversalAgent,
    create_enhanced_agent,
    quick_analyze
)
from .multi_agent_coordinator import (
    MultiAgentCoordinator,
    TaskRequest,
    AgentResponse,
    TaskStatus,
    TaskPriority,
    AgentCapability,
    WorkflowBuilder,
    WorkflowTemplates
)
from .specialized_agents import (
    BaseSpecializedAgent,
    CodeAnalysisAgent,
    SecurityAuditAgent,
    PerformanceOptimizerAgent,
    DocumentationAgent,
    TestingAgent,
    AgentFactory
)

__all__ = [
    # 基础智能体
    'UniversalAgent',
    
    # 增强智能体
    'EnhancedUniversalAgent',
    'create_enhanced_agent',
    'quick_analyze',
    
    # 多智能体协调
    'MultiAgentCoordinator',
    'TaskRequest',
    'AgentResponse',
    'TaskStatus',
    'TaskPriority',
    'AgentCapability',
    'WorkflowBuilder',
    'WorkflowTemplates',
    
    # 专门化智能体
    'BaseSpecializedAgent',
    'CodeAnalysisAgent',
    'SecurityAuditAgent',
    'PerformanceOptimizerAgent',
    'DocumentationAgent',
    'TestingAgent',
    'AgentFactory',
]
