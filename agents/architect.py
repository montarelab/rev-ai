# =============================================================================
# SOFTWARE ARCHITECT TOOLS
# =============================================================================
import re
from typing import Dict, Any, List

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class CodeFormatterInput(BaseModel):
    code: str = Field(description="Code content to format")
    language: str = Field(description="Programming language (python, javascript, java)")


@tool("code_formatter", args_schema=CodeFormatterInput)
def code_formatter(code: str, language: str) -> Dict[str, Any]:
    """Format code for proper styling, spacing, and indentation."""

    def format_python(code: str) -> str:
        """Basic Python formatting"""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue

            # Decrease indent for closing statements
            if stripped.startswith(('return', 'break', 'continue', 'pass')):
                if indent_level > 0:
                    indent_level -= 1
            elif stripped.startswith(('else:', 'elif', 'except:', 'finally:')):
                if indent_level > 0:
                    indent_level -= 1

            # Add proper indentation
            formatted_line = '    ' * indent_level + stripped
            formatted_lines.append(formatted_line)

            # Increase indent for opening statements
            if stripped.endswith(':') and not stripped.startswith(('return', 'break', 'continue', 'pass')):
                indent_level += 1

        return '\n'.join(formatted_lines)

    def format_javascript(code: str) -> str:
        """Basic JavaScript formatting"""
        # Simple formatting rules
        formatted = re.sub(r'{\s*', '{\n    ', code)
        formatted = re.sub(r';\s*', ';\n    ', formatted)
        formatted = re.sub(r'}\s*', '\n}\n', formatted)
        return formatted

    try:
        if language.lower() == 'python':
            formatted_code = format_python(code)
        elif language.lower() in ['javascript', 'js']:
            formatted_code = format_javascript(code)
        else:
            formatted_code = code  # Return as-is for unsupported languages

        return {
            "status": "success",
            "formatted_code": formatted_code,
            "issues_fixed": ["indentation", "spacing"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "formatted_code": code
        }


class RefactorToolInput(BaseModel):
    code: str = Field(description="Code content to analyze for refactoring")
    language: str = Field(description="Programming language")


@tool("refactor_analyzer", args_schema=RefactorToolInput)
def refactor_analyzer(code: str, language: str) -> Dict[str, Any]:
    """Analyze code and suggest improvements and restructuring."""

    suggestions = []

    def analyze_python(code: str) -> List[Dict]:
        python_suggestions = []
        lines = code.split('\n')

        # Check for long functions
        current_function = None
        function_line_count = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detect function start
            if stripped.startswith('def '):
                if current_function and function_line_count > 20:
                    python_suggestions.append({
                        "type": "long_function",
                        "function": current_function,
                        "lines": function_line_count,
                        "suggestion": f"Function '{current_function}' is {function_line_count} lines long. Consider breaking it into smaller functions."
                    })

                current_function = stripped.split('(')[0].replace('def ', '')
                function_line_count = 0
            elif current_function:
                function_line_count += 1

        # Check last function
        if current_function and function_line_count > 20:
            python_suggestions.append({
                "type": "long_function",
                "function": current_function,
                "lines": function_line_count,
                "suggestion": f"Function '{current_function}' is {function_line_count} lines long. Consider breaking it into smaller functions."
            })

        # Duplicate code detection (simple pattern matching)
        line_occurrences = {}
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 10 and not stripped.startswith('#'):
                line_occurrences[stripped] = line_occurrences.get(stripped, 0) + 1

        for line, count in line_occurrences.items():
            if count > 2:
                python_suggestions.append({
                    "type": "duplicate_code",
                    "pattern": line[:50] + "..." if len(line) > 50 else line,
                    "occurrences": count,
                    "suggestion": f"Consider extracting this repeated code into a function."
                })

        return python_suggestions

    try:
        if language.lower() == 'python':
            suggestions = analyze_python(code)

        return {
            "status": "success",
            "suggestions": suggestions,
            "refactoring_score": max(0, 100 - len(suggestions) * 10)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "suggestions": []
        }
