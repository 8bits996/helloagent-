"""
CodeBuddy Headless HTTP API 客户端
基于官方HTTP API规范实现
"""

import httpx
import json
import logging
from typing import Dict, Optional, List
import re
import pandas as pd

logger = logging.getLogger(__name__)


class CodeBuddyClient:
    """
    CodeBuddy Headless HTTP API 客户端
    
    API文档: 基于CodeBuddy HTTP API规范
    核心端点: POST /agent
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:3000"):
        """
        初始化客户端
        
        Args:
            base_url: CodeBuddy HTTP服务地址
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=600.0)  # 10分钟超时
        logger.info(f"CodeBuddy客户端初始化: {base_url}")
    
    async def health_check(self) -> bool:
        """
        健康检查 - 验证CodeBuddy服务是否可用
        
        Returns:
            True if service is available
        """
        try:
            # 尝试简单的Agent调用
            response = await self.client.post(
                f"{self.base_url}/agent",
                json={
                    "prompt": "hello",
                    "outputFormat": "text"
                },
                timeout=30.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"CodeBuddy服务不可用: {e}")
            return False
    
    async def review_contract(
        self,
        contract_markdown: str,
        knowledge_base_files: List[str],
        session_id: Optional[str] = None
    ) -> Dict:
        """
        执行合同评审（主接口）
        
        Args:
            contract_markdown: 合同Markdown文本
            knowledge_base_files: 知识库文件路径列表
            session_id: 会话ID（可选，用于多轮对话）
            
        Returns:
            {
                "success": True/False,
                "review_result": {...},  # 评审结果JSON
                "usage": {...},          # Token使用统计
                "model": "...",          # 使用的模型
                "error": "..."           # 错误信息（如果失败）
            }
        """
        try:
            # 1. 构建评审Prompt
            prompt = self._build_review_prompt(
                contract_markdown,
                knowledge_base_files
            )
            
            logger.info("开始调用CodeBuddy Agent进行合同评审...")
            
            # 2. 调用CodeBuddy Agent API
            result = await self._call_agent(
                prompt=prompt,
                session_id=session_id,
                output_format="json"
            )
            
            return {
                "success": True,
                "review_result": result["parsed_output"],
                "usage": result["usage"],
                "model": result["model"],
                "error": None
            }
        
        except Exception as e:
            logger.error(f"合同评审失败: {str(e)}")
            return {
                "success": False,
                "review_result": {},
                "usage": {},
                "model": "",
                "error": str(e)
            }
    
    def _build_review_prompt(
        self,
        contract_md: str,
        kb_files: List[str]
    ) -> str:
        """
        构建评审Prompt
        
        整合:
        1. 合同内容 (Markdown格式)
        2. 知识库引用 (CSV文件内容)
        3. 评审要求 (基于ContractCopilot SOP)
        """
        # 加载知识库内容
        kb_content = self._load_knowledge_bases(kb_files)
        
        prompt = f"""你是一位资深的合同评审专家，拥有超过10年的合同审查经验。

# 评审任务

请对以下合同进行全面、系统化的评审。

## 合同内容

{contract_md}

## 知识库

我已为你准备好以下知识库，请在评审过程中参考使用：

### 1. 主合同评审Checklist

{kb_content.get('checklist', '知识库未加载')}

### 2. 风险矩阵

{kb_content.get('risk_matrix', '知识库未加载')}

### 3. SOP流程

{kb_content.get('sop', '知识库未加载')}

## 评审要求

请严格按照以下步骤进行评审：

### 第1步：条款完整性检查
- 对照《主合同评审checklist》逐项检查
- 标注每个条款的状态：✅通过 / ⚠️异常 / ❌缺失
- 记录异常和缺失的具体说明

### 第2步：风险量化评估
- 使用《风险矩阵》对识别的风险进行量化
- 风险等级：🔴高风险 / 🟡中风险 / 🟢低风险
- 分类：技术风险、商务风险、法律风险、运营风险
- 对每个风险提供应对建议

### 第3步：合规性检查
- 按照《SOP流程》验证流程符合性
- 检查公司政策合规性
- 检查法律法规合规性
- 列出所有合规问题

### 第4步：生成评审决策
- 综合评估结果，给出最终决策建议
- 决策选项：建议签署 / 谨慎签署 / 不建议签署
- 提供决策依据和关键发现

## 输出格式

**关键要求**: 请严格按照以下JSON格式输出结果，不要添加额外的解释文字。

```json
{{
  "summary": {{
    "decision": "建议签署",
    "confidence": 0.85,
    "key_findings": [
      "关键发现1",
      "关键发现2",
      "关键发现3"
    ],
    "overall_risk": "中",
    "review_time": "2025-12-28"
  }},
  "checklist_results": [
    {{
      "category_1": "一级分类",
      "category_2": "二级分类",
      "category_3": "三级分类",
      "review_item": "评审项",
      "status": "通过",
      "finding": "具体发现",
      "comment": "详细说明"
    }}
  ],
  "risk_assessment": [
    {{
      "risk_type": "商务",
      "risk_description": "风险描述",
      "risk_level": "中",
      "probability": "中",
      "impact": "影响说明",
      "mitigation": "应对建议"
    }}
  ],
  "compliance_check": {{
    "company_policy_compliant": true,
    "legal_compliant": true,
    "sop_compliant": true,
    "issues": []
  }},
  "recommendations": [
    "建议1",
    "建议2"
  ]
}}
```

请开始评审并输出JSON结果。
"""
        return prompt
    
    def _load_knowledge_bases(self, kb_files: List[str]) -> Dict[str, str]:
        """
        加载知识库文件内容
        
        从ContractCopilot的CSV文件中读取并转为Markdown格式
        """
        kb_content = {}
        
        for file_path in kb_files:
            try:
                # 识别知识库类型
                file_name = str(file_path).lower()
                
                if "checklist" in file_name or "评审" in file_name:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    kb_content['checklist'] = df.head(20).to_markdown(index=False)
                    logger.info(f"加载Checklist知识库: {file_path}")
                
                elif "风险" in file_name or "risk" in file_name:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    kb_content['risk_matrix'] = df.head(20).to_markdown(index=False)
                    logger.info(f"加载风险矩阵: {file_path}")
                
                elif "sop" in file_name or "流程" in file_name:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    kb_content['sop'] = df.head(20).to_markdown(index=False)
                    logger.info(f"加载SOP流程: {file_path}")
            
            except Exception as e:
                logger.warning(f"加载知识库失败: {file_path}, 错误: {e}")
                continue
        
        return kb_content
    
    async def _call_agent(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        output_format: str = "json"
    ) -> Dict:
        """
        调用CodeBuddy Agent API
        
        API规范:
        POST /agent
        Content-Type: application/json
        
        Request Body:
        {
          "prompt": "...",
          "outputFormat": "json",
          "model": "claude-3-5-sonnet-20241022",
          "sessionId": "optional_session_id",
          "dangerouslySkipPermissions": true
        }
        
        Response (outputFormat: "json"):
        {
          "output": "生成的内容",
          "usage": {
            "inputTokens": 100,
            "outputTokens": 200,
            "totalTokens": 300
          },
          "model": "claude-3-5-sonnet"
        }
        """
        request_body = {
            "prompt": prompt,
            "outputFormat": output_format,
            "model": "claude-3-5-sonnet-20241022",
            "dangerouslySkipPermissions": True
        }
        
        if session_id:
            request_body["sessionId"] = session_id
        
        logger.info(f"调用CodeBuddy Agent API: {self.base_url}/agent")
        logger.info(f"Prompt长度: {len(prompt)} 字符")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/agent",
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Agent调用成功")
            logger.info(f"Token使用: {result.get('usage', {})}")
            
            # 解析JSON输出
            parsed_output = self._parse_json_output(result["output"])
            
            return {
                "parsed_output": parsed_output,
                "raw_output": result["output"],
                "usage": result.get("usage", {}),
                "model": result.get("model", "")
            }
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP错误: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f", 详情: {error_detail}"
            except:
                error_msg += f", 响应: {e.response.text[:200]}"
            
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            logger.error(f"Agent调用失败: {str(e)}")
            raise
    
    def _parse_json_output(self, output: str) -> Dict:
        """
        解析Agent输出的JSON
        
        可能的格式:
        1. 纯JSON字符串
        2. Markdown代码块包裹的JSON: ```json\n{...}\n```
        3. 混合文本和JSON
        """
        # 尝试直接解析
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取Markdown代码块中的JSON
        json_match = re.search(r'```json\s*\n(.*?)\n```', output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试提取任何大括号包裹的JSON
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        logger.error(f"无法解析Agent输出为JSON，输出前200字符: {output[:200]}")
        raise ValueError(f"无法解析Agent输出为JSON")
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
        logger.info("CodeBuddy客户端已关闭")


# ========== 使用示例 ==========
async def example_usage():
    """使用示例"""
    import asyncio
    
    client = CodeBuddyClient()
    
    # 健康检查
    if not await client.health_check():
        print("CodeBuddy服务不可用，请先启动: codebuddy --serve --port 3000")
        return
    
    # 读取合同Markdown
    contract_md = """
    # 软件开发合同
    
    甲方：某科技公司
    乙方：某软件开发公司
    
    ## 第一条 项目内容
    乙方为甲方开发一套合同管理系统...
    
    ## 第二条 合同金额
    合同总金额为人民币50万元...
    """
    
    # 知识库文件
    kb_files = [
        "知识库/主合同评审checklist.csv",
        "知识库/风险矩阵.csv",
        "知识库/可交付评审SOP流程说明.csv"
    ]
    
    # 执行评审
    result = await client.review_contract(
        contract_markdown=contract_md,
        knowledge_base_files=kb_files
    )
    
    if result["success"]:
        print("评审成功！")
        print(json.dumps(result["review_result"], indent=2, ensure_ascii=False))
    else:
        print(f"评审失败: {result['error']}")
    
    await client.close()


if __name__ == "__main__":
    import asyncio
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行示例
    asyncio.run(example_usage())
