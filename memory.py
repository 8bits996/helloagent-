"""
Memory 短期记忆模块
用于 Reflection Agent 存储执行和反思轨迹

作用：
- 记录每一轮的"执行"结果和"反思"反馈
- 为后续迭代提供完整的上下文
- 支持获取最新的执行结果
"""

from typing import List, Dict, Any, Optional


class Memory:
    """
    一个简单的短期记忆模块，用于存储智能体的行动与反思轨迹
    
    记录类型：
    - 'execution': 执行结果（如生成的代码）
    - 'reflection': 反思反馈（如评审意见）
    """
    
    def __init__(self):
        """初始化一个空列表来存储所有记录"""
        self.records: List[Dict[str, Any]] = []
    
    def add_record(self, record_type: str, content: str):
        """
        向记忆中添加一条新记录
        
        参数:
            record_type: 记录的类型 ('execution' 或 'reflection')
            content: 记录的具体内容
        """
        record = {"type": record_type, "content": content}
        self.records.append(record)
        print(f"📝 记忆已更新，新增一条 '{record_type}' 记录")
    
    def get_trajectory(self) -> str:
        """
        将所有记忆记录格式化为一个连贯的字符串文本
        用于构建提示词的上下文
        
        返回:
            str: 格式化的历史轨迹
        """
        trajectory_parts = []
        
        for record in self.records:
            if record['type'] == 'execution':
                trajectory_parts.append(
                    f"--- 上一轮尝试 (代码) ---\n{record['content']}"
                )
            elif record['type'] == 'reflection':
                trajectory_parts.append(
                    f"--- 评审员反馈 ---\n{record['content']}"
                )
        
        return "\n\n".join(trajectory_parts)
    
    def get_last_execution(self) -> Optional[str]:
        """
        获取最近一次的执行结果（如最新生成的代码）
        
        返回:
            str: 最新的执行结果
            None: 如果没有执行记录
        """
        # 从后往前遍历，找到最近的 execution 记录
        for record in reversed(self.records):
            if record['type'] == 'execution':
                return record['content']
        return None
    
    def get_record_count(self) -> Dict[str, int]:
        """
        获取各类型记录的数量统计
        
        返回:
            dict: {'execution': 数量, 'reflection': 数量}
        """
        counts = {'execution': 0, 'reflection': 0}
        for record in self.records:
            record_type = record.get('type', 'unknown')
            if record_type in counts:
                counts[record_type] += 1
        return counts
    
    def clear(self):
        """清空所有记忆记录"""
        self.records.clear()
        print("🗑️  记忆已清空")
    
    def __len__(self):
        """返回记录总数"""
        return len(self.records)
    
    def __str__(self):
        """返回记忆的字符串表示"""
        counts = self.get_record_count()
        return f"Memory(总记录数={len(self)}, 执行={counts['execution']}, 反思={counts['reflection']})"


# ===========================
# 测试代码
# ===========================

if __name__ == '__main__':
    print("测试 Memory 模块\n")
    
    # 创建记忆实例
    memory = Memory()
    print(f"初始状态: {memory}\n")
    
    # 模拟第一轮执行
    print("--- 第1轮 ---")
    memory.add_record('execution', 'def find_primes(n):\n    # 简单实现\n    pass')
    memory.add_record('reflection', '算法复杂度太高，建议使用筛法')
    print(f"状态: {memory}\n")
    
    # 模拟第二轮执行
    print("--- 第2轮 ---")
    memory.add_record('execution', 'def find_primes(n):\n    # 筛法实现\n    pass')
    memory.add_record('reflection', '算法已达最优，无需改进')
    print(f"状态: {memory}\n")
    
    # 获取最新执行结果
    print("--- 获取最新代码 ---")
    last_code = memory.get_last_execution()
    print(f"最新代码:\n{last_code}\n")
    
    # 获取完整轨迹
    print("--- 完整轨迹 ---")
    trajectory = memory.get_trajectory()
    print(trajectory)
