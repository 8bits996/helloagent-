"""
UniversalAgent 增强版
包含多智能体协作、增强记忆和高级代码分析功能
"""

from .agents import (
    UniversalAgent,
    EnhancedUniversalAgent,
    create_enhanced_agent,
    quick_analyze,
    MultiAgentCoordinator,
    AgentFactory
)

from .tools import (
    BrowserTool,
    TerminalTool,
    FileEditTool,
    AdvancedCodeAnalysisTool
)

from .memory import (
    EnhancedMemorySystem,
    MemoryItem,
    ConversationContext
)

__version__ = "2.0.0"

__all__ = [
    # 智能体
    'UniversalAgent',
    'EnhancedUniversalAgent',
    'create_enhanced_agent',
    'quick_analyze',
    'MultiAgentCoordinator',
    'AgentFactory',
    
    # 工具
    'BrowserTool',
    'TerminalTool',
    'FileEditTool',
    'AdvancedCodeAnalysisTool',
    
    # 记忆系统
    'EnhancedMemorySystem',
    'MemoryItem',
    'ConversationContext',
]
