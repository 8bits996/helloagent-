from typing import Dict, List, Optional
import logging
from .base_agent import BaseAgent, AgentResult
from .tools.clause_tools import ClauseTools

class ClauseAnalysisAgent(BaseAgent):
    """
    条款分析Agent
    职责：提取基本信息，识别关键条款，检查条款完整性
    """
    
    async def execute(self, input_data: Dict, context: Dict) -> AgentResult:
        """
        执行条款分析
        
        Input:
            contract_markdown: 合同Markdown内容
        
        Context:
            checklist: 评审清单 (List[Dict] or DataFrame or str)
        """
        try:
            contract_md = input_data.get("contract_markdown", "")
            if not contract_md:
                return AgentResult(self.name, "failed", None, error="Missing contract_markdown")

            checklist = context.get("checklist", [])
            formatted_checklist = ClauseTools.format_checklist(checklist)
            
            # 构建Prompt
            prompt = self._build_prompt(contract_md, formatted_checklist)
            
            # 调用LLM
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
            self.logger.error(f"Clause analysis failed: {e}")
            return AgentResult(self.name, "failed", None, error=str(e))

    def _build_prompt(self, contract_md: str, checklist: str) -> str:
        return f"""
【任务】
请分析以下合同条款，提取关键信息并对照Checklist进行完整性检查。

【合同内容】
{contract_md}

【评审清单 (Checklist)】
{checklist}

【要求】
1. 提取合同基本信息（甲方、乙方、金额、期限、标的物等）。
2. 识别关键条款（付款方式、交付标准、验收标准、知识产权、违约责任、争议解决等）。
3. 对照提供的【评审清单】，逐项检查条款是否完备。
4. 明确指出缺失的必要条款或存在明显异常的条款。

【输出格式】
请输出JSON格式，结构如下：
{{
  "basic_info": {{
    "party_a": "甲方名称",
    "party_b": "乙方名称",
    "amount": "合同金额",
    "duration": "期限",
    "subject": "标的物/服务内容"
  }},
  "key_clauses": {{
    "payment": {{ "summary": "...", "status": "present/missing/incomplete" }},
    "delivery": {{ "summary": "...", "status": "..." }},
    "acceptance": {{ "summary": "...", "status": "..." }},
    "ip_rights": {{ "summary": "...", "status": "..." }},
    "liability": {{ "summary": "...", "status": "..." }},
    "dispute": {{ "summary": "...", "status": "..." }}
  }},
  "checklist_analysis": [
    {{
      "item": "清单项名称",
      "status": "pass/fail/missing",
      "finding": "具体发现",
      "clause_reference": "引用条款内容或位置"
    }}
  ],
  "missing_items": [
    "缺失项1",
    "缺失项2"
  ],
  "issues": [
    {{ "severity": "high/medium/low", "description": "问题描述", "suggestion": "修改建议" }}
  ]
}}
"""
