"""
增强版UniversalAgent - Gradio Web界面
支持多智能体协作、智能记忆和高级代码分析
"""

import gradio as gr
import os
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

from src.agents.enhanced_universal_agent import EnhancedUniversalAgent, quick_analyze

# 全局Agent实例
agent = None


def initialize_agent():
    """初始化增强版Agent"""
    global agent
    if agent is None:
        agent = EnhancedUniversalAgent(
            enable_multi_agent=True,
            enable_memory=True,
            enable_code_analysis=True
        )
    return agent


def chat(message: str, history: list) -> str:
    """处理聊天消息"""
    agent = initialize_agent()
    
    try:
        response = agent.run(message)
        return response
    except Exception as e:
        return f"❌ 处理出错: {str(e)}"


def analyze_code_file(file, dimensions: list) -> str:
    """分析上传的代码文件"""
    if file is None:
        return "请上传代码文件"
    
    try:
        # 读取文件内容
        with open(file.name, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 执行分析
        result = quick_analyze(code, dimensions if dimensions else None)
        return result
    except Exception as e:
        return f"❌ 分析出错: {str(e)}"


def analyze_code_text(code: str, dimensions: list) -> str:
    """分析输入的代码文本"""
    if not code.strip():
        return "请输入代码内容"
    
    try:
        result = quick_analyze(code, dimensions if dimensions else None)
        return result
    except Exception as e:
        return f"❌ 分析出错: {str(e)}"


def get_session_stats() -> str:
    """获取会话统计"""
    agent = initialize_agent()
    
    try:
        stats = agent.get_session_stats()
        
        lines = ["## 📊 会话统计\n"]
        lines.append(f"- **会话开始**: {stats.get('session_start', 'N/A')}")
        lines.append(f"- **交互次数**: {stats.get('interaction_count', 0)}")
        lines.append(f"- **持续时间**: {stats.get('duration_minutes', 0):.1f} 分钟")
        
        if 'memory' in stats:
            memory = stats['memory']
            lines.append(f"\n### 记忆系统")
            lines.append(f"- 消息数: {memory.get('message_count', 0)}")
            lines.append(f"- 当前话题: {memory.get('current_topic', 'N/A')}")
            lines.append(f"- 短期记忆: {memory.get('short_term_memory_count', 0)} 条")
        
        if 'coordinator' in stats:
            coord = stats['coordinator']
            lines.append(f"\n### 多智能体协调器")
            lines.append(f"- 智能体数: {coord.get('total_agents', 0)}")
            lines.append(f"- 完成任务: {coord.get('completed_tasks', 0)}")
            lines.append(f"- 成功率: {coord.get('success_rate', 0)*100:.1f}%")
        
        return "\n".join(lines)
    except Exception as e:
        return f"❌ 获取统计出错: {str(e)}"


def get_available_agents() -> str:
    """获取可用智能体列表"""
    agent = initialize_agent()
    
    try:
        agents = agent.get_available_agents()
        
        if not agents:
            return "暂无可用智能体"
        
        lines = ["## 🤖 可用智能体\n"]
        for a in agents:
            status = "🟢 空闲" if not a['is_busy'] else "🔴 忙碌"
            lines.append(f"### {a['name']}")
            lines.append(f"- **ID**: {a['id']}")
            lines.append(f"- **状态**: {status}")
            lines.append(f"- **能力**: {', '.join(a['capabilities'])}")
            lines.append(f"- **成功率**: {a['success_rate']*100:.1f}%")
            lines.append("")
        
        return "\n".join(lines)
    except Exception as e:
        return f"❌ 获取智能体列表出错: {str(e)}"


# 创建Gradio界面
with gr.Blocks(title="增强版UniversalAgent") as demo:
    gr.Markdown("""
    # 🚀 增强版 UniversalAgent
    
    具备**多智能体协作**、**智能记忆**和**高级代码分析**能力的通用智能助手
    
    ---
    """)
    
    with gr.Tabs():
        # 聊天标签页
        with gr.TabItem("💬 智能对话"):
            chatbot = gr.ChatInterface(
                fn=chat,
                title="",
                description="与增强版智能助手对话，支持代码分析、多智能体协作等功能",
                examples=[
                    "帮我搜索Python最佳实践",
                    "查看当前目录的文件",
                    "分析一下这段代码的安全性",
                    "对这个项目进行全面的代码审查"
                ],
            )
        
        # 代码分析标签页
        with gr.TabItem("🔍 代码分析"):
            gr.Markdown("### 高级代码分析工具")
            gr.Markdown("支持安全、性能、风格、复杂度、Bug风险五维度分析")
            
            with gr.Row():
                with gr.Column():
                    code_input = gr.Code(
                        label="代码输入",
                        language="python",
                        lines=15
                    )
                    
                    dimension_select = gr.CheckboxGroup(
                        choices=["security", "performance", "style", "complexity", "bug_risk"],
                        value=["security", "performance", "style", "complexity", "bug_risk"],
                        label="分析维度"
                    )
                    
                    analyze_btn = gr.Button("🔍 分析代码", variant="primary")
                
                with gr.Column():
                    analysis_output = gr.Textbox(
                        label="分析结果",
                        lines=20,
                        max_lines=30
                    )
            
            analyze_btn.click(
                fn=analyze_code_text,
                inputs=[code_input, dimension_select],
                outputs=analysis_output
            )
            
            gr.Markdown("---")
            gr.Markdown("### 文件分析")
            
            with gr.Row():
                file_input = gr.File(label="上传代码文件", file_types=[".py", ".js", ".ts", ".java", ".go"])
                file_dimension_select = gr.CheckboxGroup(
                    choices=["security", "performance", "style", "complexity", "bug_risk"],
                    value=["security", "performance", "complexity"],
                    label="分析维度"
                )
            
            file_analyze_btn = gr.Button("📁 分析文件", variant="secondary")
            file_analysis_output = gr.Textbox(label="文件分析结果", lines=15)
            
            file_analyze_btn.click(
                fn=analyze_code_file,
                inputs=[file_input, file_dimension_select],
                outputs=file_analysis_output
            )
        
        # 系统状态标签页
        with gr.TabItem("📊 系统状态"):
            gr.Markdown("### 系统状态监控")
            
            with gr.Row():
                with gr.Column():
                    stats_output = gr.Markdown("点击刷新获取会话统计")
                    refresh_stats_btn = gr.Button("🔄 刷新统计", variant="primary")
                    
                    refresh_stats_btn.click(
                        fn=get_session_stats,
                        outputs=stats_output
                    )
                
                with gr.Column():
                    agents_output = gr.Markdown("点击刷新获取智能体列表")
                    refresh_agents_btn = gr.Button("🔄 刷新智能体", variant="secondary")
                    
                    refresh_agents_btn.click(
                        fn=get_available_agents,
                        outputs=agents_output
                    )
        
        # 帮助标签页
        with gr.TabItem("❓ 帮助"):
            gr.Markdown("""
            ## 使用指南
            
            ### 💬 智能对话
            - 支持自然语言对话
            - 可以执行网页搜索、终端命令、文件操作
            - 支持代码分析和多智能体协作
            
            ### 🔍 代码分析
            - **安全分析**: 检测SQL注入、命令注入、硬编码密钥等安全漏洞
            - **性能分析**: 识别低效循环、重复计算等性能问题
            - **风格检查**: 检查代码风格和规范
            - **复杂度分析**: 计算圈复杂度、函数长度等
            - **Bug风险**: 检测潜在的Bug模式
            
            ### 🤖 多智能体协作
            当检测到复杂任务时，系统会自动调用多个专门化智能体协作处理：
            - **代码分析专家**: 深度代码质量分析
            - **安全审计专家**: 安全漏洞扫描
            - **性能优化专家**: 性能问题检测
            - **文档生成专家**: 自动生成文档
            - **测试专家**: 测试用例生成
            
            ### 🧠 智能记忆
            - 自动记住重要的对话内容
            - 根据历史对话提供更精准的回答
            - 支持跨会话的知识积累
            
            ---
            
            ## 示例命令
            
            ```
            # 基础功能
            帮我搜索Python最佳实践
            查看当前目录的文件
            创建一个hello.py文件
            
            # 代码分析
            分析这段代码的安全性
            检查这个函数的复杂度
            
            # 多智能体协作
            对这个项目进行全面的代码审查
            帮我做一个安全审计
            分析这个文件的性能问题
            ```
            """)
    
    gr.Markdown("""
    ---
    **增强版 UniversalAgent v2.0** | 
    支持多智能体协作 | 智能记忆系统 | 高级代码分析
    """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft()
    )
