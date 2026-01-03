"""
高级代码分析工具 - 支持多维度代码质量检查
"""

import os
import re
import ast
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AnalysisDimension(Enum):
    """分析维度"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    COMPLEXITY = "complexity"
    BUG_RISK = "bug_risk"


class IssueSeverity(Enum):
    """问题严重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CodeIssue:
    """代码问题数据结构"""
    dimension: AnalysisDimension
    severity: IssueSeverity
    message: str
    line: int
    column: int = 0
    code_snippet: str = ""
    rule_id: str = ""
    suggestion: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'dimension': self.dimension.value,
            'severity': self.severity.value,
            'message': self.message,
            'line': self.line,
            'column': self.column,
            'code_snippet': self.code_snippet,
            'rule_id': self.rule_id,
            'suggestion': self.suggestion
        }


class AdvancedCodeAnalysisTool:
    """高级代码分析工具"""
    
    name = "code_analysis"
    description = "高级代码分析工具，支持安全、性能、风格、复杂度和Bug风险五维度分析"
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # 默认配置
        self.max_line_length = self.config.get('max_line_length', 120)
        self.max_function_length = self.config.get('max_function_length', 50)
        self.max_complexity = self.config.get('max_complexity', 10)
        self.max_parameters = self.config.get('max_parameters', 5)
        self.max_nesting_depth = self.config.get('max_nesting_depth', 4)
        
        # 安全规则
        self.security_rules = self._init_security_rules()
        
        # 性能规则
        self.performance_rules = self._init_performance_rules()
        
        # 风格规则
        self.style_rules = self._init_style_rules()
    
    def get_parameters(self) -> Dict:
        return {
            "path": {
                "type": "str",
                "description": "要分析的文件或目录路径",
                "required": False
            },
            "content": {
                "type": "str",
                "description": "要分析的代码内容",
                "required": False
            },
            "dimensions": {
                "type": "list",
                "description": "分析维度列表：security, performance, style, complexity, bug_risk",
                "required": False,
                "default": ["security", "performance", "style", "complexity", "bug_risk"]
            },
            "output_format": {
                "type": "str",
                "description": "输出格式：json, text, markdown",
                "required": False,
                "default": "text"
            }
        }
    
    def run(self, parameters: Dict) -> str:
        """运行代码分析"""
        if isinstance(parameters, str):
            # 简单模式：直接分析代码
            return self._analyze_and_format(parameters, None, ['security', 'performance', 'style', 'complexity', 'bug_risk'], 'text')
        
        path = parameters.get('path')
        content = parameters.get('content')
        dimensions = parameters.get('dimensions', ['security', 'performance', 'style', 'complexity', 'bug_risk'])
        output_format = parameters.get('output_format', 'text')
        
        if path:
            path = Path(path)
            if path.is_file():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif path.is_dir():
                return self._analyze_directory(path, dimensions, output_format)
            else:
                return f"错误：路径不存在 - {path}"
        
        if not content:
            return "错误：请提供代码内容或有效的文件路径"
        
        return self._analyze_and_format(content, str(path) if path else None, dimensions, output_format)
    
    def _analyze_and_format(self, content: str, filepath: Optional[str], dimensions: List[str], output_format: str) -> str:
        """分析并格式化结果"""
        result = self.analyze(content, filepath, dimensions)
        
        if output_format == 'json':
            return json.dumps(result, ensure_ascii=False, indent=2)
        elif output_format == 'markdown':
            return self._format_markdown(result)
        else:
            return self._format_text(result)
    
    def analyze(self, content: str, filepath: Optional[str] = None, dimensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """执行代码分析"""
        dimensions = dimensions or ['security', 'performance', 'style', 'complexity', 'bug_risk']
        
        result = {
            'filepath': filepath,
            'issues': [],
            'metrics': {},
            'summary': {}
        }
        
        lines = content.split('\n')
        
        # 基础指标
        result['metrics'] = self._calculate_metrics(content, lines)
        
        # 按维度分析
        if 'security' in dimensions:
            result['issues'].extend(self._analyze_security(content, lines))
        
        if 'performance' in dimensions:
            result['issues'].extend(self._analyze_performance(content, lines))
        
        if 'style' in dimensions:
            result['issues'].extend(self._analyze_style(content, lines))
        
        if 'complexity' in dimensions:
            complexity_issues, complexity_metrics = self._analyze_complexity(content)
            result['issues'].extend(complexity_issues)
            result['metrics']['complexity'] = complexity_metrics
        
        if 'bug_risk' in dimensions:
            result['issues'].extend(self._analyze_bug_risk(content, lines))
        
        # 生成摘要
        result['summary'] = self._generate_summary(result)
        
        return result
    
    def _calculate_metrics(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """计算代码指标"""
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        comment_lines = [l for l in lines if l.strip().startswith('#')]
        
        return {
            'total_lines': len(lines),
            'code_lines': len(code_lines),
            'comment_lines': len(comment_lines),
            'blank_lines': len([l for l in lines if not l.strip()]),
            'comment_ratio': len(comment_lines) / len(code_lines) if code_lines else 0,
            'average_line_length': sum(len(l) for l in code_lines) / len(code_lines) if code_lines else 0
        }
    
    def _analyze_security(self, content: str, lines: List[str]) -> List[CodeIssue]:
        """安全分析"""
        issues = []
        
        for rule_id, rule in self.security_rules.items():
            pattern = rule['pattern']
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        dimension=AnalysisDimension.SECURITY,
                        severity=IssueSeverity[rule['severity'].upper()],
                        message=rule['message'],
                        line=i,
                        code_snippet=line.strip()[:100],
                        rule_id=rule_id,
                        suggestion=rule.get('suggestion', '')
                    ))
        
        return issues
    
    def _analyze_performance(self, content: str, lines: List[str]) -> List[CodeIssue]:
        """性能分析"""
        issues = []
        
        for rule_id, rule in self.performance_rules.items():
            pattern = rule['pattern']
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        dimension=AnalysisDimension.PERFORMANCE,
                        severity=IssueSeverity[rule['severity'].upper()],
                        message=rule['message'],
                        line=i,
                        code_snippet=line.strip()[:100],
                        rule_id=rule_id,
                        suggestion=rule.get('suggestion', '')
                    ))
        
        return issues
    
    def _analyze_style(self, content: str, lines: List[str]) -> List[CodeIssue]:
        """风格分析"""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # 行长度检查
            if len(line) > self.max_line_length:
                issues.append(CodeIssue(
                    dimension=AnalysisDimension.STYLE,
                    severity=IssueSeverity.WARNING,
                    message=f"行长度超过 {self.max_line_length} 字符 ({len(line)} 字符)",
                    line=i,
                    rule_id='line_length',
                    suggestion=f"将行拆分为多行，保持每行不超过 {self.max_line_length} 字符"
                ))
            
            # 尾随空白
            if line.rstrip() != line and line.strip():
                issues.append(CodeIssue(
                    dimension=AnalysisDimension.STYLE,
                    severity=IssueSeverity.INFO,
                    message="行尾有多余空白",
                    line=i,
                    rule_id='trailing_whitespace',
                    suggestion="删除行尾的空白字符"
                ))
            
            # 混合缩进
            if line.startswith(' ') and '\t' in line[:len(line) - len(line.lstrip())]:
                issues.append(CodeIssue(
                    dimension=AnalysisDimension.STYLE,
                    severity=IssueSeverity.WARNING,
                    message="混合使用空格和制表符缩进",
                    line=i,
                    rule_id='mixed_indentation',
                    suggestion="统一使用空格或制表符进行缩进"
                ))
        
        # 应用自定义风格规则
        for rule_id, rule in self.style_rules.items():
            pattern = rule['pattern']
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        dimension=AnalysisDimension.STYLE,
                        severity=IssueSeverity[rule['severity'].upper()],
                        message=rule['message'],
                        line=i,
                        code_snippet=line.strip()[:100],
                        rule_id=rule_id,
                        suggestion=rule.get('suggestion', '')
                    ))
        
        return issues
    
    def _analyze_complexity(self, content: str) -> Tuple[List[CodeIssue], Dict]:
        """复杂度分析"""
        issues = []
        metrics = {
            'functions': [],
            'classes': [],
            'average_complexity': 0,
            'max_complexity': 0
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    func_lines = (node.end_lineno - node.lineno + 1) if hasattr(node, 'end_lineno') else 0
                    param_count = len(node.args.args)
                    nesting_depth = self._calculate_nesting_depth(node)
                    
                    func_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'complexity': complexity,
                        'lines': func_lines,
                        'parameters': param_count,
                        'nesting_depth': nesting_depth
                    }
                    metrics['functions'].append(func_info)
                    
                    # 检查复杂度
                    if complexity > self.max_complexity:
                        issues.append(CodeIssue(
                            dimension=AnalysisDimension.COMPLEXITY,
                            severity=IssueSeverity.WARNING if complexity <= self.max_complexity * 1.5 else IssueSeverity.ERROR,
                            message=f"函数 '{node.name}' 圈复杂度过高 ({complexity}，阈值 {self.max_complexity})",
                            line=node.lineno,
                            rule_id='high_complexity',
                            suggestion="考虑将函数拆分为更小的函数，或简化条件逻辑"
                        ))
                    
                    # 检查函数长度
                    if func_lines > self.max_function_length:
                        issues.append(CodeIssue(
                            dimension=AnalysisDimension.COMPLEXITY,
                            severity=IssueSeverity.WARNING,
                            message=f"函数 '{node.name}' 过长 ({func_lines} 行，阈值 {self.max_function_length})",
                            line=node.lineno,
                            rule_id='function_length',
                            suggestion="将函数拆分为更小的辅助函数"
                        ))
                    
                    # 检查参数数量
                    if param_count > self.max_parameters:
                        issues.append(CodeIssue(
                            dimension=AnalysisDimension.COMPLEXITY,
                            severity=IssueSeverity.WARNING,
                            message=f"函数 '{node.name}' 参数过多 ({param_count} 个，阈值 {self.max_parameters})",
                            line=node.lineno,
                            rule_id='too_many_parameters',
                            suggestion="考虑使用对象或字典封装参数"
                        ))
                    
                    # 检查嵌套深度
                    if nesting_depth > self.max_nesting_depth:
                        issues.append(CodeIssue(
                            dimension=AnalysisDimension.COMPLEXITY,
                            severity=IssueSeverity.WARNING,
                            message=f"函数 '{node.name}' 嵌套层级过深 ({nesting_depth} 层，阈值 {self.max_nesting_depth})",
                            line=node.lineno,
                            rule_id='deep_nesting',
                            suggestion="使用早返回(early return)或提取子函数来减少嵌套"
                        ))
                    
                    # 检查是否有文档字符串
                    if not ast.get_docstring(node):
                        issues.append(CodeIssue(
                            dimension=AnalysisDimension.COMPLEXITY,
                            severity=IssueSeverity.INFO,
                            message=f"函数 '{node.name}' 缺少文档字符串",
                            line=node.lineno,
                            rule_id='missing_docstring',
                            suggestion="添加文档字符串说明函数的用途、参数和返回值"
                        ))
                
                elif isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    metrics['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'method_count': len(methods),
                        'has_docstring': ast.get_docstring(node) is not None
                    })
            
            # 计算平均复杂度
            if metrics['functions']:
                complexities = [f['complexity'] for f in metrics['functions']]
                metrics['average_complexity'] = sum(complexities) / len(complexities)
                metrics['max_complexity'] = max(complexities)
            
        except SyntaxError as e:
            issues.append(CodeIssue(
                dimension=AnalysisDimension.COMPLEXITY,
                severity=IssueSeverity.CRITICAL,
                message=f"语法错误: {str(e)}",
                line=e.lineno or 0,
                rule_id='syntax_error'
            ))
        
        return issues, metrics
    
    def _analyze_bug_risk(self, content: str, lines: List[str]) -> List[CodeIssue]:
        """Bug风险分析"""
        issues = []
        
        bug_patterns = {
            'mutable_default': {
                'pattern': r'def\s+\w+\s*\([^)]*=\s*(\[\]|\{\}|\[\s*\]|\{\s*\})',
                'message': '使用可变对象作为默认参数值',
                'severity': 'warning',
                'suggestion': '使用 None 作为默认值，然后在函数内部初始化'
            },
            'bare_except': {
                'pattern': r'except\s*:',
                'message': '使用裸except捕获所有异常',
                'severity': 'warning',
                'suggestion': '明确指定要捕获的异常类型'
            },
            'assert_tuple': {
                'pattern': r'assert\s*\([^)]+,[^)]+\)',
                'message': 'assert语句使用元组（总是为True）',
                'severity': 'error',
                'suggestion': '移除assert后的括号，或使用逗号分隔条件和消息'
            },
            'comparison_to_none': {
                'pattern': r'==\s*None|!=\s*None',
                'message': '使用==或!=与None比较',
                'severity': 'info',
                'suggestion': '使用 is None 或 is not None'
            },
            'comparison_to_true': {
                'pattern': r'==\s*True|==\s*False',
                'message': '使用==与True/False比较',
                'severity': 'info',
                'suggestion': '直接使用布尔表达式或使用 is'
            },
            'string_concat_in_loop': {
                'pattern': r'for\s+.*:\s*\n\s+\w+\s*\+=\s*["\']',
                'message': '在循环中使用字符串拼接',
                'severity': 'warning',
                'suggestion': '使用列表收集字符串，最后用join连接'
            },
            'unused_variable': {
                'pattern': r'^\s*\w+\s*=\s*[^=].*$',
                'message': '可能未使用的变量赋值',
                'severity': 'info',
                'suggestion': '检查变量是否被使用，未使用则删除'
            },
            'shadowing_builtin': {
                'pattern': r'\b(list|dict|str|int|float|bool|set|tuple|type|id|input|print|len|range|map|filter|sum|min|max|open|file|dir|help|vars|locals|globals)\s*=',
                'message': '变量名覆盖了Python内置名称',
                'severity': 'warning',
                'suggestion': '使用不同的变量名避免覆盖内置名称'
            },
        }
        
        for rule_id, rule in bug_patterns.items():
            pattern = rule['pattern']
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    # 排除注释
                    if line.strip().startswith('#'):
                        continue
                    
                    issues.append(CodeIssue(
                        dimension=AnalysisDimension.BUG_RISK,
                        severity=IssueSeverity[rule['severity'].upper()],
                        message=rule['message'],
                        line=i,
                        code_snippet=line.strip()[:100],
                        rule_id=rule_id,
                        suggestion=rule.get('suggestion', '')
                    ))
        
        return issues
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)
            elif isinstance(child, ast.Assert):
                complexity += 1
        
        return complexity
    
    def _calculate_nesting_depth(self, node: ast.AST) -> int:
        """计算最大嵌套深度"""
        def get_depth(node, current_depth=0):
            max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                    child_depth = get_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_depth(child, current_depth)
                    max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        return get_depth(node)
    
    def _generate_summary(self, result: Dict) -> Dict[str, Any]:
        """生成分析摘要"""
        issues = result['issues']
        
        # 按维度统计
        by_dimension = {}
        for dim in AnalysisDimension:
            dim_issues = [i for i in issues if i.dimension == dim]
            by_dimension[dim.value] = {
                'total': len(dim_issues),
                'critical': len([i for i in dim_issues if i.severity == IssueSeverity.CRITICAL]),
                'error': len([i for i in dim_issues if i.severity == IssueSeverity.ERROR]),
                'warning': len([i for i in dim_issues if i.severity == IssueSeverity.WARNING]),
                'info': len([i for i in dim_issues if i.severity == IssueSeverity.INFO])
            }
        
        # 计算质量分数
        quality_score = 100.0
        for issue in issues:
            if issue.severity == IssueSeverity.CRITICAL:
                quality_score -= 20
            elif issue.severity == IssueSeverity.ERROR:
                quality_score -= 10
            elif issue.severity == IssueSeverity.WARNING:
                quality_score -= 3
            elif issue.severity == IssueSeverity.INFO:
                quality_score -= 0.5
        
        quality_score = max(0, min(100, quality_score))
        
        # 确定整体等级
        if quality_score >= 90:
            grade = 'A'
        elif quality_score >= 80:
            grade = 'B'
        elif quality_score >= 70:
            grade = 'C'
        elif quality_score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'total_issues': len(issues),
            'by_severity': {
                'critical': len([i for i in issues if i.severity == IssueSeverity.CRITICAL]),
                'error': len([i for i in issues if i.severity == IssueSeverity.ERROR]),
                'warning': len([i for i in issues if i.severity == IssueSeverity.WARNING]),
                'info': len([i for i in issues if i.severity == IssueSeverity.INFO])
            },
            'by_dimension': by_dimension,
            'quality_score': round(quality_score, 1),
            'grade': grade
        }
    
    def _format_text(self, result: Dict) -> str:
        """格式化为文本输出"""
        lines = []
        
        lines.append("=" * 60)
        lines.append("代码分析报告")
        lines.append("=" * 60)
        
        if result.get('filepath'):
            lines.append(f"文件: {result['filepath']}")
        
        # 摘要
        summary = result.get('summary', {})
        lines.append(f"\n📊 质量评分: {summary.get('quality_score', 0)}/100 (等级: {summary.get('grade', 'N/A')})")
        lines.append(f"📝 总问题数: {summary.get('total_issues', 0)}")
        
        by_severity = summary.get('by_severity', {})
        lines.append(f"   - 严重: {by_severity.get('critical', 0)}")
        lines.append(f"   - 错误: {by_severity.get('error', 0)}")
        lines.append(f"   - 警告: {by_severity.get('warning', 0)}")
        lines.append(f"   - 提示: {by_severity.get('info', 0)}")
        
        # 指标
        metrics = result.get('metrics', {})
        lines.append(f"\n📈 代码指标:")
        lines.append(f"   - 总行数: {metrics.get('total_lines', 0)}")
        lines.append(f"   - 代码行: {metrics.get('code_lines', 0)}")
        lines.append(f"   - 注释行: {metrics.get('comment_lines', 0)}")
        
        if 'complexity' in metrics:
            comp = metrics['complexity']
            lines.append(f"   - 平均复杂度: {comp.get('average_complexity', 0):.1f}")
            lines.append(f"   - 最大复杂度: {comp.get('max_complexity', 0)}")
        
        # 问题详情
        issues = result.get('issues', [])
        if issues:
            lines.append(f"\n🔍 问题详情:")
            
            # 按维度分组
            for dim in AnalysisDimension:
                dim_issues = [i for i in issues if i.dimension == dim]
                if dim_issues:
                    lines.append(f"\n  [{dim.value.upper()}]")
                    for issue in dim_issues[:10]:  # 限制显示数量
                        severity_icon = {'critical': '🔴', 'error': '🟠', 'warning': '🟡', 'info': '🔵'}.get(issue.severity.value, '⚪')
                        lines.append(f"    {severity_icon} 行 {issue.line}: {issue.message}")
                        if issue.suggestion:
                            lines.append(f"       💡 建议: {issue.suggestion}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def _format_markdown(self, result: Dict) -> str:
        """格式化为Markdown输出"""
        lines = []
        
        lines.append("# 代码分析报告\n")
        
        if result.get('filepath'):
            lines.append(f"**文件**: `{result['filepath']}`\n")
        
        # 摘要
        summary = result.get('summary', {})
        lines.append("## 📊 摘要\n")
        lines.append(f"| 指标 | 值 |")
        lines.append(f"|------|-----|")
        lines.append(f"| 质量评分 | {summary.get('quality_score', 0)}/100 |")
        lines.append(f"| 等级 | {summary.get('grade', 'N/A')} |")
        lines.append(f"| 总问题数 | {summary.get('total_issues', 0)} |")
        
        by_severity = summary.get('by_severity', {})
        lines.append(f"| 严重问题 | {by_severity.get('critical', 0)} |")
        lines.append(f"| 错误 | {by_severity.get('error', 0)} |")
        lines.append(f"| 警告 | {by_severity.get('warning', 0)} |")
        lines.append(f"| 提示 | {by_severity.get('info', 0)} |")
        lines.append("")
        
        # 问题详情
        issues = result.get('issues', [])
        if issues:
            lines.append("## 🔍 问题详情\n")
            
            for dim in AnalysisDimension:
                dim_issues = [i for i in issues if i.dimension == dim]
                if dim_issues:
                    lines.append(f"### {dim.value.title()}\n")
                    
                    for issue in dim_issues:
                        severity_badge = {'critical': '🔴', 'error': '🟠', 'warning': '🟡', 'info': '🔵'}.get(issue.severity.value, '⚪')
                        lines.append(f"- {severity_badge} **行 {issue.line}**: {issue.message}")
                        if issue.suggestion:
                            lines.append(f"  - 💡 *{issue.suggestion}*")
                    
                    lines.append("")
        
        return "\n".join(lines)
    
    def _analyze_directory(self, path: Path, dimensions: List[str], output_format: str) -> str:
        """分析整个目录"""
        results = []
        
        for file_path in path.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                result = self.analyze(content, str(file_path), dimensions)
                results.append(result)
            except Exception as e:
                results.append({
                    'filepath': str(file_path),
                    'error': str(e)
                })
        
        # 汇总结果
        total_issues = sum(len(r.get('issues', [])) for r in results)
        total_files = len(results)
        
        summary = {
            'directory': str(path),
            'total_files': total_files,
            'total_issues': total_issues,
            'files': results
        }
        
        if output_format == 'json':
            return json.dumps(summary, ensure_ascii=False, indent=2, default=lambda x: x.to_dict() if hasattr(x, 'to_dict') else str(x))
        else:
            lines = [f"目录分析: {path}", f"文件数: {total_files}", f"总问题数: {total_issues}", ""]
            for r in results:
                lines.append(f"\n--- {r.get('filepath', 'Unknown')} ---")
                if 'error' in r:
                    lines.append(f"错误: {r['error']}")
                else:
                    s = r.get('summary', {})
                    lines.append(f"评分: {s.get('quality_score', 0)}/100, 问题: {s.get('total_issues', 0)}")
            return "\n".join(lines)
    
    def _init_security_rules(self) -> Dict:
        """初始化安全规则"""
        return {
            'sql_injection_format': {
                'pattern': r'execute\s*\(\s*["\'].*%s',
                'message': 'SQL注入风险：使用字符串格式化构建SQL',
                'severity': 'critical',
                'suggestion': '使用参数化查询，如 cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'
            },
            'sql_injection_fstring': {
                'pattern': r'execute\s*\(\s*f["\']',
                'message': 'SQL注入风险：使用f-string构建SQL',
                'severity': 'critical',
                'suggestion': '使用参数化查询而不是f-string'
            },
            'sql_injection_concat': {
                'pattern': r'cursor\.execute\s*\([^,]+\+',
                'message': 'SQL注入风险：字符串拼接构建SQL',
                'severity': 'critical',
                'suggestion': '使用参数化查询而不是字符串拼接'
            },
            'command_injection_system': {
                'pattern': r'os\.system\s*\(',
                'message': '命令注入风险：使用os.system',
                'severity': 'critical',
                'suggestion': '使用subprocess模块并避免shell=True'
            },
            'command_injection_shell': {
                'pattern': r'subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True',
                'message': '命令注入风险：shell=True',
                'severity': 'critical',
                'suggestion': '避免使用shell=True，传入命令列表'
            },
            'code_injection_eval': {
                'pattern': r'\beval\s*\(',
                'message': '代码注入风险：使用eval',
                'severity': 'critical',
                'suggestion': '避免使用eval，使用ast.literal_eval或其他安全替代方案'
            },
            'code_injection_exec': {
                'pattern': r'\bexec\s*\(',
                'message': '代码注入风险：使用exec',
                'severity': 'critical',
                'suggestion': '避免使用exec，重新设计代码逻辑'
            },
            'hardcoded_password': {
                'pattern': r'password\s*=\s*["\'][^"\']+["\']',
                'message': '硬编码密码',
                'severity': 'error',
                'suggestion': '使用环境变量或配置文件存储敏感信息'
            },
            'hardcoded_api_key': {
                'pattern': r'api_key\s*=\s*["\'][^"\']+["\']',
                'message': '硬编码API密钥',
                'severity': 'error',
                'suggestion': '使用环境变量存储API密钥'
            },
            'hardcoded_secret': {
                'pattern': r'secret\s*=\s*["\'][^"\']+["\']',
                'message': '硬编码密钥',
                'severity': 'error',
                'suggestion': '使用环境变量或密钥管理服务'
            },
            'insecure_pickle': {
                'pattern': r'pickle\.loads?\s*\(',
                'message': '不安全的反序列化：使用pickle',
                'severity': 'error',
                'suggestion': '避免反序列化不可信数据，考虑使用json'
            },
            'insecure_yaml': {
                'pattern': r'yaml\.load\s*\([^)]*\)(?!\s*,\s*Loader)',
                'message': '不安全的YAML加载',
                'severity': 'error',
                'suggestion': '使用yaml.safe_load或指定Loader'
            },
            'path_traversal': {
                'pattern': r'\.\.\/',
                'message': '路径遍历风险：包含../',
                'severity': 'warning',
                'suggestion': '验证和清理文件路径，使用os.path.realpath'
            },
        }
    
    def _init_performance_rules(self) -> Dict:
        """初始化性能规则"""
        return {
            'inefficient_range_len': {
                'pattern': r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(',
                'message': '低效循环：使用range(len())而不是直接迭代',
                'severity': 'warning',
                'suggestion': '使用enumerate()或直接迭代序列'
            },
            'string_concat_loop': {
                'pattern': r'\+=\s*["\']',
                'message': '字符串拼接：可能在循环中使用+=拼接字符串',
                'severity': 'warning',
                'suggestion': '使用列表收集字符串，最后用join连接'
            },
            'global_usage': {
                'pattern': r'^\s*global\s+',
                'message': '使用global关键字',
                'severity': 'info',
                'suggestion': '考虑使用类或闭包来管理状态'
            },
            'repeated_attribute': {
                'pattern': r'(\w+\.\w+)\s*[^=].*\1',
                'message': '重复属性访问',
                'severity': 'info',
                'suggestion': '将重复访问的属性缓存到局部变量'
            },
            'list_append_loop': {
                'pattern': r'\.append\s*\([^)]+\)\s*$',
                'message': '循环中使用append',
                'severity': 'info',
                'suggestion': '考虑使用列表推导式替代循环append'
            },
        }
    
    def _init_style_rules(self) -> Dict:
        """初始化风格规则"""
        return {
            'multiple_statements': {
                'pattern': r';\s*\w+',
                'message': '同一行有多条语句',
                'severity': 'info',
                'suggestion': '每行只写一条语句'
            },
            'comparison_with_singleton': {
                'pattern': r'==\s*(True|False|None)|(\bTrue\b|\bFalse\b|\bNone\b)\s*==',
                'message': '与单例值使用==比较',
                'severity': 'info',
                'suggestion': '使用 is 或 is not 与 True/False/None 比较'
            },
            'wildcard_import': {
                'pattern': r'from\s+\w+\s+import\s+\*',
                'message': '使用通配符导入',
                'severity': 'warning',
                'suggestion': '明确导入需要的名称'
            },
            'bare_except': {
                'pattern': r'except\s*:',
                'message': '使用裸except',
                'severity': 'warning',
                'suggestion': '明确指定要捕获的异常类型'
            },
        }
