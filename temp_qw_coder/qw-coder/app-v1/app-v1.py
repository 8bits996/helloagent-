#!/usr/bin/env python3
"""企业微信回调服务 - V1 版本（纯企微）
支持企微消息接收、解密和回复
"""
import base64
import json
import os
import socket
import struct
from datetime import datetime
from typing import Tuple

import defusedxml.ElementTree as ET
import httpx
from Crypto.Cipher import AES
from fastapi import FastAPI, Query, Request, Response, BackgroundTasks


# ========== 配置部分 ==========
class ConfigV1:
    """V1 配置"""

    # 企业微信配置
    QYWX_TOKEN: str = os.getenv("QYWX_TOKEN", "")
    QYWX_ENCODING_AES_KEY: str = os.getenv("QYWX_ENCODING_AES_KEY", "")

    # 服务配置
    PORT: int = int(os.getenv("PORT", "8088"))

    # 日志配置
    LOG_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app-v1.log")

    # 白名单配置
    ALLOWED_USERS: list = os.getenv("QYWX_RECEIVE_ID", "rtxid").split(",")

    @classmethod
    def validate(cls) -> Tuple[bool, str]:
        """验证配置是否完整"""
        missing = []
        if not cls.QYWX_TOKEN:
            missing.append("QYWX_TOKEN")
        if not cls.QYWX_ENCODING_AES_KEY:
            missing.append("QYWX_ENCODING_AES_KEY")

        if missing:
            return False, f"缺少必需的环境变量: {', '.join(missing)}"
        return True, "配置验证通过"

    @classmethod
    def get_summary(cls) -> str:
        """获取配置摘要"""
        return f"""
企业微信回调服务 V1 配置:
- 服务端口: {cls.PORT}
- 白名单用户: {', '.join(cls.ALLOWED_USERS)}
- 日志文件: {cls.LOG_FILE}
        """.strip()


config = ConfigV1()
app = FastAPI(title="企业微信回调服务-V1", version="1.0.0")

# 初始化企微密钥
TOKEN = config.QYWX_TOKEN
KEY = base64.b64decode(config.QYWX_ENCODING_AES_KEY + "=")


# ========== 工具函数 ==========
def log_message(msg_type: str, content: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{msg_type}]\n{content}\n{'-'*80}\n")


def decrypt(encrypted: str) -> str:
    """解密企微消息"""
    try:
        data = base64.b64decode(encrypted)
        cipher = AES.new(KEY, AES.MODE_CBC, KEY[:16])
        decrypted = cipher.decrypt(data)[:-cipher.decrypt(data)[-1]]
        content = decrypted[16:]
        msg_len = socket.ntohl(struct.unpack("I", content[:4])[0])
        result = content[4:4+msg_len].decode()
        log_message("解密消息", result)
        return result
    except Exception as e:
        log_message("解密失败", str(e))
        raise


# ========== 企微回复 ==========
async def send_qywx_message(webhook_url: str, content: str):
    """发送企微消息"""
    try:
        send_data = {
            "msgtype": "text",
            "text": {"content": content}
        }

        log_message("发送消息", f"webhook: {webhook_url}\n内容: {content}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(webhook_url, json=send_data)

            if response.status_code == 200:
                log_message("发送成功", f"状态码: {response.status_code}")
            else:
                log_message("发送失败", f"状态码: {response.status_code}\n响应: {response.text}")

    except Exception as e:
        log_message("发送异常", str(e))


async def handle_message(content: str, from_name: str, webhook_url: str):
    """处理消息并回复（简单回显）"""
    try:
        log_message("处理消息", f"用户: {from_name}\n内容: {content}")

        # 发送处理中的提示
        await send_qywx_message(webhook_url, f"✅ 已收到消息\n来自: {from_name}")

        # 简单回显消息（实际使用时可以接入你自己的业务逻辑）
        reply_message = f"【回显消息】\n\n您说: {content}\n\n💡 提示: 这是企微回调服务的测试回复"
        await send_qywx_message(webhook_url, reply_message)

    except Exception as e:
        log_message("处理异常", str(e))
        await send_qywx_message(webhook_url, f"❌ 处理失败: {str(e)}")


# ========== 企微回调接口 ==========
@app.api_route("/qyapi", methods=["GET", "POST"])
async def qyapi_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    msg_signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...),
    echostr: str = Query(None),
):
    """企业微信回调接口"""

    # GET 请求：验证URL
    if request.method == "GET":
        log_message("验证请求", f"echostr: {echostr}")
        try:
            decrypted = decrypt(echostr)
            return Response(decrypted)
        except Exception as e:
            log_message("验证失败", str(e))
            return Response("验证失败", status_code=500)

    # POST 请求：处理消息
    try:
        body = await request.body()
        log_message("接收消息", f"原始body长度: {len(body)}")

        # 解密消息
        xml_msg = decrypt(ET.fromstring(body.decode()).find("Encrypt").text)
        msg_root = ET.fromstring(xml_msg)

        # 只处理文本消息
        if msg_root.find("MsgType").text == "text":
            from_name = msg_root.find("From/Name").text
            from_alias = msg_root.find("From/Alias").text
            webhook_url = msg_root.find("WebhookUrl").text
            content = msg_root.find("Text/Content").text

            log_message(
                "解析消息",
                f"发送人: {from_name}\nAlias: {from_alias}\n内容: {content}"
            )

            # 白名单验证
            if from_alias not in config.ALLOWED_USERS:
                log_message("权限验证失败", f"用户 {from_alias} 不在白名单中")
                await send_qywx_message(webhook_url, "❌ 权限不足，您不在白名单中")
                return Response("success")

            # 后台异步处理消息
            background_tasks.add_task(handle_message, content, from_name, webhook_url)
        else:
            log_message("忽略消息", f"消息类型: {msg_root.find('MsgType').text}")

    except Exception as e:
        log_message("回调异常", str(e))

    return Response("success")


# ========== 健康检查 ==========
@app.get("/health")
async def health_check():
    """健康检查接口"""
    valid, msg = config.validate()
    return {
        "status": "ok" if valid else "error",
        "message": msg,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "企业微信回调服务",
        "version": "1.0.0",
        "description": "支持企微消息接收、解密和回复"
    }


# ========== 启动服务 ==========
if __name__ == "__main__":
    import sys

    # 验证配置
    valid, msg = config.validate()
    if not valid:
        print(f"❌ 配置错误: {msg}")
        print("\n请设置以下环境变量:")
        print("  - QYWX_TOKEN")
        print("  - QYWX_ENCODING_AES_KEY")
        sys.exit(1)

    print("=" * 60)
    print(config.get_summary())
    print("=" * 60)
    print(f"\n✅ 配置验证: {msg}")
    print("\n提示: 请使用 uvicorn 启动服务")
    print(f"  python3 -m uvicorn app-v1:app --host 0.0.0.0 --port {config.PORT}")
    print("  或使用启动脚本: ./start-v1.sh")

