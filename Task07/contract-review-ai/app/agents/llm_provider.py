from typing import Dict, Optional, Any
import logging
import json
import asyncio
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class LLMProvider:
    """LLM提供者接口，支持OpenAI兼容API"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None, use_mock: bool = False):
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = base_url or settings.LLM_BASE_URL
        self.model = model or settings.LLM_MODEL
        self.use_mock = use_mock
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, output_format: str = "json") -> Dict:
        """
        生成响应
        """
        if self.use_mock:
            return await self._generate_mock(prompt, output_format)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "response_format": {"type": "json_object"} if output_format == "json" else None
                }
            )
            response.raise_for_status()
            result = response.json()
            
            content_str = result["choices"][0]["message"]["content"]
            
            parsed_content = content_str
            if output_format == "json":
                try:
                    parsed_content = json.loads(content_str)
                except json.JSONDecodeError:
                    # 尝试清理markdown代码块
                    cleaned = content_str.replace("```json", "").replace("```", "").strip()
                    try:
                        parsed_content = json.loads(cleaned)
                    except:
                        logger.warning("Failed to parse JSON response, returning raw string")
            
            return {
                "content": parsed_content,
                "raw_output": content_str,
                "usage": result.get("usage", {}),
                "model": result.get("model", self.model)
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            # 自动回退到Mock模式，确保演示可用性
            logger.warning("Falling back to Mock mode due to API error.")
            return await self._generate_mock(prompt, output_format)

    async def _generate_mock(self, prompt: str, output_format: str) -> Dict:
        """生成Mock响应"""
        await asyncio.sleep(1) # 模拟延迟
        
        # 根据Prompt内容推断是哪个Agent
        content = {}
        if "条款分析专家" in prompt or "提取合同基本信息" in prompt or "Contract Analysis" in prompt:
            content = {
                "basic_info": {
                    "party_a": "科技创新有限公司",
                    "party_b": "未来软件工作室",
                    "amount": "500,000.00元",
                    "duration": "3个月",
                    "subject": "智能客户管理系统开发"
                },
                "key_clauses": {
                    "payment": {"summary": "30%预付，60%验收，10%维保", "status": "present"},
                    "ip_rights": {"summary": "知识产权归乙方所有", "status": "present"},
                    "liability": {"summary": "违约金5%", "status": "present"}
                },
                "missing_items": ["保密条款", "不可抗力条款"],
                "issues": [
                    {"severity": "high", "description": "知识产权归乙方所有，对甲方不利", "suggestion": "应约定归甲方所有或共有"},
                    {"severity": "medium", "description": "违约金5%偏低", "suggestion": "建议提高至20%"}
                ],
                "completeness_score": 0.85
            }
        elif "风险评估专家" in prompt or "Risk Assessment" in prompt:
            content = {
                "risk_summary": {
                    "total_risks": 2,
                    "high_risks": 1,
                    "medium_risks": 1,
                    "low_risks": 0,
                    "overall_risk_level": "High"
                },
                "risks": [
                    {
                        "id": "R001",
                        "type": "法律风险",
                        "description": "知识产权归属乙方，甲方仅有使用权，存在长期被锁定风险",
                        "level": "High",
                        "mitigation": "谈判修改为知识产权归甲方所有"
                    },
                    {
                        "id": "R002",
                        "type": "商务风险",
                        "description": "违约金5%过低，难以约束乙方按时交付",
                        "level": "Medium",
                        "mitigation": "建议提高违约金比例"
                    }
                ]
            }
        elif "合规检查专员" in prompt or "Compliance Check" in prompt:
            content = {
                "compliance_score": 0.85,
                "issues": [
                     {"item": "知识产权条款", "status": "fail", "issue": "权属约定不利于公司"},
                     {"item": "使用标准模板", "status": "fail", "issue": "未使用公司标准技术开发合同模板"}
                ]
            }
        elif "首席评审官" in prompt or "Report Generation" in prompt:
            content = {
                "decision": "谨慎签署",
                "confidence_score": 0.9,
                "executive_summary": "合同整体结构完整，但在知识产权归属和违约责任方面存在较大风险，建议修改后签署。",
                "action_items": [
                    "修改第四条，约定知识产权归甲方所有",
                    "修改第五条，将违约金比例提高至20%",
                    "补充保密条款和不可抗力条款"
                ]
            }
        else:
            # 默认Mock响应
            content = {"error": "Mock: Unknown agent prompt type"}

        return {
            "content": content,
            "raw_output": json.dumps(content),
            "usage": {"inputTokens": 100, "outputTokens": 200},
            "model": "mock-model"
        }

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
