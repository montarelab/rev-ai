"""
Software Engineer Tool Implementation for Multi-Agent Code Review System
Based on feedback from expert agents, implement fixes and improvements
"""

import re
import json
import ast
import os
from typing import Dict, List, Any, Optional, Tuple
from langchain_core.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
import subprocess
from pathlib import Path


# =============================================================================
# SOFTWARE ENGINEER TOOL
# =============================================================================

class CodeFixerInput(BaseModel):
    code: str = Field(description="Original code with issues")
    expert_feedback: Dict[str, Any] = Field(description="Combined feedback from all expert agents")
    language: str = Field(description="Programming language")


@tool("code_fix_implementer", args_schema=CodeFixerInput)
def code_fix_implementer(code: str, expert_feedback: Dict[str, Any], language: str) -> Dict[str, Any]:
    """
    Comprehensive code fixer that implements fixes based on feedback from all expert agents:
    - Security Engineer: Fix security vulnerabilities
    - Performance Engineer: Optimize performance issues
    - Software Architect: Apply refactoring suggestions
    - Technical Writer: Add missing documentation
    """

    fixed_code = code
    all_fixes_applied = []

    try:
        # =============================================================================
        # FIX SECURITY ISSUES
        # =============================================================================
        security_issues = expert_feedback.get('security', {}).get('issues', [])

        for issue in security_issues:
            message = issue.get('message', '').lower()
            line_num = issue.get('line', 0)

            if 'hardcoded password' in message:
                fixed_code = re.sub(
                    r'password\s*=\s*["\'][^"\']+["\']',
                    'password = os.environ.get("PASSWORD")',
                    fixed_code,
                    flags=re.IGNORECASE
                )
                all_fixes_applied.append({
                    "category": "security",
                    "issue": "Hardcoded password",
                    "fix": "Replaced with environment variable",
                    "line": line_num
                })

            elif 'hardcoded api key' in message:
                fixed_code = re.sub(
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    'api_key = os.environ.get("API_KEY")',
                    fixed_code,
                    flags=re.IGNORECASE
                )
                all_fixes_applied.append({
                    "category": "security",
                    "issue": "Hardcoded API key",
                    "fix": "Replaced with environment variable",
                    "line": line_num
                })

            elif 'sql injection' in message:
                if 'string concatenation' in message:
                    fixed_code = re.sub(
                        r'query\s*=\s*["\'].*\+.*["\']',
                        'query = "SELECT * FROM table WHERE id = %s"  # Use parameterized query',
                        fixed_code
                    )
                    all_fixes_applied.append({
                        "category": "security",
                        "issue": "SQL injection via string concatenation",
                        "fix": "Replaced with parameterized query",
                        "line": line_num
                    })

        # =============================================================================
        # FIX PERFORMANCE ISSUES
        # =============================================================================
        performance_issues = expert_feedback.get('performance', {}).get('issues', [])

        for issue in performance_issues:
            issue_type = issue.get('type', '')
            message = issue.get('message', '')
            line_num = issue.get('line', 0)

            if issue_type == 'nested_loops':
                depth = issue.get('depth', 0)
                lines = fixed_code.split('\n')
                if line_num - 1 < len(lines):
                    lines[line_num - 1] = f"    # OPTIMIZATION: Consider refactoring nested loop (depth: {depth})\n" + \
                                          lines[line_num - 1]
                    fixed_code = '\n'.join(lines)

                all_fixes_applied.append({
                    "category": "performance",
                    "issue": f"Nested loops with depth {depth}",
                    "fix": "Added optimization comment",
                    "line": line_num,
                    "suggestion": "Consider using list comprehension or breaking into functions"
                })

            elif 'multiple filter calls' in message.lower():
                fixed_code = re.sub(
                    r'\.filter\([^)]+\)\.filter\([^)]+\)',
                    '.filter(Q(condition1) & Q(condition2))',
                    fixed_code
                )
                all_fixes_applied.append({
                    "category": "performance",
                    "issue": "Multiple filter calls",
                    "fix": "Combined into single filter with Q objects",
                    "line": line_num
                })

            elif 'all()' in message.lower() and 'loop' in message.lower():
                fixed_code = re.sub(
                    r'for\s+\w+\s+in\s+\w+\.all\(\):',
                    'for item in queryset.iterator():  # Use iterator for large datasets',
                    fixed_code
                )
                all_fixes_applied.append({
                    "category": "performance",
                    "issue": "Using .all() in loop",
                    "fix": "Replaced with .iterator() for memory efficiency",
                    "line": line_num
                })

        # =============================================================================
        # APPLY REFACTORING SUGGESTIONS
        # =============================================================================
        refactoring_suggestions = expert_feedback.get('architecture', {}).get('suggestions', [])

        for suggestion in refactoring_suggestions:
            suggestion_type = suggestion.get('type', '')

            if suggestion_type == 'long_function':
                function_name = suggestion.get('function', '')
                lines_count = suggestion.get('lines', 0)

                # Add refactoring comment
                pattern = rf'def {re.escape(function_name)}\('
                replacement = f'def {function_name}(  # TODO: Refactor - {lines_count} lines, consider breaking into smaller functions'
                fixed_code = re.sub(pattern, replacement, fixed_code)

                all_fixes_applied.append({
                    "category": "architecture",
                    "issue": f"Long function '{function_name}' ({lines_count} lines)",
                    "fix": "Added refactoring TODO comment",
                    "suggestion": "Break into smaller, focused functions"
                })

            elif suggestion_type == 'duplicate_code':
                pattern = suggestion.get('pattern', '')
                occurrences = suggestion.get('occurrences', 0)

                # Add comment about duplicate code
                if pattern and len(pattern) > 10:
                    escaped_pattern = re.escape(pattern[:30])
                    fixed_code = re.sub(
                        escaped_pattern,
                        f'# TODO: Extract duplicate code into function - occurs {occurrences} times\n    {pattern[:30]}',
                        fixed_code,
                        count=1
                    )

                    all_fixes_applied.append({
                        "category": "architecture",
                        "issue": f"Duplicate code ({occurrences} occurrences)",
                        "fix": "Added TODO comment for code extraction",
                        "suggestion": "Extract repeated code into reusable function"
                    })

        # =============================================================================
        # ADD MISSING DOCUMENTATION
        # =============================================================================
        doc_analysis = expert_feedback.get('documentation', {}).get('documentation_analysis', {})
        functions_without_docs = doc_analysis.get('functions_without_docs', [])
        classes_without_docs = doc_analysis.get('classes_without_docs', [])

        # Add docstrings for functions without documentation
        for func_info in functions_without_docs:
            func_name = func_info.get('name', '')

            if func_name:
                # Find function definition and add docstring
                pattern = rf'def {re.escape(func_name)}\([^)]*\):'

                def add_docstring(match):
                    return match.group(
                        0) + f'\n    """\n    {func_name.replace("_", " ").title()}\n    \n    TODO: Add proper description, parameters, and return value documentation\n    """'

                fixed_code = re.sub(pattern, add_docstring, fixed_code)

                all_fixes_applied.append({
                    "category": "documentation",
                    "issue": f"Missing docstring for function '{func_name}'",
                    "fix": "Added placeholder docstring",
                    "suggestion": "Complete the docstring with proper description and parameters"
                })

        # Add docstrings for classes without documentation
        for class_info in classes_without_docs:
            class_name = class_info.get('name', '')

            if class_name:
                pattern = rf'class {re.escape(class_name)}[^:]*:'

                def add_class_docstring(match):
                    return match.group(
                        0) + f'\n    """\n    {class_name} class\n    \n    TODO: Add class description and usage examples\n    """'

                fixed_code = re.sub(pattern, add_class_docstring, fixed_code)

                all_fixes_applied.append({
                    "category": "documentation",
                    "issue": f"Missing docstring for class '{class_name}'",
                    "fix": "Added placeholder docstring",
                    "suggestion": "Complete the docstring with class description and usage"
                })

        # =============================================================================
        # ADD NECESSARY IMPORTS
        # =============================================================================
        needs_os_import = any('environment variable' in fix.get('fix', '') for fix in all_fixes_applied)
        needs_q_import = any('Q objects' in fix.get('fix', '') for fix in all_fixes_applied)

        imports_to_add = []
        if needs_os_import and 'import os' not in fixed_code:
            imports_to_add.append('import os')

        if needs_q_import and 'from django.db.models import Q' not in fixed_code:
            imports_to_add.append('from django.db.models import Q')

        if imports_to_add:
            fixed_code = '\n'.join(imports_to_add) + '\n' + fixed_code
            all_fixes_applied.append({
                "category": "imports",
                "issue": "Missing required imports",
                "fix": f"Added imports: {', '.join(imports_to_add)}",
                "line": 1
            })

        # =============================================================================
        # GENERATE SUMMARY
        # =============================================================================
        fixes_by_category = {}
        for fix in all_fixes_applied:
            category = fix.get('category', 'other')
            if category not in fixes_by_category:
                fixes_by_category[category] = []
            fixes_by_category[category].append(fix)

        return {
            "status": "success",
            "fixed_code": fixed_code,
            "total_fixes": len(all_fixes_applied),
            "fixes_by_category": fixes_by_category,
            "all_fixes": all_fixes_applied,
            "summary": {
                "security_fixes": len(fixes_by_category.get('security', [])),
                "performance_fixes": len(fixes_by_category.get('performance', [])),
                "architecture_fixes": len(fixes_by_category.get('architecture', [])),
                "documentation_fixes": len(fixes_by_category.get('documentation', [])),
                "import_fixes": len(fixes_by_category.get('imports', []))
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fixed_code": code,
            "total_fixes": 0,
            "all_fixes": []
        }