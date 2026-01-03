from typing import Dict, List, Optional
import logging
import json
from datetime import datetime
from .base_agent import BaseAgent, AgentResult
from .tools.report_tools import ReportTools

class ReportGenerationAgent(BaseAgent):
    """
    报告生成Agent
    职责：整合各Agent的分析结果，生成最终的评审报告和决策建议
    """
    
    async def execute(self, input_data: Dict, context: Dict) -> AgentResult:
        """
        执行报告生成
        
        Input:
            agent_outputs: 包含 clause, risk, compliance 的输出 (Dict[str, AgentResult])
        
        """
        try:
            agent_outputs = input_data.get("agent_outputs", {})
            
            # Helper to safely get output from AgentResult or dict
            def get_output(key):
                obj = agent_outputs.get(key)
                if isinstance(obj, AgentResult):
                    return obj.output
                elif isinstance(obj, dict):
                    return obj.get("output", obj)
                return {}

            clause_result = get_output("clause")
            risk_result = get_output("risk")
            compliance_result = get_output("compliance")
            
            # 构建Prompt
            prompt = self._build_prompt(clause_result, risk_result, compliance_result)
            
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
            self.logger.error(f"Report generation failed: {e}")
            return AgentResult(self.name, "failed", None, error=str(e))

    def _build_prompt(self, clause: Dict, risk: Dict, compliance: Dict) -> str:
        data = {
            "clause_analysis": clause,
            "risk_assessment": risk,
            "compliance_check": compliance
        }
        data_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        return f"""
【任务】
作为首席评审官，请综合各项分析结果，生成一份最终的合同评审决策报告。

【分析数据】
{data_str}

【要求】
1. 给出明确的决策建议（建议签署 / 谨慎签署 / 不建议签署）。
2. 提炼核心风险点（Top 3）。
3. 总结条款完备性和合规性情况。
4. 给出最终的修改建议清单。

【输出格式】
请输出JSON格式，结构如下：
{{
  "decision": "建议签署/谨慎签署/不建议签署",
  "confidence_score": 0.0-1.0,
  "executive_summary": "总体评价摘要",
  "top_risks": [
    {{ "title": "风险标题", "description": "描述", "severity": "High" }}
  ],
  "key_issues": [
    "关键问题1", "关键问题2"
  ],
  "action_items": [
    "修改建议1", "修改建议2"
  ],
  "review_timestamp": "{datetime.now().isoformat()}"
}}
"""
