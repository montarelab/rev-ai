import ast
from typing import Dict, Any, List

from langchain_core.tools import tool
from pydantic import BaseModel, Field


# =============================================================================
# TECHNICAL WRITER TOOLS
# =============================================================================

class DocAnalyzerInput(BaseModel):
    code: str = Field(description="Code content to analyze for documentation")
    language: str = Field(description="Programming language")


@tool("doc_analyzer", args_schema=DocAnalyzerInput)
def doc_analyzer(code: str, language: str) -> Dict[str, Any]:
    """Check for missing docstrings and comments."""

    def analyze_python_docs(code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(code)

            doc_issues = []
            functions_without_docs = []
            classes_without_docs = []

            class DocVisitor(ast.NodeVisitor):
                def visit_FunctionDef(self, node):
                    has_docstring = (
                            len(node.body) > 0 and
                            isinstance(node.body[0], ast.Expr) and
                            isinstance(node.body[0].value, ast.Str)
                    )

                    if not has_docstring:
                        functions_without_docs.append({
                            "name": node.name,
                            "line": node.lineno,
                            "type": "function"
                        })

                    self.generic_visit(node)

                def visit_ClassDef(self, node):
                    has_docstring = (
                            len(node.body) > 0 and
                            isinstance(node.body[0], ast.Expr) and
                            isinstance(node.body[0].value, ast.Str)
                    )

                    if not has_docstring:
                        classes_without_docs.append({
                            "name": node.name,
                            "line": node.lineno,
                            "type": "class"
                        })

                    self.generic_visit(node)

            visitor = DocVisitor()
            visitor.visit(tree)

            # Count total comments
            comment_count = code.count('#')
            lines_of_code = len([line for line in code.split('\n') if line.strip()])
            comment_ratio = comment_count / max(lines_of_code, 1) * 100

            return {
                "functions_without_docs": functions_without_docs,
                "classes_without_docs": classes_without_docs,
                "comment_count": comment_count,
                "comment_ratio": comment_ratio,
                "total_issues": len(functions_without_docs) + len(classes_without_docs)
            }

        except SyntaxError:
            return {"error": "Syntax error in code"}

    try:
        if language.lower() == 'python':
            doc_data = analyze_python_docs(code)
        else:
            # Simple fallback
            doc_data = {
                "functions_without_docs": [],
                "classes_without_docs": [],
                "comment_count": code.count('//') + code.count('#'),
                "comment_ratio": 0,
                "total_issues": 0
            }

        documentation_score = max(0, 100 - doc_data.get("total_issues", 0) * 10)

        return {
            "status": "success",
            "documentation_analysis": doc_data,
            "documentation_score": documentation_score
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


class DocGeneratorInput(BaseModel):
    code: str = Field(description="Code content to generate documentation for")
    language: str = Field(description="Programming language")


@tool("doc_generator", args_schema=DocGeneratorInput)
def doc_generator(code: str, language: str) -> Dict[str, Any]:
    """Generate documentation from code structure."""

    def generate_python_docs(code: str) -> List[Dict]:
        try:
            tree = ast.parse(code)
            documentation = []

            class DocGenerator(ast.NodeVisitor):
                def visit_FunctionDef(self, node):
                    args = [arg.arg for arg in node.args.args]

                    doc_suggestion = {
                        "type": "function",
                        "name": node.name,
                        "line": node.lineno,
                        "args": args,
                        "suggested_docstring": f'"""\n    {node.name.replace("_", " ").title()}\n    \n    Args:\n'
                    }

                    for arg in args:
                        doc_suggestion["suggested_docstring"] += f"        {arg}: Description of {arg}\n"

                    doc_suggestion[
                        "suggested_docstring"] += "    \n    Returns:\n        Description of return value\n    \"\"\""

                    documentation.append(doc_suggestion)
                    self.generic_visit(node)

                def visit_ClassDef(self, node):
                    doc_suggestion = {
                        "type": "class",
                        "name": node.name,
                        "line": node.lineno,
                        "suggested_docstring": f'"""\n    {node.name} class\n    \n    Description of the class purpose and usage.\n    \"\"\"'
                    }

                    documentation.append(doc_suggestion)
                    self.generic_visit(node)

            generator = DocGenerator()
            generator.visit(tree)

            return documentation

        except SyntaxError:
            return []

    try:
        if language.lower() == 'python':
            docs = generate_python_docs(code)
        else:
            docs = []

        return {
            "status": "success",
            "generated_docs": docs,
            "total_suggestions": len(docs)
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "generated_docs": []}

