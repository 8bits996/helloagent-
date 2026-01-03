from typing import Dict, List, Optional, Union
import pandas as pd

class RiskTools:
    """风险评估工具集"""
    
    @staticmethod
    def format_risk_matrix(matrix_data: Union[List[Dict], str, pd.DataFrame]) -> str:
        """格式化风险矩阵"""
        if isinstance(matrix_data, pd.DataFrame):
            return matrix_data.to_markdown(index=False)
        # 其他类型处理类似ClauseTools
        return str(matrix_data)
