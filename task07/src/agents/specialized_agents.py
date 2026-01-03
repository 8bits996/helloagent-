"""
专门化智能体 - 实现各种专门功能的智能体
"""

import os
import re
import ast
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from .multi_agent_coordinator import (
    BaseSpecializedAgent,
    TaskRequest,
    AgentResponse,
    TaskStatus,
    AgentCapability
)


class CodeAnalysisAgent(BaseSpecializedAgent):
    """代码分析智能体 - 负责代码质量分析"""
    
    def __init__(self, agent_id: str = "code_analyzer"):
        super().__init__(
            agent_id=agent_id,
            name="代码分析专家",
            capabilities=[
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.REFACTORING
            ]
        )
        
        # 代码质量规则
        self.quality_rules = {
            'max_line_length': 120,
            'max_function_length': 50,
            'max_complexity': 10,
            'max_parameters': 5,
        }
    
    def process(self, task: TaskRequest) -> AgentResponse:
        """处理代码分析任务"""
        try:
            code_path = task.context.get('path', '')
            code_content = task.context.get('content', '')
            
            if code_path and os.path.exists(code_path):
                with open(code_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            
            if not code_content:
                return AgentResponse(
                    task_id=task.id,
                    agent_id=self.agent_id,
                    status=TaskStatus.FAILED,
                    error="没有提供代码内容或有效的代码路径"
                )
            
            # 执行分析
            analysis_result = self._analyze_code(code_content, code_path)
            
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.COMPLETED,
                result=analysis_result,
                confidence=0.9,
                suggestions=analysis_result.get('suggestions', [])
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    def _analyze_code(self, code: str, filepath: str = "") -> Dict[str, Any]:
        """分析代码质量"""
        lines = code.split('\n')
        
        result = {
            'filepath': filepath,
            'metrics': {},
            'issues': [],
            'suggestions': [],
            'summary': {}
        }
        
        # 基础指标
        result['metrics']['total_lines'] = len(lines)
        result['metrics']['code_lines'] = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        result['metrics']['comment_lines'] = len([l for l in lines if l.strip().startswith('#')])
        result['metrics']['blank_lines'] = len([l for l in lines if not l.strip()])
        
        # 检查行长度
        long_lines = [(i+1, len(l)) for i, l in enumerate(lines) if len(l) > self.quality_rules['max_line_length']]
        if long_lines:
            result['issues'].append({
                'type': 'line_length',
                'severity': 'warning',
                'message': f"发现 {len(long_lines)} 行超过 {self.quality_rules['max_line_length']} 字符",
                'locations': long_lines[:5]
            })
        
        # Python特定分析
        if filepath.endswith('.py') or self._is_python_code(code):
            python_analysis = self._analyze_python(code)
            result['metrics'].update(python_analysis['metrics'])
            result['issues'].extend(python_analysis['issues'])
            result['suggestions'].extend(python_analysis['suggestions'])
        
        # 生成摘要
        result['summary'] = {
            'quality_score': self._calculate_quality_score(result),
            'total_issues': len(result['issues']),
            'critical_issues': len([i for i in result['issues'] if i.get('severity') == 'critical']),
            'warnings': len([i for i in result['issues'] if i.get('severity') == 'warning'])
        }
        
        return result
    
    def _is_python_code(self, code: str) -> bool:
        """检测是否为Python代码"""
        python_indicators = ['def ', 'class ', 'import ', 'from ', 'if __name__']
        return any(indicator in code for indicator in python_indicators)
    
    def _analyze_python(self, code: str) -> Dict[str, Any]:
        """Python代码专门分析"""
        result = {'metrics': {}, 'issues': [], 'suggestions': []}
        
        try:
            tree = ast.parse(code)
            
            # 统计函数和类
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            result['metrics']['function_count'] = len(functions)
            result['metrics']['class_count'] = len(classes)
            
            # 分析每个函数
            for func in functions:
                func_analysis = self._analyze_function(func, code)
                if func_analysis['issues']:
                    result['issues'].extend(func_analysis['issues'])
                if func_analysis['suggestions']:
                    result['suggestions'].extend(func_analysis['suggestions'])
            
            # 检查导入
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            result['metrics']['import_count'] = len(imports)
            
            # 检查未使用的导入（简化版）
            import_names = set()
            for imp in imports:
                if isinstance(imp, ast.Import):
                    for alias in imp.names:
                        import_names.add(alias.asname or alias.name.split('.')[0])
                elif isinstance(imp, ast.ImportFrom):
                    for alias in imp.names:
                        import_names.add(alias.asname or alias.name)
            
        except SyntaxError as e:
            result['issues'].append({
                'type': 'syntax_error',
                'severity': 'critical',
                'message': f"语法错误: {str(e)}",
                'line': e.lineno
            })
        
        return result
    
    def _analyze_function(self, func: ast.FunctionDef, code: str) -> Dict[str, Any]:
        """分析单个函数"""
        result = {'issues': [], 'suggestions': []}
        
        # 计算函数行数
        func_lines = func.end_lineno - func.lineno + 1 if hasattr(func, 'end_lineno') else 0
        
        if func_lines > self.quality_rules['max_function_length']:
            result['issues'].append({
                'type': 'function_length',
                'severity': 'warning',
                'message': f"函数 '{func.name}' 过长 ({func_lines} 行)",
                'line': func.lineno
            })
            result['suggestions'].append(f"考虑将函数 '{func.name}' 拆分为更小的函数")
        
        # 检查参数数量
        param_count = len(func.args.args)
        if param_count > self.quality_rules['max_parameters']:
            result['issues'].append({
                'type': 'too_many_parameters',
                'severity': 'warning',
                'message': f"函数 '{func.name}' 参数过多 ({param_count} 个)",
                'line': func.lineno
            })
            result['suggestions'].append(f"考虑使用对象或字典封装函数 '{func.name}' 的参数")
        
        # 计算圈复杂度
        complexity = self._calculate_complexity(func)
        if complexity > self.quality_rules['max_complexity']:
            result['issues'].append({
                'type': 'high_complexity',
                'severity': 'warning',
                'message': f"函数 '{func.name}' 圈复杂度过高 ({complexity})",
                'line': func.lineno
            })
            result['suggestions'].append(f"简化函数 '{func.name}' 的逻辑，降低复杂度")
        
        # 检查是否有文档字符串
        if not ast.get_docstring(func):
            result['issues'].append({
                'type': 'missing_docstring',
                'severity': 'info',
                'message': f"函数 '{func.name}' 缺少文档字符串",
                'line': func.lineno
            })
        
        return result
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_quality_score(self, analysis: Dict) -> float:
        """计算代码质量分数（0-100）"""
        score = 100.0
        
        for issue in analysis['issues']:
            severity = issue.get('severity', 'info')
            if severity == 'critical':
                score -= 20
            elif severity == 'warning':
                score -= 5
            else:
                score -= 1
        
        return max(0, min(100, score))


class SecurityAuditAgent(BaseSpecializedAgent):
    """安全审计智能体 - 负责代码安全检查"""
    
    def __init__(self, agent_id: str = "security_auditor"):
        super().__init__(
            agent_id=agent_id,
            name="安全审计专家",
            capabilities=[AgentCapability.SECURITY_AUDIT]
        )
        
        # 安全规则
        self.security_patterns = {
            'sql_injection': [
                (r'execute\s*\(\s*["\'].*%s', 'SQL注入风险：使用字符串格式化构建SQL'),
                (r'execute\s*\(\s*f["\']', 'SQL注入风险：使用f-string构建SQL'),
                (r'cursor\.execute\s*\([^,]+\+', 'SQL注入风险：字符串拼接构建SQL'),
            ],
            'command_injection': [
                (r'os\.system\s*\(', '命令注入风险：使用os.system'),
                (r'subprocess\.call\s*\([^,]*shell\s*=\s*True', '命令注入风险：shell=True'),
                (r'eval\s*\(', '代码注入风险：使用eval'),
                (r'exec\s*\(', '代码注入风险：使用exec'),
            ],
            'hardcoded_secrets': [
                (r'password\s*=\s*["\'][^"\']+["\']', '硬编码密码'),
                (r'api_key\s*=\s*["\'][^"\']+["\']', '硬编码API密钥'),
                (r'secret\s*=\s*["\'][^"\']+["\']', '硬编码密钥'),
                (r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']', '硬编码令牌'),
            ],
            'path_traversal': [
                (r'open\s*\([^)]*\+[^)]*\)', '路径遍历风险：动态构建文件路径'),
                (r'\.\./', '路径遍历风险：包含../'),
            ],
            'insecure_deserialization': [
                (r'pickle\.loads?\s*\(', '不安全的反序列化：使用pickle'),
                (r'yaml\.load\s*\([^,)]*\)', '不安全的YAML加载：未使用safe_load'),
            ],
        }
    
    def process(self, task: TaskRequest) -> AgentResponse:
        """处理安全审计任务"""
        try:
            code_path = task.context.get('path', '')
            code_content = task.context.get('content', '')
            
            if code_path and os.path.exists(code_path):
                with open(code_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            
            if not code_content:
                return AgentResponse(
                    task_id=task.id,
                    agent_id=self.agent_id,
                    status=TaskStatus.FAILED,
                    error="没有提供代码内容或有效的代码路径"
                )
            
            # 执行安全审计
            audit_result = self._audit_code(code_content, code_path)
            
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.COMPLETED,
                result=audit_result,
                confidence=0.85,
                suggestions=audit_result.get('recommendations', [])
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    def _audit_code(self, code: str, filepath: str = "") -> Dict[str, Any]:
        """执行代码安全审计"""
        result = {
            'filepath': filepath,
            'vulnerabilities': [],
            'risk_level': 'low',
            'recommendations': [],
            'summary': {}
        }
        
        lines = code.split('\n')
        
        # 检查各类安全问题
        for category, patterns in self.security_patterns.items():
            for pattern, description in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerability = {
                            'category': category,
                            'description': description,
                            'line': i,
                            'code': line.strip()[:100],
                            'severity': self._get_severity(category)
                        }
                        result['vulnerabilities'].append(vulnerability)
                        
                        # 添加修复建议
                        recommendation = self._get_recommendation(category)
                        if recommendation and recommendation not in result['recommendations']:
                            result['recommendations'].append(recommendation)
        
        # 计算风险等级
        result['risk_level'] = self._calculate_risk_level(result['vulnerabilities'])
        
        # 生成摘要
        result['summary'] = {
            'total_vulnerabilities': len(result['vulnerabilities']),
            'critical': len([v for v in result['vulnerabilities'] if v['severity'] == 'critical']),
            'high': len([v for v in result['vulnerabilities'] if v['severity'] == 'high']),
            'medium': len([v for v in result['vulnerabilities'] if v['severity'] == 'medium']),
            'low': len([v for v in result['vulnerabilities'] if v['severity'] == 'low']),
            'risk_level': result['risk_level']
        }
        
        return result
    
    def _get_severity(self, category: str) -> str:
        """获取漏洞严重程度"""
        severity_map = {
            'sql_injection': 'critical',
            'command_injection': 'critical',
            'hardcoded_secrets': 'high',
            'path_traversal': 'high',
            'insecure_deserialization': 'high',
        }
        return severity_map.get(category, 'medium')
    
    def _get_recommendation(self, category: str) -> str:
        """获取修复建议"""
        recommendations = {
            'sql_injection': '使用参数化查询或ORM来防止SQL注入',
            'command_injection': '避免使用shell=True，使用subprocess.run并传入列表参数',
            'hardcoded_secrets': '使用环境变量或配置文件存储敏感信息',
            'path_traversal': '验证和清理用户输入的文件路径，使用os.path.realpath',
            'insecure_deserialization': '使用安全的序列化方法，如json，或使用yaml.safe_load',
        }
        return recommendations.get(category, '')
    
    def _calculate_risk_level(self, vulnerabilities: List[Dict]) -> str:
        """计算整体风险等级"""
        if not vulnerabilities:
            return 'low'
        
        critical_count = len([v for v in vulnerabilities if v['severity'] == 'critical'])
        high_count = len([v for v in vulnerabilities if v['severity'] == 'high'])
        
        if critical_count > 0:
            return 'critical'
        elif high_count >= 3:
            return 'high'
        elif high_count > 0:
            return 'medium'
        else:
            return 'low'


class PerformanceOptimizerAgent(BaseSpecializedAgent):
    """性能优化智能体 - 负责性能分析和优化建议"""
    
    def __init__(self, agent_id: str = "performance_optimizer"):
        super().__init__(
            agent_id=agent_id,
            name="性能优化专家",
            capabilities=[AgentCapability.PERFORMANCE_OPTIMIZATION]
        )
        
        # 性能反模式
        self.anti_patterns = {
            'inefficient_loop': [
                (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', '低效循环：使用range(len())而不是直接迭代'),
                (r'\+\s*=\s*["\']', '字符串拼接：在循环中使用+=拼接字符串'),
            ],
            'repeated_computation': [
                (r'for.*:\s*\n.*len\s*\(', '重复计算：在循环中重复调用len()'),
            ],
            'global_variable': [
                (r'^global\s+', '全局变量：过度使用global关键字'),
            ],
            'nested_loop': [
                (r'for\s+.*:\s*\n\s+for\s+.*:', '嵌套循环：可能存在O(n²)复杂度'),
            ],
            'list_comprehension': [
                (r'\.append\s*\([^)]+\)\s*$', '可优化：考虑使用列表推导式替代append'),
            ],
        }
    
    def process(self, task: TaskRequest) -> AgentResponse:
        """处理性能优化任务"""
        try:
            code_path = task.context.get('path', '')
            code_content = task.context.get('content', '')
            
            if code_path and os.path.exists(code_path):
                with open(code_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            
            if not code_content:
                return AgentResponse(
                    task_id=task.id,
                    agent_id=self.agent_id,
                    status=TaskStatus.FAILED,
                    error="没有提供代码内容或有效的代码路径"
                )
            
            # 执行性能分析
            perf_result = self._analyze_performance(code_content, code_path)
            
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.COMPLETED,
                result=perf_result,
                confidence=0.8,
                suggestions=perf_result.get('optimizations', [])
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    def _analyze_performance(self, code: str, filepath: str = "") -> Dict[str, Any]:
        """分析代码性能"""
        result = {
            'filepath': filepath,
            'issues': [],
            'optimizations': [],
            'complexity_analysis': {},
            'summary': {}
        }
        
        lines = code.split('\n')
        
        # 检查性能反模式
        for category, patterns in self.anti_patterns.items():
            for pattern, description in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.MULTILINE):
                        issue = {
                            'category': category,
                            'description': description,
                            'line': i,
                            'code': line.strip()[:100],
                            'impact': self._get_impact(category)
                        }
                        result['issues'].append(issue)
                        
                        optimization = self._get_optimization(category)
                        if optimization and optimization not in result['optimizations']:
                            result['optimizations'].append(optimization)
        
        # Python特定分析
        if filepath.endswith('.py') or 'def ' in code:
            result['complexity_analysis'] = self._analyze_complexity(code)
        
        # 生成摘要
        result['summary'] = {
            'total_issues': len(result['issues']),
            'high_impact': len([i for i in result['issues'] if i['impact'] == 'high']),
            'medium_impact': len([i for i in result['issues'] if i['impact'] == 'medium']),
            'optimization_suggestions': len(result['optimizations'])
        }
        
        return result
    
    def _get_impact(self, category: str) -> str:
        """获取性能影响程度"""
        impact_map = {
            'inefficient_loop': 'medium',
            'repeated_computation': 'high',
            'global_variable': 'low',
            'nested_loop': 'high',
            'list_comprehension': 'low',
        }
        return impact_map.get(category, 'medium')
    
    def _get_optimization(self, category: str) -> str:
        """获取优化建议"""
        optimizations = {
            'inefficient_loop': '使用enumerate()或直接迭代序列，避免range(len())',
            'repeated_computation': '将循环不变的计算移到循环外部',
            'global_variable': '考虑使用类或闭包来管理状态',
            'nested_loop': '考虑使用字典查找或集合操作来降低复杂度',
            'list_comprehension': '使用列表推导式替代循环append，提高性能和可读性',
        }
        return optimizations.get(category, '')
    
    def _analyze_complexity(self, code: str) -> Dict[str, Any]:
        """分析代码复杂度"""
        try:
            tree = ast.parse(code)
            
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'complexity': complexity,
                        'rating': 'high' if complexity > 10 else 'medium' if complexity > 5 else 'low'
                    })
            
            return {
                'functions': functions,
                'average_complexity': sum(f['complexity'] for f in functions) / len(functions) if functions else 0,
                'max_complexity': max((f['complexity'] for f in functions), default=0)
            }
            
        except SyntaxError:
            return {'error': '无法解析代码'}
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


class DocumentationAgent(BaseSpecializedAgent):
    """文档生成智能体 - 负责生成代码文档和报告"""
    
    def __init__(self, agent_id: str = "documentation_agent"):
        super().__init__(
            agent_id=agent_id,
            name="文档生成专家",
            capabilities=[AgentCapability.DOCUMENTATION]
        )
    
    def process(self, task: TaskRequest) -> AgentResponse:
        """处理文档生成任务"""
        try:
            context = task.context
            report_type = context.get('report_type', 'code_review')
            
            if report_type == 'code_review':
                result = self._generate_code_review_report(context)
            elif report_type == 'api_doc':
                result = self._generate_api_documentation(context)
            else:
                result = self._generate_general_report(context)
            
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.COMPLETED,
                result=result,
                confidence=0.9
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    def _generate_code_review_report(self, context: Dict) -> Dict[str, Any]:
        """生成代码审查报告"""
        analysis_result = context.get('analysis_result', {})
        security_result = context.get('security_result', {})
        performance_result = context.get('performance_result', {})
        
        report = {
            'title': '代码审查报告',
            'generated_at': datetime.now().isoformat(),
            'filepath': context.get('path', ''),
            'sections': []
        }
        
        # 概述部分
        report['sections'].append({
            'title': '概述',
            'content': self._generate_overview(analysis_result, security_result, performance_result)
        })
        
        # 代码质量部分
        if analysis_result:
            report['sections'].append({
                'title': '代码质量分析',
                'content': self._format_analysis_section(analysis_result)
            })
        
        # 安全审计部分
        if security_result:
            report['sections'].append({
                'title': '安全审计',
                'content': self._format_security_section(security_result)
            })
        
        # 性能分析部分
        if performance_result:
            report['sections'].append({
                'title': '性能分析',
                'content': self._format_performance_section(performance_result)
            })
        
        # 建议部分
        report['sections'].append({
            'title': '改进建议',
            'content': self._generate_recommendations(analysis_result, security_result, performance_result)
        })
        
        return report
    
    def _generate_overview(self, analysis: Dict, security: Dict, performance: Dict) -> str:
        """生成概述"""
        lines = []
        
        if analysis:
            quality_score = analysis.get('summary', {}).get('quality_score', 0)
            lines.append(f"代码质量评分: {quality_score:.1f}/100")
        
        if security:
            risk_level = security.get('risk_level', 'unknown')
            vuln_count = security.get('summary', {}).get('total_vulnerabilities', 0)
            lines.append(f"安全风险等级: {risk_level.upper()}")
            lines.append(f"发现安全漏洞: {vuln_count} 个")
        
        if performance:
            issue_count = performance.get('summary', {}).get('total_issues', 0)
            lines.append(f"性能问题: {issue_count} 个")
        
        return '\n'.join(lines)
    
    def _format_analysis_section(self, analysis: Dict) -> str:
        """格式化代码分析部分"""
        lines = []
        
        metrics = analysis.get('metrics', {})
        lines.append(f"总行数: {metrics.get('total_lines', 0)}")
        lines.append(f"代码行: {metrics.get('code_lines', 0)}")
        lines.append(f"注释行: {metrics.get('comment_lines', 0)}")
        lines.append(f"函数数: {metrics.get('function_count', 0)}")
        lines.append(f"类数量: {metrics.get('class_count', 0)}")
        
        issues = analysis.get('issues', [])
        if issues:
            lines.append(f"\n发现问题 ({len(issues)} 个):")
            for issue in issues[:10]:
                lines.append(f"  - [{issue.get('severity', 'info')}] {issue.get('message', '')} (行 {issue.get('line', '?')})")
        
        return '\n'.join(lines)
    
    def _format_security_section(self, security: Dict) -> str:
        """格式化安全审计部分"""
        lines = []
        
        summary = security.get('summary', {})
        lines.append(f"风险等级: {security.get('risk_level', 'unknown').upper()}")
        lines.append(f"严重漏洞: {summary.get('critical', 0)} 个")
        lines.append(f"高危漏洞: {summary.get('high', 0)} 个")
        lines.append(f"中危漏洞: {summary.get('medium', 0)} 个")
        
        vulnerabilities = security.get('vulnerabilities', [])
        if vulnerabilities:
            lines.append(f"\n漏洞详情:")
            for vuln in vulnerabilities[:10]:
                lines.append(f"  - [{vuln.get('severity', 'unknown')}] {vuln.get('description', '')} (行 {vuln.get('line', '?')})")
        
        return '\n'.join(lines)
    
    def _format_performance_section(self, performance: Dict) -> str:
        """格式化性能分析部分"""
        lines = []
        
        complexity = performance.get('complexity_analysis', {})
        if complexity and 'average_complexity' in complexity:
            lines.append(f"平均圈复杂度: {complexity['average_complexity']:.1f}")
            lines.append(f"最大圈复杂度: {complexity['max_complexity']}")
        
        issues = performance.get('issues', [])
        if issues:
            lines.append(f"\n性能问题 ({len(issues)} 个):")
            for issue in issues[:10]:
                lines.append(f"  - [{issue.get('impact', 'medium')}] {issue.get('description', '')} (行 {issue.get('line', '?')})")
        
        return '\n'.join(lines)
    
    def _generate_recommendations(self, analysis: Dict, security: Dict, performance: Dict) -> str:
        """生成改进建议"""
        recommendations = []
        
        # 从各个分析结果收集建议
        if analysis:
            recommendations.extend(analysis.get('suggestions', []))
        
        if security:
            recommendations.extend(security.get('recommendations', []))
        
        if performance:
            recommendations.extend(performance.get('optimizations', []))
        
        # 去重
        recommendations = list(dict.fromkeys(recommendations))
        
        if recommendations:
            return '\n'.join(f"  {i+1}. {rec}" for i, rec in enumerate(recommendations[:15]))
        else:
            return "暂无具体建议"
    
    def _generate_api_documentation(self, context: Dict) -> Dict[str, Any]:
        """生成API文档"""
        code = context.get('content', '')
        
        try:
            tree = ast.parse(code)
            
            doc = {
                'title': 'API文档',
                'generated_at': datetime.now().isoformat(),
                'modules': [],
                'classes': [],
                'functions': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_doc = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or '',
                        'methods': []
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_doc['methods'].append({
                                'name': item.name,
                                'docstring': ast.get_docstring(item) or '',
                                'parameters': [arg.arg for arg in item.args.args]
                            })
                    
                    doc['classes'].append(class_doc)
                
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    doc['functions'].append({
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or '',
                        'parameters': [arg.arg for arg in node.args.args]
                    })
            
            return doc
            
        except SyntaxError:
            return {'error': '无法解析代码'}
    
    def _generate_general_report(self, context: Dict) -> Dict[str, Any]:
        """生成通用报告"""
        return {
            'title': '分析报告',
            'generated_at': datetime.now().isoformat(),
            'content': context.get('content', ''),
            'metadata': context.get('metadata', {})
        }


class TestingAgent(BaseSpecializedAgent):
    """测试智能体 - 负责测试相关任务"""
    
    def __init__(self, agent_id: str = "testing_agent"):
        super().__init__(
            agent_id=agent_id,
            name="测试专家",
            capabilities=[AgentCapability.TESTING]
        )
    
    def process(self, task: TaskRequest) -> AgentResponse:
        """处理测试任务"""
        try:
            context = task.context
            test_type = context.get('test_type', 'unit')
            
            if test_type == 'unit':
                result = self._generate_unit_tests(context)
            elif test_type == 'coverage':
                result = self._analyze_test_coverage(context)
            else:
                result = self._generate_test_suggestions(context)
            
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.COMPLETED,
                result=result,
                confidence=0.85
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    def _generate_unit_tests(self, context: Dict) -> Dict[str, Any]:
        """生成单元测试建议"""
        code = context.get('content', '')
        
        try:
            tree = ast.parse(code)
            
            test_suggestions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 为每个函数生成测试建议
                    test_suggestions.append({
                        'function': node.name,
                        'test_cases': self._suggest_test_cases(node),
                        'test_template': self._generate_test_template(node)
                    })
            
            return {
                'test_suggestions': test_suggestions,
                'total_functions': len(test_suggestions),
                'framework': 'pytest'
            }
            
        except SyntaxError:
            return {'error': '无法解析代码'}
    
    def _suggest_test_cases(self, func: ast.FunctionDef) -> List[str]:
        """建议测试用例"""
        cases = [
            f"test_{func.name}_normal_input",
            f"test_{func.name}_edge_cases",
            f"test_{func.name}_invalid_input",
        ]
        
        # 检查是否有参数
        if func.args.args:
            cases.append(f"test_{func.name}_missing_arguments")
        
        return cases
    
    def _generate_test_template(self, func: ast.FunctionDef) -> str:
        """生成测试模板"""
        params = [arg.arg for arg in func.args.args if arg.arg != 'self']
        param_str = ', '.join(params) if params else ''
        
        template = f'''
def test_{func.name}_basic():
    """测试 {func.name} 的基本功能"""
    # Arrange
    # TODO: 设置测试数据
    
    # Act
    result = {func.name}({param_str})
    
    # Assert
    # TODO: 添加断言
    assert result is not None
'''
        return template.strip()
    
    def _analyze_test_coverage(self, context: Dict) -> Dict[str, Any]:
        """分析测试覆盖率（简化版）"""
        code = context.get('content', '')
        test_code = context.get('test_content', '')
        
        try:
            tree = ast.parse(code)
            
            # 获取所有函数
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            # 检查测试代码中是否有对应的测试
            tested_functions = []
            if test_code:
                for func in functions:
                    if f'test_{func}' in test_code or func in test_code:
                        tested_functions.append(func)
            
            coverage = len(tested_functions) / len(functions) * 100 if functions else 0
            
            return {
                'total_functions': len(functions),
                'tested_functions': len(tested_functions),
                'untested_functions': [f for f in functions if f not in tested_functions],
                'coverage_percentage': coverage
            }
            
        except SyntaxError:
            return {'error': '无法解析代码'}
    
    def _generate_test_suggestions(self, context: Dict) -> Dict[str, Any]:
        """生成测试建议"""
        return {
            'suggestions': [
                '确保每个公共函数都有对应的单元测试',
                '测试边界条件和异常情况',
                '使用mock对象隔离外部依赖',
                '保持测试的独立性和可重复性',
                '使用参数化测试减少重复代码'
            ]
        }


# 智能体工厂
class AgentFactory:
    """智能体工厂 - 创建和管理智能体实例"""
    
    _agent_classes = {
        'code_analysis': CodeAnalysisAgent,
        'security_audit': SecurityAuditAgent,
        'performance_optimization': PerformanceOptimizerAgent,
        'documentation': DocumentationAgent,
        'testing': TestingAgent,
    }
    
    @classmethod
    def create(cls, agent_type: str, agent_id: Optional[str] = None) -> BaseSpecializedAgent:
        """创建智能体实例"""
        if agent_type not in cls._agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agent_classes[agent_type]
        return agent_class(agent_id=agent_id) if agent_id else agent_class()
    
    @classmethod
    def create_all(cls) -> List[BaseSpecializedAgent]:
        """创建所有类型的智能体"""
        return [cls.create(agent_type) for agent_type in cls._agent_classes]
    
    @classmethod
    def register_agent_class(cls, agent_type: str, agent_class: type):
        """注册新的智能体类"""
        cls._agent_classes[agent_type] = agent_class
    
    @classmethod
    def available_types(cls) -> List[str]:
        """获取可用的智能体类型"""
        return list(cls._agent_classes.keys())
