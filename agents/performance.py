import ast
import re
from typing import Dict, Any, List

from langchain_core.tools import tool
from pydantic import BaseModel, Field


# =============================================================================
# PERFORMANCE ENGINEER TOOLS
# =============================================================================

class PerformanceProfilerInput(BaseModel):
    code: str = Field(description="Code content to analyze for performance issues")
    language: str = Field(description="Programming language")


@tool("performance_profiler", args_schema=PerformanceProfilerInput)
def performance_profiler(code: str, language: str) -> Dict[str, Any]:
    """Analyze code for performance issues like nested loops and inefficient queries."""

    performance_issues = []

    def analyze_python_performance(code: str) -> List[Dict]:
        issues = []
        lines = code.split('\n')

        # Check for nested loops
        loop_depth = 0
        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith('for ') or stripped.startswith('while '):
                loop_depth += 1
                if loop_depth > 2:
                    issues.append({
                        "type": "nested_loops",
                        "line": i + 1,
                        "depth": loop_depth,
                        "message": f"Deeply nested loop (depth: {loop_depth}) may cause performance issues"
                    })

            # Reset depth when exiting loops (simplified logic)
            if not line.startswith(' ') and loop_depth > 0:
                loop_depth = 0

        # Check for inefficient database queries
        query_patterns = [
            (r'\.filter\(.*\)\.filter\(.*\)', "Multiple filter calls can be combined"),
            (r'for.*in.*\.all\(\):', "Using .all() in loop may be inefficient"),
            (r'SELECT.*FROM.*WHERE.*IN.*SELECT', "Subquery might be inefficient")
        ]

        for pattern, message in query_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append({
                    "type": "inefficient_query",
                    "line": line_num,
                    "message": message
                })

        return issues

    try:
        if language.lower() == 'python':
            performance_issues = analyze_python_performance(code)

        return {
            "status": "success",
            "issues": performance_issues,
            "performance_score": max(0, 100 - len(performance_issues) * 15)
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "issues": []}


class ComplexityAnalyzerInput(BaseModel):
    code: str = Field(description="Code content to analyze for complexity")
    language: str = Field(description="Programming language")


@tool("complexity_analyzer", args_schema=ComplexityAnalyzerInput)
def complexity_analyzer(code: str, language: str) -> Dict[str, Any]:
    """Calculate cyclomatic complexity and nesting depth."""

    def calculate_python_complexity(code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(code)

            complexity_data = {
                "cyclomatic_complexity": 1,  # Base complexity
                "max_nesting_depth": 0,
                "functions": []
            }

            class ComplexityVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.complexity = 1
                    self.nesting_depth = 0
                    self.max_depth = 0

                def visit_If(self, node):
                    self.complexity += 1
                    self.nesting_depth += 1
                    self.max_depth = max(self.max_depth, self.nesting_depth)
                    self.generic_visit(node)
                    self.nesting_depth -= 1

                def visit_For(self, node):
                    self.complexity += 1
                    self.nesting_depth += 1
                    self.max_depth = max(self.max_depth, self.nesting_depth)
                    self.generic_visit(node)
                    self.nesting_depth -= 1

                def visit_While(self, node):
                    self.complexity += 1
                    self.nesting_depth += 1
                    self.max_depth = max(self.max_depth, self.nesting_depth)
                    self.generic_visit(node)
                    self.nesting_depth -= 1

                def visit_FunctionDef(self, node):
                    func_visitor = ComplexityVisitor()
                    func_visitor.visit(node)

                    complexity_data["functions"].append({
                        "name": node.name,
                        "complexity": func_visitor.complexity,
                        "max_nesting": func_visitor.max_depth
                    })

            visitor = ComplexityVisitor()
            visitor.visit(tree)

            complexity_data["cyclomatic_complexity"] = visitor.complexity
            complexity_data["max_nesting_depth"] = visitor.max_depth

            return complexity_data

        except SyntaxError:
            return {
                "cyclomatic_complexity": 0,
                "max_nesting_depth": 0,
                "functions": [],
                "error": "Syntax error in code"
            }

    try:
        if language.lower() == 'python':
            complexity_data = calculate_python_complexity(code)
        else:
            # Simple fallback for other languages
            complexity_data = {
                "cyclomatic_complexity": code.count('if') + code.count('for') + code.count('while') + 1,
                "max_nesting_depth": 0,
                "functions": []
            }

        return {
            "status": "success",
            "complexity_data": complexity_data,
            "complexity_score": max(0, 100 - complexity_data["cyclomatic_complexity"] * 5)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

