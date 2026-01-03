from typing import Dict, List, Optional
import logging
from .base_agent import BaseAgent, AgentResult
from .tools.risk_tools import RiskTools

class RiskAssessmentAgent(BaseAgent):
    """
    风险评估Agent
    职责：基于条款分析结果和风险矩阵，识别并量化评估风险
    """
    
    async def execute(self, input_data: Dict, context: Dict) -> AgentResult:
        """
        执行风险评估
        
        Input:
            contract_markdown: 合同Markdown内容
            clause_analysis: 条款分析结果 (来自ClauseAnalysisAgent)
        
        Context:
            risk_matrix: 风险矩阵 (List[Dict] or DataFrame or str)
        """
        try:
            contract_md = input_data.get("contract_markdown", "")
            clause_analysis = input_data.get("clause_analysis", {})
            
            risk_matrix = context.get("risk_matrix", [])
            formatted_matrix = RiskTools.format_risk_matrix(risk_matrix)
            
            prompt = self._build_prompt(contract_md, clause_analysis, formatted_matrix)
            
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
            self.logger.error(f"Risk assessment failed: {e}")
            return AgentResult(self.name, "failed", None, error=str(e))

    def _build_prompt(self, contract_md: str, clause_analysis: Dict, risk_matrix: str) -> str:
        # 将clause_analysis转换为字符串以便插入Prompt
        import json
        clause_analysis_str = json.dumps(clause_analysis, ensure_ascii=False, indent=2)
        
        return f"""
【任务】
请基于合同内容、条款分析结果和风险矩阵，进行全面的风险评估。

【合同内容】
{contract_md}

【条款分析结果】
{clause_analysis_str}

【风险矩阵 (Risk Matrix)】
{risk_matrix}

【要求】
1. 识别合同中的商务风险、法律风险、技术风险和运营风险。
2. 参照【风险矩阵】中的定义，对每个风险进行量化评估（高/中/低）。
3. 重点关注条款分析中识别出的缺失项和问题。
4. 为每个识别出的风险提供具体的缓解措施或修改建议。

【输出格式】
请输出JSON格式，结构如下：
{{
  "risk_summary": {{
    "total_risks": 0,
    "high_risks": 0,
    "medium_risks": 0,
    "low_risks": 0,
    "overall_risk_level": "High/Medium/Low"
  }},
  "risks": [
    {{
      "id": "R001",
      "type": "商务/法律/技术/运营",
      "description": "风险描述",
      "level": "High/Medium/Low",
      "probability": "High/Medium/Low",
      "impact": "High/Medium/Low",
      "related_clause": "相关条款",
      "mitigation": "缓解措施/建议",
      "reference_matrix": "对应风险矩阵中的ID或项"
    }}
  ]
}}
"""
