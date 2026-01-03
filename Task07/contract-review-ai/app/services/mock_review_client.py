"""
模拟评审客户端
用于测试完整工作流程，当 CodeBuddy API 不可用时使用
"""

import asyncio
import json
import logging
import random
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


class MockReviewClient:
    """
    模拟评审客户端
    生成示例评审结果，用于测试系统完整性
    """
    
    def __init__(self):
        logger.info("Mock评审客户端初始化（测试模式）")
    
    async def review_contract(
        self,
        contract_markdown: str,
        knowledge_base_files: List[str],
        session_id: Optional[str] = None
    ) -> Dict:
        """
        执行模拟合同评审
        
        Args:
            contract_markdown: 合同Markdown文本
            knowledge_base_files: 知识库文件路径列表
            session_id: 会话ID
            
        Returns:
            模拟的评审结果
        """
        try:
            logger.info("⚠️ 使用Mock模式生成评审结果（非真实AI评审）")
            
            # 模拟处理时间
            await asyncio.sleep(2)
            
            # 加载知识库获取评审标准
            kb_dict = self._load_knowledge_bases(knowledge_base_files)
            
            # 分析合同内容
            contract_info = self._analyze_contract(contract_markdown)
            
            # 生成评审结果
            review_result = self._generate_review_result(contract_info, kb_dict)
            
            return {
                "success": True,
                "review_result": review_result,
                "model": "mock-ai-reviewer-v1.0",
                "mode": "simulation",
                "warning": "这是模拟评审结果，仅供测试使用"
            }
            
        except Exception as e:
            error_msg = f"Mock评审失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def _load_knowledge_bases(self, kb_files: List[str]) -> Dict[str, pd.DataFrame]:
        """加载知识库"""
        kb_dict = {}
        
        for file_path in kb_files:
            try:
                path = Path(file_path)
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                kb_dict[path.stem] = df
                logger.info(f"加载知识库: {path.stem} ({len(df)} 行)")
            except Exception as e:
                logger.warning(f"加载知识库失败: {file_path}, {e}")
        
        return kb_dict
    
    def _analyze_contract(self, contract_markdown: str) -> Dict:
        """分析合同内容"""
        info = {
            "length": len(contract_markdown),
            "has_payment_terms": "支付" in contract_markdown or "款项" in contract_markdown,
            "has_delivery_terms": "交付" in contract_markdown or "验收" in contract_markdown,
            "has_liability_terms": "责任" in contract_markdown or "违约" in contract_markdown,
            "has_ip_terms": "知识产权" in contract_markdown or "专利" in contract_markdown,
            "party_a": "甲方" in contract_markdown,
            "party_b": "乙方" in contract_markdown,
        }
        
        # 提取关键词
        keywords = []
        if "软件" in contract_markdown:
            keywords.append("软件开发")
        if "框架协议" in contract_markdown:
            keywords.append("框架协议")
        if "委托开发" in contract_markdown:
            keywords.append("委托开发")
        
        info["keywords"] = keywords
        
        return info
    
    def _generate_review_result(self, contract_info: Dict, kb_dict: Dict) -> Dict:
        """生成评审结果"""
        
        # 基于合同特征生成风险等级
        risk_count = 0
        if not contract_info["has_payment_terms"]:
            risk_count += 2
        if not contract_info["has_delivery_terms"]:
            risk_count += 1
        if not contract_info["has_liability_terms"]:
            risk_count += 2
        if not contract_info["has_ip_terms"]:
            risk_count += 1
        
        risk_level = "高" if risk_count >= 4 else ("中" if risk_count >= 2 else "低")
        
        # 生成关键发现
        key_findings = []
        
        if not contract_info["has_payment_terms"]:
            key_findings.append({
                "category": "支付条款",
                "severity": "高",
                "description": "合同中未明确支付条款或金额约定不清晰",
                "location": "合同主体部分",
                "suggestion": "建议补充明确的支付金额、支付时间节点、支付方式等条款"
            })
        
        if not contract_info["has_delivery_terms"]:
            key_findings.append({
                "category": "交付验收",
                "severity": "中",
                "description": "缺少明确的交付标准和验收流程约定",
                "location": "履行条款",
                "suggestion": "建议增加详细的交付物描述、验收标准、验收期限等内容"
            })
        
        if not contract_info["has_liability_terms"]:
            key_findings.append({
                "category": "违约责任",
                "severity": "高",
                "description": "违约责任条款不完整或不明确",
                "location": "违约责任部分",
                "suggestion": "建议明确双方违约情形、违约金计算方式、损失赔偿范围"
            })
        
        if not contract_info["has_ip_terms"]:
            key_findings.append({
                "category": "知识产权",
                "severity": "中",
                "description": "知识产权归属约定不明确",
                "location": "权利义务部分",
                "suggestion": "建议明确约定开发成果的知识产权归属、使用权限、保密义务"
            })
        
        # 如果没有发现问题，添加一些常规建议
        if len(key_findings) == 0:
            key_findings.append({
                "category": "合同完整性",
                "severity": "低",
                "description": "合同主要条款完整，建议关注细节",
                "location": "全文",
                "suggestion": "建议核实各方主体资格、盖章签字的有效性"
            })
        
        # 合规性检查
        compliance_check = [
            {
                "item": "合同主体资格",
                "status": "需关注",
                "details": "请核实双方的营业执照、法定代表人身份等资质文件"
            },
            {
                "item": "必备条款完整性",
                "status": "通过" if len(key_findings) <= 2 else "不通过",
                "details": f"合同包含主要条款，发现 {len(key_findings)} 个需要关注的问题"
            },
            {
                "item": "法律合规性",
                "status": "需关注",
                "details": "建议法务部门进一步审核合同是否符合相关法律法规"
            }
        ]
        
        # 建议
        recommendations = [
            "建议在合同签订前进行充分的商务谈判，明确双方权利义务",
            "建议保留完整的合同签订流程记录和沟通往来邮件",
            "建议定期review合同执行情况，及时发现和解决潜在问题"
        ]
        
        if "框架协议" in contract_info.get("keywords", []):
            recommendations.append("框架协议建议补充具体的执行协议或订单，明确每次交易的细节")
        
        if "软件开发" in contract_info.get("keywords", []):
            recommendations.append("软件开发合同建议明确技术规格、开发进度、测试标准等技术细节")
        
        # 缺失条款
        missing_clauses = []
        if not contract_info["has_ip_terms"]:
            missing_clauses.append("知识产权归属条款")
        if "保密" not in str(contract_info):
            missing_clauses.append("保密条款")
        if "争议解决" not in str(contract_info):
            missing_clauses.append("争议解决条款（仲裁/诉讼）")
        
        # 汇总评估
        overall_assessment = f"合同整体风险等级为【{risk_level}】。"
        if len(key_findings) > 0:
            overall_assessment += f"发现 {len(key_findings)} 个需要重点关注的问题，建议在签订前进行修改完善。"
        else:
            overall_assessment += "合同条款相对完整，建议进行常规法务审核后签署。"
        
        result = {
            "overall_assessment": overall_assessment,
            "risk_level": risk_level,
            "key_findings": key_findings,
            "compliance_check": compliance_check,
            "recommendations": recommendations,
            "missing_clauses": missing_clauses,
            "metadata": {
                "contract_length": contract_info["length"],
                "keywords": contract_info.get("keywords", []),
                "knowledge_base_used": len(kb_dict),
                "review_mode": "simulation"
            }
        }
        
        return result


# 测试代码
async def test_mock_client():
    """测试Mock客户端"""
    print("\n" + "=" * 80)
    print("测试 Mock 评审客户端")
    print("=" * 80)
    
    client = MockReviewClient()
    
    # 读取测试合同
    contract_path = Path("data/outputs/70820fb8-fcde-4c4a-993c-3bdcdcab0925/combined.md")
    
    if not contract_path.exists():
        print(f"\n❌ 测试合同不存在: {contract_path}")
        return
    
    print(f"\n📄 读取测试合同...")
    contract_content = contract_path.read_text(encoding="utf-8")
    print(f"   合同长度: {len(contract_content):,} 字符")
    
    # 准备知识库
    kb_dir = Path("知识库")
    kb_files = [str(f) for f in kb_dir.glob("*.csv")]
    print(f"\n📚 使用 {len(kb_files)} 个知识库文件")
    
    # 执行评审
    print("\n⏳ 开始Mock评审...")
    result = await client.review_contract(
        contract_markdown=contract_content,
        knowledge_base_files=kb_files
    )
    
    if result["success"]:
        print("\n✅ 评审完成!")
        
        review = result["review_result"]
        
        print("\n" + "=" * 80)
        print("评审结果摘要")
        print("=" * 80)
        print(f"\n总体评价: {review['overall_assessment']}")
        print(f"风险等级: {review['risk_level']}")
        print(f"\n关键发现数: {len(review['key_findings'])}")
        for idx, finding in enumerate(review['key_findings'], 1):
            print(f"  {idx}. [{finding['severity']}] {finding['category']}: {finding['description']}")
        
        print(f"\n建议数: {len(review['recommendations'])}")
        for idx, rec in enumerate(review['recommendations'], 1):
            print(f"  {idx}. {rec}")
        
        print(f"\n缺失条款: {', '.join(review['missing_clauses']) if review['missing_clauses'] else '无'}")
        
        print("\n" + "=" * 80)
        
        # 保存结果
        output_file = contract_path.parent / "mock_review_result.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result["review_result"], f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 结果已保存: {output_file}")
        
    else:
        print(f"\n❌ 评审失败: {result['error']}")


if __name__ == "__main__":
    asyncio.run(test_mock_client())
