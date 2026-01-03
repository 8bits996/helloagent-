"""
增强版UniversalAgent - 集成多智能体协作、增强记忆和高级代码分析
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from hello_agents import HelloAgentsLLM, SimpleAgent, ToolRegistry

from src.tools.browser_tool import BrowserTool
from src.tools.terminal_tool import TerminalTool
from src.tools.file_tool import FileEditTool
from src.tools.advanced_code_analysis_tool import AdvancedCodeAnalysisTool
from src.agents.config import (
    TERMINAL_SECURITY_MODE, 
    AGENT_NAME
)
from src.memory.enhanced_memory_system import (
    EnhancedMemorySystem,
    MemoryType,
    ImportanceLevel
)
from src.agents.multi_agent_coordinator import (
    MultiAgentCoordinator,
    TaskRequest,
    AgentCapability,
    TaskPriority,
    WorkflowTemplates
)
from src.agents.specialized_agents import (
    AgentFactory,
    CodeAnalysisAgent,
    SecurityAuditAgent,
    PerformanceOptimizerAgent,
    DocumentationAgent,
    TestingAgent
)


# 增强版系统提示词
ENHANCED_SYSTEM_PROMPT = """你是一个增强版通用智能助手，具备多智能体协作、智能记忆和高级代码分析能力。

## 🛠️ 可用工具
1. **browser_search**: [TOOL_CALL:browser_search:搜索关键词] - 执行网页搜索
2. **terminal_exec**: [TOOL_CALL:terminal_exec:终端命令] - 执行受限的终端命令
3. **file_edit**: [TOOL_CALL:file_edit:path=路径,content=内容] - 编辑或创建文件
4. **code_analysis**: [TOOL_CALL:code_analysis:path=路径] - 高级代码分析（安全/性能/风格/复杂度/Bug风险）

## 🤖 多智能体协作能力
你可以调用专门化智能体来处理复杂任务：
- **代码分析专家**: 深度代码质量分析
- **安全审计专家**: 安全漏洞扫描
- **性能优化专家**: 性能问题检测
- **文档生成专家**: 自动生成文档
- **测试专家**: 测试用例生成

## 🧠 智能记忆系统
- 自动记住重要的对话内容和上下文
- 根据历史对话提供更精准的回答
- 支持跨会话的知识积累

## 💡 使用指南

### 代码分析示例
用户: 分析一下这个Python文件的代码质量
AI: [TOOL_CALL:code_analysis:path=example.py]
AI: 分析完成，发现以下问题...

### 多智能体协作示例
用户: 对这个项目进行全面的代码审查
AI: 我将调用多个专家智能体进行协作分析...
    1. 代码分析专家 - 分析代码结构和质量
    2. 安全审计专家 - 检查安全漏洞
    3. 性能优化专家 - 识别性能问题
    4. 文档生成专家 - 生成审查报告

## 🎯 核心原则
1. **智能协作**: 根据任务复杂度自动调用合适的专家智能体
2. **上下文感知**: 利用记忆系统理解用户意图
3. **全面分析**: 多维度分析代码问题
4. **主动建议**: 根据分析结果提供改进建议

你是一个强大的智能助手，善于协调多个专家来解决复杂问题！
"""


class EnhancedUniversalAgent(SimpleAgent):
    """增强版UniversalAgent"""
    
    def __init__(
        self,
        enable_multi_agent: bool = True,
        enable_memory: bool = True,
        enable_code_analysis: bool = True,
        memory_db_path: str = "data/memory.db",
        max_workers: int = 4,
        skip_llm_init: bool = False
    ):
        """
        初始化增强版智能体
        
        Args:
            enable_multi_agent: 是否启用多智能体协作
            enable_memory: 是否启用增强记忆
            enable_code_analysis: 是否启用高级代码分析
            memory_db_path: 记忆数据库路径
            max_workers: 多智能体并行工作数
            skip_llm_init: 是否跳过LLM初始化（用于测试）
        """
        # 创建工具注册表
        tool_registry = ToolRegistry()
        tool_registry.register_tool(BrowserTool())
        tool_registry.register_tool(TerminalTool(security_mode=TERMINAL_SECURITY_MODE))
        tool_registry.register_tool(FileEditTool())
        
        # 注册高级代码分析工具
        if enable_code_analysis:
            tool_registry.register_tool(AdvancedCodeAnalysisTool())
        
        # 根据是否跳过LLM初始化来决定初始化方式
        self._llm_initialized = False
        if skip_llm_init:
            # 跳过LLM初始化，仅设置基本属性
            self.name = f"Enhanced{AGENT_NAME}"
            self.system_prompt = ENHANCED_SYSTEM_PROMPT
            self.tool_registry = tool_registry
            self.llm = None
        else:
            # 从环境变量读取 LLM 配置
            llm = HelloAgentsLLM(
                provider=os.getenv('LLM_PROVIDER', 'modelscope'),
                model=os.getenv('LLM_MODEL', 'Qwen/Qwen3-VL-8B-Instruct'),
                api_key=os.getenv('LLM_API_KEY'),
                base_url=os.getenv('LLM_API_BASE')
            )
            
            # 初始化父类
            super().__init__(
                name=f"Enhanced{AGENT_NAME}",
                llm=llm,
                system_prompt=ENHANCED_SYSTEM_PROMPT,
                tool_registry=tool_registry
            )
            self._llm_initialized = True
        
        # 功能开关
        self.enable_multi_agent = enable_multi_agent
        self.enable_memory = enable_memory
        self.enable_code_analysis = enable_code_analysis
        
        # 初始化增强记忆系统
        self.memory_system = None
        if enable_memory:
            self.memory_system = EnhancedMemorySystem(db_path=memory_db_path)
            self.memory_system.start_session()
        
        # 初始化多智能体协调器
        self.coordinator = None
        if enable_multi_agent:
            self.coordinator = MultiAgentCoordinator(max_workers=max_workers)
            self._register_specialized_agents()
        
        # 会话状态
        self.session_start_time = datetime.now()
        self.interaction_count = 0
        self.last_query = None
        self.last_response = None
    
    def _register_specialized_agents(self):
        """注册专门化智能体"""
        agents = AgentFactory.create_all()
        for agent in agents:
            self.coordinator.register_agent(agent)
    
    def run(self, input_text: str, **kwargs) -> str:
        """运行Agent处理用户输入"""
        self.interaction_count += 1
        self.last_query = input_text
        
        # 记录用户输入到记忆系统
        if self.memory_system:
            self.memory_system.add_interaction('user', input_text)
        
        # 分析输入，决定是否需要多智能体协作
        needs_collaboration = self._analyze_collaboration_need(input_text)
        
        if needs_collaboration and self.coordinator:
            # 使用多智能体协作处理
            response = self._handle_with_collaboration(input_text)
        else:
            # 使用标准处理流程
            # 获取相关上下文
            context = ""
            if self.memory_system:
                context = self.memory_system.get_relevant_context(input_text)
            
            # 增强输入
            enhanced_input = input_text
            if context:
                enhanced_input = f"[上下文信息]\n{context}\n\n[用户问题]\n{input_text}"
            
            # 调用父类方法
            response = super().run(enhanced_input, **kwargs)
        
        # 记录响应到记忆系统
        if self.memory_system:
            self.memory_system.add_interaction('assistant', response)
            
            # 根据响应重要性保存记忆
            if self._is_important_response(response):
                self.memory_system.add_memory(
                    content=f"Q: {input_text}\nA: {response[:500]}",
                    memory_type=MemoryType.EPISODIC,
                    importance=ImportanceLevel.HIGH,
                    context_tags=['qa', 'important']
                )
        
        self.last_response = response
        return response
    
    def _analyze_collaboration_need(self, input_text: str) -> bool:
        """分析是否需要多智能体协作"""
        # 关键词检测
        collaboration_keywords = [
            '代码审查', '全面分析', '安全审计', '性能优化',
            '代码质量', '重构', '测试', '文档生成',
            'code review', 'security audit', 'performance',
            '多角度', '综合分析', '深度分析'
        ]
        
        input_lower = input_text.lower()
        return any(kw in input_lower for kw in collaboration_keywords)
    
    def _handle_with_collaboration(self, input_text: str) -> str:
        """使用多智能体协作处理请求"""
        # 解析任务类型
        task_type = self._determine_task_type(input_text)
        
        # 提取代码路径（如果有）
        code_path = self._extract_code_path(input_text)
        
        if task_type == 'code_review' and code_path:
            # 使用代码审查工作流
            return self._execute_code_review_workflow(code_path)
        elif task_type == 'security_audit' and code_path:
            # 执行安全审计
            return self._execute_security_audit(code_path)
        elif task_type == 'performance_analysis' and code_path:
            # 执行性能分析
            return self._execute_performance_analysis(code_path)
        else:
            # 通用协作处理
            return self._execute_general_collaboration(input_text)
    
    def _determine_task_type(self, input_text: str) -> str:
        """确定任务类型"""
        input_lower = input_text.lower()
        
        if any(kw in input_lower for kw in ['代码审查', 'code review', '全面分析', '综合分析']):
            return 'code_review'
        elif any(kw in input_lower for kw in ['安全', 'security', '漏洞', 'vulnerability']):
            return 'security_audit'
        elif any(kw in input_lower for kw in ['性能', 'performance', '优化', 'optimize']):
            return 'performance_analysis'
        else:
            return 'general'
    
    def _extract_code_path(self, input_text: str) -> Optional[str]:
        """从输入中提取代码路径"""
        import re
        
        # 匹配文件路径
        patterns = [
            r'[\w\-./\\]+\.py',
            r'[\w\-./\\]+\.js',
            r'[\w\-./\\]+\.ts',
            r'[\w\-./\\]+\.java',
            r'[\w\-./\\]+\.go',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, input_text)
            if match:
                path = match.group()
                if os.path.exists(path):
                    return path
        
        return None
    
    def _execute_code_review_workflow(self, code_path: str) -> str:
        """执行代码审查工作流"""
        # 创建工作流任务
        tasks = WorkflowTemplates.code_review_workflow(code_path)
        
        # 执行工作流
        results = self.coordinator.execute_workflow(tasks)
        
        # 整合结果
        return self._format_workflow_results(results, "代码审查报告")
    
    def _execute_security_audit(self, code_path: str) -> str:
        """执行安全审计"""
        task = TaskRequest(
            description=f"安全审计: {code_path}",
            task_type=AgentCapability.SECURITY_AUDIT,
            priority=TaskPriority.HIGH,
            context={'path': code_path}
        )
        
        response = self.coordinator.execute_task(task)
        
        if response.status.value == 'completed':
            result = response.result
            return self._format_security_result(result)
        else:
            return f"安全审计失败: {response.error}"
    
    def _execute_performance_analysis(self, code_path: str) -> str:
        """执行性能分析"""
        task = TaskRequest(
            description=f"性能分析: {code_path}",
            task_type=AgentCapability.PERFORMANCE_OPTIMIZATION,
            priority=TaskPriority.NORMAL,
            context={'path': code_path}
        )
        
        response = self.coordinator.execute_task(task)
        
        if response.status.value == 'completed':
            result = response.result
            return self._format_performance_result(result)
        else:
            return f"性能分析失败: {response.error}"
    
    def _execute_general_collaboration(self, input_text: str) -> str:
        """执行通用协作处理"""
        # 创建通用任务
        task = TaskRequest(
            description=input_text[:100],
            task_type=AgentCapability.GENERAL,
            context={'query': input_text}
        )
        
        # 尝试找到合适的智能体
        available_agents = self.coordinator.get_available_agents()
        
        if not available_agents:
            return super().run(input_text)
        
        # 使用标准处理
        return super().run(input_text)
    
    def _format_workflow_results(self, results: Dict, title: str) -> str:
        """格式化工作流结果"""
        lines = [f"# {title}\n"]
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for task_id, response in results.items():
            lines.append(f"## 任务: {task_id}")
            lines.append(f"状态: {response.status.value}")
            
            if response.status.value == 'completed':
                result = response.result
                if isinstance(result, dict):
                    # 格式化字典结果
                    if 'summary' in result:
                        summary = result['summary']
                        lines.append(f"质量评分: {summary.get('quality_score', 'N/A')}")
                        lines.append(f"问题数: {summary.get('total_issues', 0)}")
                    
                    if 'vulnerabilities' in result:
                        vulns = result['vulnerabilities']
                        lines.append(f"安全漏洞: {len(vulns)} 个")
                        lines.append(f"风险等级: {result.get('risk_level', 'unknown')}")
                    
                    if 'issues' in result:
                        issues = result['issues']
                        lines.append(f"性能问题: {len(issues)} 个")
                else:
                    lines.append(str(result)[:500])
            else:
                lines.append(f"错误: {response.error}")
            
            if response.suggestions:
                lines.append("\n建议:")
                for suggestion in response.suggestions[:5]:
                    lines.append(f"  - {suggestion}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_security_result(self, result: Dict) -> str:
        """格式化安全审计结果"""
        lines = ["# 安全审计报告\n"]
        
        summary = result.get('summary', {})
        lines.append(f"风险等级: {result.get('risk_level', 'unknown').upper()}")
        lines.append(f"总漏洞数: {summary.get('total_vulnerabilities', 0)}")
        lines.append(f"  - 严重: {summary.get('critical', 0)}")
        lines.append(f"  - 高危: {summary.get('high', 0)}")
        lines.append(f"  - 中危: {summary.get('medium', 0)}")
        lines.append(f"  - 低危: {summary.get('low', 0)}")
        
        vulnerabilities = result.get('vulnerabilities', [])
        if vulnerabilities:
            lines.append("\n## 漏洞详情")
            for vuln in vulnerabilities[:10]:
                lines.append(f"\n### [{vuln.get('severity', 'unknown')}] {vuln.get('category', '')}")
                lines.append(f"描述: {vuln.get('description', '')}")
                lines.append(f"位置: 行 {vuln.get('line', '?')}")
                lines.append(f"代码: `{vuln.get('code', '')[:80]}`")
        
        recommendations = result.get('recommendations', [])
        if recommendations:
            lines.append("\n## 修复建议")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
        
        return "\n".join(lines)
    
    def _format_performance_result(self, result: Dict) -> str:
        """格式化性能分析结果"""
        lines = ["# 性能分析报告\n"]
        
        summary = result.get('summary', {})
        lines.append(f"总问题数: {summary.get('total_issues', 0)}")
        lines.append(f"高影响: {summary.get('high_impact', 0)}")
        lines.append(f"中影响: {summary.get('medium_impact', 0)}")
        
        complexity = result.get('complexity_analysis', {})
        if complexity:
            lines.append(f"\n## 复杂度分析")
            lines.append(f"平均圈复杂度: {complexity.get('average_complexity', 0):.1f}")
            lines.append(f"最大圈复杂度: {complexity.get('max_complexity', 0)}")
        
        issues = result.get('issues', [])
        if issues:
            lines.append("\n## 性能问题")
            for issue in issues[:10]:
                lines.append(f"\n### [{issue.get('impact', 'medium')}] {issue.get('category', '')}")
                lines.append(f"描述: {issue.get('description', '')}")
                lines.append(f"位置: 行 {issue.get('line', '?')}")
        
        optimizations = result.get('optimizations', [])
        if optimizations:
            lines.append("\n## 优化建议")
            for i, opt in enumerate(optimizations, 1):
                lines.append(f"{i}. {opt}")
        
        return "\n".join(lines)
    
    def _is_important_response(self, response: str) -> bool:
        """判断响应是否重要"""
        # 简单启发式：长响应或包含代码/结果的响应更重要
        if len(response) > 500:
            return True
        if '```' in response:
            return True
        if any(kw in response for kw in ['结果', '分析', '建议', '报告', '完成']):
            return True
        return False
    
    def analyze_code(self, code_or_path: str, dimensions: Optional[List[str]] = None) -> Dict:
        """
        分析代码质量
        
        Args:
            code_or_path: 代码内容或文件路径
            dimensions: 分析维度列表
        
        Returns:
            分析结果字典
        """
        tool = AdvancedCodeAnalysisTool()
        
        if os.path.exists(code_or_path):
            with open(code_or_path, 'r', encoding='utf-8') as f:
                code = f.read()
            filepath = code_or_path
        else:
            code = code_or_path
            filepath = None
        
        return tool.analyze(code, filepath, dimensions)
    
    def get_session_stats(self) -> Dict:
        """获取会话统计信息"""
        stats = {
            'session_start': self.session_start_time.isoformat(),
            'interaction_count': self.interaction_count,
            'duration_minutes': (datetime.now() - self.session_start_time).total_seconds() / 60
        }
        
        if self.memory_system:
            stats['memory'] = self.memory_system.get_context_summary()
        
        if self.coordinator:
            stats['coordinator'] = self.coordinator.get_statistics()
        
        return stats
    
    def get_available_agents(self) -> List[Dict]:
        """获取可用的专门化智能体列表"""
        if self.coordinator:
            return self.coordinator.get_available_agents()
        return []
    
    def end_session(self, summary: Optional[str] = None):
        """结束会话"""
        if self.memory_system:
            self.memory_system.end_session(summary)
        
        if self.coordinator:
            self.coordinator.shutdown()


# 便捷函数
def create_enhanced_agent(
    enable_all: bool = True,
    **kwargs
) -> EnhancedUniversalAgent:
    """
    创建增强版智能体的便捷函数
    
    Args:
        enable_all: 是否启用所有增强功能
        **kwargs: 其他配置参数
    
    Returns:
        EnhancedUniversalAgent实例
    """
    if enable_all:
        return EnhancedUniversalAgent(
            enable_multi_agent=True,
            enable_memory=True,
            enable_code_analysis=True,
            **kwargs
        )
    else:
        return EnhancedUniversalAgent(**kwargs)


# 快速代码分析函数
def quick_analyze(code_or_path: str, dimensions: Optional[List[str]] = None) -> str:
    """
    快速代码分析
    
    Args:
        code_or_path: 代码内容或文件路径
        dimensions: 分析维度
    
    Returns:
        格式化的分析结果
    """
    tool = AdvancedCodeAnalysisTool()
    return tool.run({
        'path' if os.path.exists(code_or_path) else 'content': code_or_path,
        'dimensions': dimensions or ['security', 'performance', 'style', 'complexity', 'bug_risk'],
        'output_format': 'text'
    })
