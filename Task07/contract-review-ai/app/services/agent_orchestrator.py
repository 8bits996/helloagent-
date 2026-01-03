import logging
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from app.agents.base_agent import AgentConfig, AgentResult
from app.agents.llm_provider import LLMProvider
from app.agents.clause_analysis_agent import ClauseAnalysisAgent
from app.agents.risk_assessment_agent import RiskAssessmentAgent
from app.agents.compliance_check_agent import ComplianceCheckAgent
from app.agents.report_generation_agent import ReportGenerationAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Agent编排器"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.agents = {}
        self._load_agents()
    
    def _load_agents(self):
        """加载并实例化所有Agent"""
        try:
            self._load_agents_from_config()
        except Exception as e:
            logger.warning(f"从配置文件加载Agent失败: {e}，回退到硬编码配置")
            self._load_agents_hardcoded()

    def _load_agents_from_config(self):
        """从JSON配置文件加载Agent"""
        # 获取配置文件的绝对路径
        current_dir = Path(__file__).parent.resolve()
        project_root = current_dir.parent.parent
        config_dir = project_root / "app" / "config" / "agents"
        
        # 1. Clause Analysis
        with open(config_dir / "clause_analysis.json", "r", encoding="utf-8") as f:
            clause_config = AgentConfig(**json.load(f))
        self.agents["clause"] = ClauseAnalysisAgent(clause_config, self.llm)
        
        # 2. Risk Assessment
        with open(config_dir / "risk_assessment.json", "r", encoding="utf-8") as f:
            risk_config = AgentConfig(**json.load(f))
        self.agents["risk"] = RiskAssessmentAgent(risk_config, self.llm)
        
        # 3. Compliance Check
        with open(config_dir / "compliance_check.json", "r", encoding="utf-8") as f:
            comp_config = AgentConfig(**json.load(f))
        self.agents["compliance"] = ComplianceCheckAgent(comp_config, self.llm)
        
        # 4. Report Generation
        with open(config_dir / "report_generation.json", "r", encoding="utf-8") as f:
            report_config = AgentConfig(**json.load(f))
        self.agents["report"] = ReportGenerationAgent(report_config, self.llm)
        
        logger.info("所有Agent从配置文件加载完成")

    def _load_agents_hardcoded(self):
        """硬编码加载Agent（回退方案）"""
        # 1. 条款分析Agent
        clause_config = AgentConfig(
            name="clause_analysis",
            display_name="条款分析专家",
            role="分析合同条款，提取关键信息，检查完整性",
            system_prompt="你是一位资深的合同条款分析专家。",
            capabilities=["基本信息提取", "关键条款识别", "条款完整性检查"],
            knowledge_bases=["主合同评审checklist.csv"],
            input_schema={},
            output_schema={}
        )
        self.agents["clause"] = ClauseAnalysisAgent(clause_config, self.llm)
        
        # 2. 风险评估Agent
        risk_config = AgentConfig(
            name="risk_assessment",
            display_name="风险评估专家",
            role="识别并量化评估风险",
            system_prompt="你是一位资深的风险评估专家。",
            capabilities=["风险识别", "风险量化", "应对建议"],
            knowledge_bases=["风险矩阵.csv"],
            input_schema={},
            output_schema={}
        )
        self.agents["risk"] = RiskAssessmentAgent(risk_config, self.llm)
        
        # 3. 合规检查Agent
        compliance_config = AgentConfig(
            name="compliance_check",
            display_name="合规检查专员",
            role="检查合同合规性",
            system_prompt="你是一位细致的合规检查专员。",
            capabilities=["SOP检查", "法律合规检查", "政策合规检查"],
            knowledge_bases=["可交付评审SOP流程说明.csv"],
            input_schema={},
            output_schema={}
        )
        self.agents["compliance"] = ComplianceCheckAgent(compliance_config, self.llm)
        
        # 4. 报告生成Agent
        report_config = AgentConfig(
            name="report_generation",
            display_name="首席评审官",
            role="生成最终评审报告",
            system_prompt="你是一位首席评审官，负责综合各方意见做出决策。",
            capabilities=["结果整合", "决策生成", "报告撰写"],
            knowledge_bases=[],
            input_schema={},
            output_schema={}
        )
        self.agents["report"] = ReportGenerationAgent(report_config, self.llm)
        
        logger.info("所有Agent加载完成 (Hardcoded)")

    async def execute_review_workflow(
        self,
        contract_markdown: str,
        knowledge_base: Dict
    ) -> Dict:
        """
        执行评审工作流
        
        流程:
        1. 条款分析 -> clause_result
        2. (并行) 风险评估 + 合规检查 -> risk_result, compliance_result
        3. 报告生成 -> final_report
        """
        start_time = datetime.now()
        context = {
            "checklist": knowledge_base.get("checklist", []),
            "risk_matrix": knowledge_base.get("risk_matrix", []),
            "sop": knowledge_base.get("sop", [])
        }
        
        results = {}
        
        try:
            # 阶段1: 条款分析
            logger.info("阶段1: 条款分析Agent 执行中...")
            clause_result = await self.agents["clause"].execute(
                {"contract_markdown": contract_markdown},
                context
            )
            results["clause"] = clause_result
            
            if clause_result.status == "failed":
                raise Exception(f"条款分析失败: {clause_result.error}")
            
            # 阶段2: 并行执行 风险评估 和 合规检查
            logger.info("阶段2: 风险评估 + 合规检查 并行执行...")
            
            risk_task = self.agents["risk"].execute(
                {
                    "contract_markdown": contract_markdown, 
                    "clause_analysis": clause_result.output
                },
                context
            )
            
            compliance_task = self.agents["compliance"].execute(
                {
                    "contract_markdown": contract_markdown, 
                    "clause_analysis": clause_result.output
                },
                context
            )
            
            risk_result, compliance_result = await asyncio.gather(risk_task, compliance_task)
            
            results["risk"] = risk_result
            results["compliance"] = compliance_result
            
            # 阶段3: 报告生成
            logger.info("阶段3: 报告生成Agent 执行中...")
            report_result = await self.agents["report"].execute(
                {"agent_outputs": results},
                context
            )
            results["report"] = report_result
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "workflow_id": f"wf_{int(start_time.timestamp())}",
                "duration": duration,
                "results": results,
                "final_report": report_result.output
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": results
            }

    def get_agents_info(self) -> List[Dict]:
        """获取所有Agent信息"""
        return [agent.get_info() for agent in self.agents.values()]
