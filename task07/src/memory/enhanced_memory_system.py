"""
增强记忆系统 - 支持持久化存储、上下文分析和记忆整合
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading
import re
from collections import defaultdict


class MemoryType(Enum):
    """记忆类型枚举"""
    SHORT_TERM = "short_term"      # 短期记忆（当前会话）
    LONG_TERM = "long_term"        # 长期记忆（跨会话）
    EPISODIC = "episodic"          # 情景记忆（特定事件）
    SEMANTIC = "semantic"          # 语义记忆（知识和事实）
    PROCEDURAL = "procedural"      # 程序记忆（操作步骤）


class ImportanceLevel(Enum):
    """重要性级别"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryItem:
    """记忆项数据结构"""
    id: str
    content: str
    memory_type: MemoryType
    importance: ImportanceLevel
    timestamp: datetime
    context_tags: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'importance': self.importance.value,
            'timestamp': self.timestamp.isoformat(),
            'context_tags': self.context_tags,
            'related_memories': self.related_memories,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'embedding': self.embedding,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryItem':
        """从字典创建"""
        return cls(
            id=data['id'],
            content=data['content'],
            memory_type=MemoryType(data['memory_type']),
            importance=ImportanceLevel(data['importance']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            context_tags=data.get('context_tags', []),
            related_memories=data.get('related_memories', []),
            access_count=data.get('access_count', 0),
            last_accessed=datetime.fromisoformat(data['last_accessed']) if data.get('last_accessed') else None,
            embedding=data.get('embedding'),
            metadata=data.get('metadata', {})
        )


@dataclass
class ConversationContext:
    """会话上下文"""
    session_id: str
    user_id: Optional[str]
    start_time: datetime
    messages: List[Dict[str, str]] = field(default_factory=list)
    current_topic: Optional[str] = None
    detected_intents: List[str] = field(default_factory=list)
    entity_mentions: Dict[str, List[str]] = field(default_factory=dict)
    sentiment_history: List[float] = field(default_factory=list)
    tool_usage: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加消息"""
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        })
    
    def get_recent_messages(self, count: int = 10) -> List[Dict]:
        """获取最近的消息"""
        return self.messages[-count:]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat(),
            'messages': self.messages,
            'current_topic': self.current_topic,
            'detected_intents': self.detected_intents,
            'entity_mentions': self.entity_mentions,
            'sentiment_history': self.sentiment_history,
            'tool_usage': self.tool_usage
        }


class ContextAnalyzer:
    """上下文分析器 - 分析对话上下文，提取关键信息"""
    
    # 意图关键词映射
    INTENT_PATTERNS = {
        'code_help': ['代码', '编程', '函数', '类', '调试', 'bug', '错误', 'code', 'programming'],
        'search': ['搜索', '查找', '找', '搜', 'search', 'find'],
        'file_operation': ['文件', '创建', '删除', '修改', '保存', 'file', 'create', 'delete'],
        'system_info': ['系统', '环境', '版本', 'system', 'version', 'env'],
        'learning': ['学习', '教程', '怎么', '如何', 'learn', 'tutorial', 'how'],
        'analysis': ['分析', '检查', '审计', '评估', 'analyze', 'check', 'audit'],
    }
    
    # 实体模式
    ENTITY_PATTERNS = {
        'file_path': r'[\w\-./\\]+\.\w+',
        'url': r'https?://[\w\-./]+',
        'version': r'v?\d+\.\d+(?:\.\d+)?',
        'command': r'`[^`]+`',
        'code_block': r'```[\s\S]*?```',
    }
    
    def __init__(self):
        self.topic_history: List[str] = []
    
    def analyze(self, context: ConversationContext) -> Dict[str, Any]:
        """分析会话上下文"""
        recent_messages = context.get_recent_messages(5)
        
        # 提取最新消息内容
        latest_content = recent_messages[-1]['content'] if recent_messages else ""
        all_content = " ".join([m['content'] for m in recent_messages])
        
        analysis = {
            'detected_intents': self._detect_intents(all_content),
            'entities': self._extract_entities(all_content),
            'topic': self._identify_topic(all_content),
            'complexity': self._assess_complexity(latest_content),
            'sentiment': self._analyze_sentiment(latest_content),
            'suggested_tools': self._suggest_tools(all_content),
        }
        
        return analysis
    
    def _detect_intents(self, text: str) -> List[str]:
        """检测用户意图"""
        detected = []
        text_lower = text.lower()
        
        for intent, keywords in self.INTENT_PATTERNS.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(intent)
        
        return detected
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """提取实体"""
        entities = {}
        
        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
    def _identify_topic(self, text: str) -> str:
        """识别当前话题"""
        intents = self._detect_intents(text)
        
        if 'code_help' in intents:
            return 'programming'
        elif 'file_operation' in intents:
            return 'file_management'
        elif 'search' in intents:
            return 'information_retrieval'
        elif 'analysis' in intents:
            return 'code_analysis'
        elif 'learning' in intents:
            return 'learning'
        else:
            return 'general'
    
    def _assess_complexity(self, text: str) -> str:
        """评估任务复杂度"""
        # 基于文本长度和特征评估
        word_count = len(text.split())
        has_code = '```' in text or '`' in text
        has_multiple_requests = text.count('？') + text.count('?') > 1
        
        if word_count > 100 or (has_code and has_multiple_requests):
            return 'high'
        elif word_count > 30 or has_code:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_sentiment(self, text: str) -> float:
        """简单情感分析（返回-1到1之间的值）"""
        positive_words = ['好', '棒', '谢谢', '感谢', '完美', 'good', 'great', 'thanks', 'perfect']
        negative_words = ['差', '错', '问题', '失败', '糟糕', 'bad', 'error', 'problem', 'fail']
        
        text_lower = text.lower()
        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def _suggest_tools(self, text: str) -> List[str]:
        """根据上下文建议工具"""
        suggestions = []
        intents = self._detect_intents(text)
        
        if 'search' in intents:
            suggestions.append('browser_search')
        if 'file_operation' in intents:
            suggestions.append('file_edit')
        if 'system_info' in intents or 'code_help' in intents:
            suggestions.append('terminal_exec')
        if 'analysis' in intents:
            suggestions.append('code_analysis')
        
        return suggestions


class MemoryConsolidator:
    """记忆整合器 - 整合和优化记忆存储"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
    
    def consolidate(self, memories: List[MemoryItem]) -> List[MemoryItem]:
        """整合相似记忆"""
        if len(memories) < 2:
            return memories
        
        # 按内容相似度分组
        groups = self._group_similar_memories(memories)
        
        # 合并每个组
        consolidated = []
        for group in groups:
            if len(group) == 1:
                consolidated.append(group[0])
            else:
                merged = self._merge_memories(group)
                consolidated.append(merged)
        
        return consolidated
    
    def _group_similar_memories(self, memories: List[MemoryItem]) -> List[List[MemoryItem]]:
        """将相似记忆分组"""
        groups = []
        used = set()
        
        for i, mem1 in enumerate(memories):
            if i in used:
                continue
            
            group = [mem1]
            used.add(i)
            
            for j, mem2 in enumerate(memories[i+1:], start=i+1):
                if j not in used and self._calculate_similarity(mem1, mem2) >= self.similarity_threshold:
                    group.append(mem2)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _calculate_similarity(self, mem1: MemoryItem, mem2: MemoryItem) -> float:
        """计算两个记忆的相似度（简单实现）"""
        # 基于共同词汇的Jaccard相似度
        words1 = set(mem1.content.lower().split())
        words2 = set(mem2.content.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _merge_memories(self, memories: List[MemoryItem]) -> MemoryItem:
        """合并多个记忆为一个"""
        # 选择最重要的作为基础
        base = max(memories, key=lambda m: (m.importance.value, m.access_count))
        
        # 合并标签
        all_tags = set()
        for mem in memories:
            all_tags.update(mem.context_tags)
        
        # 合并关联记忆
        all_related = set()
        for mem in memories:
            all_related.update(mem.related_memories)
        
        # 更新访问计数
        total_access = sum(m.access_count for m in memories)
        
        return MemoryItem(
            id=base.id,
            content=base.content,
            memory_type=base.memory_type,
            importance=base.importance,
            timestamp=base.timestamp,
            context_tags=list(all_tags),
            related_memories=list(all_related),
            access_count=total_access,
            last_accessed=max((m.last_accessed for m in memories if m.last_accessed), default=None),
            embedding=base.embedding,
            metadata={**base.metadata, 'merged_count': len(memories)}
        )
    
    def prioritize(self, memories: List[MemoryItem], limit: int = 10) -> List[MemoryItem]:
        """优先级排序，返回最重要的记忆"""
        def score(mem: MemoryItem) -> float:
            # 综合评分：重要性 * 2 + 访问频率 + 时效性
            importance_score = mem.importance.value * 2
            access_score = min(mem.access_count / 10, 1.0)
            
            # 时效性：最近的记忆得分更高
            days_old = (datetime.now() - mem.timestamp).days
            recency_score = max(0, 1 - days_old / 30)
            
            return importance_score + access_score + recency_score
        
        sorted_memories = sorted(memories, key=score, reverse=True)
        return sorted_memories[:limit]


class EnhancedMemorySystem:
    """增强记忆系统 - 主类"""
    
    def __init__(self, db_path: str = "data/memory.db", max_short_term: int = 100):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.max_short_term = max_short_term
        self.short_term_memory: Dict[str, MemoryItem] = {}
        self.current_context: Optional[ConversationContext] = None
        
        self.analyzer = ContextAnalyzer()
        self.consolidator = MemoryConsolidator()
        
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """初始化SQLite数据库"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # 记忆表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    context_tags TEXT,
                    related_memories TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    embedding TEXT,
                    metadata TEXT
                )
            ''')
            
            # 会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    messages TEXT,
                    summary TEXT,
                    metadata TEXT
                )
            ''')
            
            # 索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)')
            
            conn.commit()
    
    def start_session(self, session_id: Optional[str] = None, user_id: Optional[str] = None) -> ConversationContext:
        """开始新会话"""
        if session_id is None:
            session_id = hashlib.md5(f"{datetime.now().isoformat()}{user_id}".encode()).hexdigest()[:16]
        
        self.current_context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now()
        )
        
        return self.current_context
    
    def end_session(self, summary: Optional[str] = None):
        """结束会话并保存"""
        if self.current_context is None:
            return
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_id, user_id, start_time, end_time, messages, summary, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_context.session_id,
                self.current_context.user_id,
                self.current_context.start_time.isoformat(),
                datetime.now().isoformat(),
                json.dumps(self.current_context.messages, ensure_ascii=False),
                summary,
                json.dumps({
                    'detected_intents': self.current_context.detected_intents,
                    'tool_usage': self.current_context.tool_usage
                }, ensure_ascii=False)
            ))
            conn.commit()
        
        # 将重要的短期记忆转为长期记忆
        self._promote_important_memories()
        
        self.current_context = None
    
    def close(self):
        """关闭记忆系统，释放资源"""
        # 如果有未结束的会话，先结束
        if self.current_context is not None:
            self.end_session("Session closed")
        
        # 清理短期记忆
        self.short_term_memory.clear()
    
    def add_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: ImportanceLevel = ImportanceLevel.MEDIUM,
        context_tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> MemoryItem:
        """添加新记忆"""
        memory_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        memory = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            timestamp=datetime.now(),
            context_tags=context_tags or [],
            metadata=metadata or {}
        )
        
        with self._lock:
            if memory_type == MemoryType.SHORT_TERM:
                self.short_term_memory[memory_id] = memory
                self._manage_short_term_capacity()
            else:
                self._save_to_database(memory)
        
        return memory
    
    def add_interaction(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加交互记录到当前会话"""
        if self.current_context is None:
            self.start_session()
        
        self.current_context.add_message(role, content, metadata)
        
        # 分析上下文
        analysis = self.analyzer.analyze(self.current_context)
        self.current_context.detected_intents = analysis['detected_intents']
        self.current_context.current_topic = analysis['topic']
        
        # 根据重要性决定是否保存为记忆
        if analysis['complexity'] in ['medium', 'high']:
            self.add_memory(
                content=content,
                memory_type=MemoryType.SHORT_TERM,
                importance=ImportanceLevel.HIGH if analysis['complexity'] == 'high' else ImportanceLevel.MEDIUM,
                context_tags=analysis['detected_intents']
            )
    
    def recall(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        include_context: bool = True
    ) -> List[MemoryItem]:
        """回忆相关记忆"""
        results = []
        
        # 搜索短期记忆
        for memory in self.short_term_memory.values():
            if memory_types and memory.memory_type not in memory_types:
                continue
            if self._is_relevant(query, memory):
                results.append(memory)
                memory.access_count += 1
                memory.last_accessed = datetime.now()
        
        # 搜索长期记忆
        db_results = self._search_database(query, memory_types, limit)
        results.extend(db_results)
        
        # 优先级排序
        results = self.consolidator.prioritize(results, limit)
        
        return results
    
    def get_context_summary(self) -> Dict[str, Any]:
        """获取当前上下文摘要"""
        if self.current_context is None:
            return {'status': 'no_active_session'}
        
        analysis = self.analyzer.analyze(self.current_context)
        
        return {
            'session_id': self.current_context.session_id,
            'message_count': len(self.current_context.messages),
            'current_topic': self.current_context.current_topic,
            'detected_intents': self.current_context.detected_intents,
            'analysis': analysis,
            'short_term_memory_count': len(self.short_term_memory)
        }
    
    def get_relevant_context(self, query: str, max_tokens: int = 2000) -> str:
        """获取与查询相关的上下文（用于注入到提示词）"""
        # 获取相关记忆
        memories = self.recall(query, limit=5)
        
        # 获取最近消息
        recent_messages = []
        if self.current_context:
            recent_messages = self.current_context.get_recent_messages(5)
        
        # 构建上下文字符串
        context_parts = []
        
        if memories:
            context_parts.append("## 相关记忆")
            for mem in memories:
                context_parts.append(f"- [{mem.memory_type.value}] {mem.content}")
        
        if recent_messages:
            context_parts.append("\n## 最近对话")
            for msg in recent_messages[-3:]:
                context_parts.append(f"- {msg['role']}: {msg['content'][:100]}...")
        
        context_str = "\n".join(context_parts)
        
        # 简单的token估算（中文约2字符/token）
        estimated_tokens = len(context_str) // 2
        if estimated_tokens > max_tokens:
            # 截断
            context_str = context_str[:max_tokens * 2]
        
        return context_str
    
    def _is_relevant(self, query: str, memory: MemoryItem) -> bool:
        """判断记忆是否与查询相关"""
        query_words = set(query.lower().split())
        memory_words = set(memory.content.lower().split())
        memory_tags = set(tag.lower() for tag in memory.context_tags)
        
        # 检查词汇重叠
        word_overlap = query_words & memory_words
        tag_overlap = query_words & memory_tags
        
        return len(word_overlap) > 0 or len(tag_overlap) > 0
    
    def _save_to_database(self, memory: MemoryItem):
        """保存记忆到数据库"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO memories 
                (id, content, memory_type, importance, timestamp, context_tags, 
                 related_memories, access_count, last_accessed, embedding, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.id,
                memory.content,
                memory.memory_type.value,
                memory.importance.value,
                memory.timestamp.isoformat(),
                json.dumps(memory.context_tags),
                json.dumps(memory.related_memories),
                memory.access_count,
                memory.last_accessed.isoformat() if memory.last_accessed else None,
                json.dumps(memory.embedding) if memory.embedding else None,
                json.dumps(memory.metadata)
            ))
            conn.commit()
    
    def _search_database(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """从数据库搜索记忆"""
        results = []
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # 构建查询
            sql = "SELECT * FROM memories WHERE content LIKE ?"
            params = [f"%{query}%"]
            
            if memory_types:
                type_placeholders = ",".join("?" * len(memory_types))
                sql += f" AND memory_type IN ({type_placeholders})"
                params.extend([mt.value for mt in memory_types])
            
            sql += " ORDER BY importance DESC, access_count DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            for row in rows:
                memory = MemoryItem(
                    id=row[0],
                    content=row[1],
                    memory_type=MemoryType(row[2]),
                    importance=ImportanceLevel(row[3]),
                    timestamp=datetime.fromisoformat(row[4]),
                    context_tags=json.loads(row[5]) if row[5] else [],
                    related_memories=json.loads(row[6]) if row[6] else [],
                    access_count=row[7],
                    last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
                    embedding=json.loads(row[9]) if row[9] else None,
                    metadata=json.loads(row[10]) if row[10] else {}
                )
                results.append(memory)
        
        return results
    
    def _manage_short_term_capacity(self):
        """管理短期记忆容量"""
        if len(self.short_term_memory) <= self.max_short_term:
            return
        
        # 整合相似记忆
        memories = list(self.short_term_memory.values())
        consolidated = self.consolidator.consolidate(memories)
        
        # 如果仍然超过限制，移除最不重要的
        if len(consolidated) > self.max_short_term:
            prioritized = self.consolidator.prioritize(consolidated, self.max_short_term)
            
            # 将被移除的重要记忆保存到长期存储
            removed = set(m.id for m in consolidated) - set(m.id for m in prioritized)
            for mem_id in removed:
                if mem_id in self.short_term_memory:
                    mem = self.short_term_memory[mem_id]
                    if mem.importance.value >= ImportanceLevel.MEDIUM.value:
                        mem.memory_type = MemoryType.LONG_TERM
                        self._save_to_database(mem)
            
            consolidated = prioritized
        
        # 更新短期记忆
        self.short_term_memory = {m.id: m for m in consolidated}
    
    def _promote_important_memories(self):
        """将重要的短期记忆提升为长期记忆"""
        for memory in list(self.short_term_memory.values()):
            if memory.importance.value >= ImportanceLevel.HIGH.value:
                memory.memory_type = MemoryType.LONG_TERM
                self._save_to_database(memory)
        
        # 清空短期记忆
        self.short_term_memory.clear()
    
    def cleanup_old_memories(self, days: int = 30):
        """清理旧记忆"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            # 只删除低重要性的旧记忆
            cursor.execute('''
                DELETE FROM memories 
                WHERE timestamp < ? AND importance <= ?
            ''', (cutoff.isoformat(), ImportanceLevel.LOW.value))
            conn.commit()
    
    def export_memories(self, filepath: str):
        """导出所有记忆到JSON文件"""
        all_memories = []
        
        # 短期记忆
        for mem in self.short_term_memory.values():
            all_memories.append(mem.to_dict())
        
        # 长期记忆
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories")
            rows = cursor.fetchall()
            
            for row in rows:
                memory = MemoryItem(
                    id=row[0],
                    content=row[1],
                    memory_type=MemoryType(row[2]),
                    importance=ImportanceLevel(row[3]),
                    timestamp=datetime.fromisoformat(row[4]),
                    context_tags=json.loads(row[5]) if row[5] else [],
                    related_memories=json.loads(row[6]) if row[6] else [],
                    access_count=row[7],
                    last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
                    embedding=json.loads(row[9]) if row[9] else None,
                    metadata=json.loads(row[10]) if row[10] else {}
                )
                all_memories.append(memory.to_dict())
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_memories, f, ensure_ascii=False, indent=2)
    
    def import_memories(self, filepath: str):
        """从JSON文件导入记忆"""
        with open(filepath, 'r', encoding='utf-8') as f:
            memories_data = json.load(f)
        
        for data in memories_data:
            memory = MemoryItem.from_dict(data)
            if memory.memory_type == MemoryType.SHORT_TERM:
                self.short_term_memory[memory.id] = memory
            else:
                self._save_to_database(memory)
