from typing import Dict, List, Optional, Union
import json

class ReportTools:
    """报告生成工具集"""
    
    @staticmethod
    def aggregate_results(clause_result: Dict, risk_result: Dict, compliance_result: Dict) -> Dict:
        """聚合各Agent的结果"""
        return {
            "clause_analysis": clause_result,
            "risk_assessment": risk_result,
            "compliance_check": compliance_result
        }
