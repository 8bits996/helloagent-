#!/usr/bin/env python3
"""测试 CodeBuddy 集成"""
import asyncio
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ['CODEBUDDY_PATH'] = '/root/.npm/node_modules/bin/claude-internal'
os.environ['WORKING_DIR'] = '/root/workspace/qw-coder'

async def test_codebuddy():
    """测试 CodeBuddy 调用"""
    # 导入模块
    from importlib import import_module
    app_module = import_module('app-v2')
    
    print("=" * 60)
    print("测试 CodeBuddy 集成")
    print("=" * 60)
    print("")
    
    # 测试用例
    test_cases = [
        "Hello, CodeBuddy!",
        "什么是 Python?",
    ]
    
    for i, prompt in enumerate(test_cases, 1):
        print(f"【测试 {i}】")
        print(f"提示词: {prompt}")
        print("-" * 60)
        
        success, result = await app_module.call_codebuddy(prompt)
        
        if success:
            print(f"✅ 成功")
            print(f"结果长度: {len(result)} 字符")
            print(f"前 200 字符: {result[:200]}...")
        else:
            print(f"❌ 失败")
            print(f"错误: {result}")
        
        print("")
        print("=" * 60)
        print("")

if __name__ == "__main__":
    asyncio.run(test_codebuddy())
