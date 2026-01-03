from typing import Dict, List, Optional
import logging
import json
from .base_agent import BaseAgent, AgentResult
from .tools.compliance_tools import ComplianceTools

class ComplianceCheckAgent(BaseAgent):
    """
    合规检查Agent
    职责：检查合同是否符合公司SOP流程、法律法规和内部政策
    """
    
    async def execute(self, input_data: Dict, context: Dict) -> AgentResult:
        """
        执行合规检查
        
        Input:
            contract_markdown: 合同Markdown内容
            clause_analysis: 条款分析结果
        
        Context:
            sop: SOP流程说明
        """
        try:
            contract_md = input_data.get("contract_markdown", "")
            clause_analysis = input_data.get("clause_analysis", {})
            
            sop = context.get("sop", [])
            formatted_sop = ComplianceTools.format_sop(sop)
            
            prompt = self._build_prompt(contract_md, clause_analysis, formatted_sop)
            
            result = await self.llm.generate(
                prompt=prompt,
                system_prompt=self.config.system_prompt,
                output_format="json"
            )
            
            return AgentResult(
                agent_name=self.name,
                status="completed",
                output=result["content"],
                metadata={"usage": result["usage"], "model": result["model"]}
            )
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {e}")
            return AgentResult(self.name, "failed", None, error=str(e))

    def _build_prompt(self, contract_md: str, clause_analysis: Dict, sop: str) -> str:
        clause_analysis_str = json.dumps(clause_analysis, ensure_ascii=False, indent=2)
        
        return f"""
【任务】
请检查合同是否符合公司SOP流程、法律法规和内部政策。

【合同内容】
{contract_md}

【条款分析结果】
{clause_analysis_str}

【SOP流程说明】
{sop}

【要求】
1. 检查合同签署流程、审批节点等是否符合SOP要求。
2. 检查合同内容是否符合相关法律法规（如民法典）。
3. 检查是否违反公司内部合规政策（如反腐败、数据合规等）。
4. 明确列出合规/不合规项。

【输出格式】
请输出JSON格式，结构如下：
{{
  "compliance_score": 0-100,
  "summary": "合规性总结",
  "sop_check": [
    {{ "item": "SOP项", "status": "pass/fail/not_applicable", "comment": "说明" }}
  ],
  "legal_check": [
    {{ "item": "法律合规项", "status": "pass/fail", "issue": "问题", "recommendation": "建议" }}
  ],
  "policy_check": [
    {{ "item": "公司政策项", "status": "pass/fail", "issue": "问题" }}
  ]
}}
"""
