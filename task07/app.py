
import gradio as gr
from src.agents.agent_universal import UniversalAgent
from dotenv import load_dotenv
import os

# 加载配置
load_dotenv()

# 初始化 Agent (如果 API Key 未设置，这里会报错，但我们可以在界面上提示)
try:
    agent = UniversalAgent()
    agent_status = "✅ Agent 初始化成功"
except Exception as e:
    agent = None
    agent_status = f"⚠️ Agent 初始化失败: {str(e)}\n请检查 .env 配置或在下方设置 API Key。"

def chat_response(message, history):
    if not agent:
        return "❌ Agent 未运行，请先配置 API Key。"
    
    try:
        # 在这里调用 Agent
        response = agent.run(message)
        return response
    except Exception as e:
        return f"❌ 处理出错: {str(e)}"

def update_api_key(api_key):
    global agent
    if not api_key:
        return "⚠️ API Key 不能为空"
    
    os.environ["LLM_API_KEY"] = api_key
    try:
        # 重新初始化 Agent
        agent = UniversalAgent()
        return "✅ API Key 更新成功，Agent 已重启！"
    except Exception as e:
        return f"❌ Agent 重启失败: {str(e)}"

# 构建界面
with gr.Blocks(title="Universal Agent") as demo:
    gr.Markdown("# 🤖 Universal Agent Web UI")
    
    with gr.Row():
        status_box = gr.Textbox(value=agent_status, label="系统状态", interactive=False)
        api_key_input = gr.Textbox(label="设置 ModelScope API Key (临时)", type="password", placeholder="如果没有在 .env 中设置...")
        update_btn = gr.Button("更新 Key")
    
    update_btn.click(update_api_key, inputs=[api_key_input], outputs=[status_box])
    
    chatbot = gr.ChatInterface(
        fn=chat_response,
        examples=["搜索 Python 教程", "pwd", "ls -la", "创建一个 hello.txt 文件，内容是 Hello World"],
        title="智能助手对话",
        description="支持搜索、终端命令和文件操作。",
    )

if __name__ == "__main__":
    demo.launch(share=False)
