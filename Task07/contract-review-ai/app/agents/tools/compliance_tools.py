from typing import Dict, List, Optional, Union
import pandas as pd

class ComplianceTools:
    """合规检查工具集"""
    
    @staticmethod
    def format_sop(sop_data: Union[List[Dict], str, pd.DataFrame]) -> str:
        """格式化SOP流程说明"""
        if isinstance(sop_data, pd.DataFrame):
            return sop_data.to_markdown(index=False)
        return str(sop_data)
