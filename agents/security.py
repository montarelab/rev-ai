import json
import os
import re
from typing import Dict, Any

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool


# =============================================================================
# SECURITY ENGINEER TOOLS
# =============================================================================

class SecurityScannerInput(BaseModel):
    code: str = Field(description="Code content to scan for security issues")
    language: str = Field(description="Programming language")


@tool("security_scanner", args_schema=SecurityScannerInput)
def security_scanner(code: str, language: str) -> Dict[str, Any]:
    """Scan code for security vulnerabilities like hardcoded secrets and SQL injection patterns."""

    security_issues = []

    # Hardcoded secrets patterns
    secret_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
        (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token detected"),
    ]

    # SQL injection patterns
    sql_patterns = [
        (r'execute\s*\(\s*["\'].*%.*["\']', "Potential SQL injection vulnerability"),
        (r'query\s*=\s*["\'].*\+.*["\']', "String concatenation in SQL query"),
        (r'SELECT.*\+.*FROM', "SQL injection risk in SELECT statement"),
    ]

    all_patterns = secret_patterns + sql_patterns

    for pattern, message in all_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE)
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            security_issues.append({
                "type": "security_vulnerability",
                "line": line_num,
                "pattern": pattern,
                "message": message,
                "severity": "high" if "injection" in message.lower() else "medium"
            })

    return {
        "status": "success",
        "issues": security_issues,
        "security_score": max(0, 100 - len(security_issues) * 20)
    }


class CVECheckerInput(BaseModel):
    package_name: str = Field(description="Package name to check")
    version: str = Field(description="Package version")


@tool("cve_checker", args_schema=CVECheckerInput)
def cve_checker(package_name: str, version: str) -> Dict[str, Any]:
    """Check package against CVE database and GitHub Advisory Database."""

    # Mock CVE data for demonstration (in production, use real APIs)
    known_vulnerabilities = {
        "django": {
            "2.0": ["CVE-2019-12781", "CVE-2019-14232"],
            "1.11": ["CVE-2018-14574", "CVE-2018-16984"]
        },
        "requests": {
            "2.19.1": ["CVE-2018-18074"]
        },
        "flask": {
            "0.12": ["CVE-2018-1000656"]
        }
    }

    vulnerabilities = []

    if package_name.lower() in known_vulnerabilities:
        package_vulns = known_vulnerabilities[package_name.lower()]
        if version in package_vulns:
            for cve in package_vulns[version]:
                vulnerabilities.append({
                    "cve_id": cve,
                    "package": package_name,
                    "version": version,
                    "severity": "high",
                    "description": f"Known vulnerability in {package_name} {version}"
                })

    return {
        "status": "success",
        "package": package_name,
        "version": version,
        "vulnerabilities": vulnerabilities,
        "is_vulnerable": len(vulnerabilities) > 0
    }


class DependencyCheckerInput(BaseModel):
    file_path: str = Field(description="Path to dependency file (requirements.txt, package.json)")


@tool("dependency_checker", args_schema=DependencyCheckerInput)
def dependency_checker(file_path: str) -> Dict[str, Any]:
    """Check for outdated and deprecated dependencies."""

    try:
        if not os.path.exists(file_path):
            return {"status": "error", "error": "File not found"}

        with open(file_path, 'r') as f:
            content = f.read()

        outdated_packages = []

        if file_path.endswith('requirements.txt'):
            # Parse Python requirements
            lines = content.strip().split('\n')
            for line in lines:
                if '==' in line:
                    package, version = line.split('==')
                    package = package.strip()
                    version = version.strip()

                    # Mock outdated check (in production, use PyPI API)
                    if package.lower() in ['django', 'flask', 'requests']:
                        outdated_packages.append({
                            "package": package,
                            "current_version": version,
                            "latest_version": "latest",
                            "status": "outdated"
                        })

        elif file_path.endswith('package.json'):
            # Parse Node.js package.json
            try:
                data = json.loads(content)
                dependencies = data.get('dependencies', {})

                for package, version in dependencies.items():
                    if package in ['express', 'lodash', 'moment']:
                        outdated_packages.append({
                            "package": package,
                            "current_version": version,
                            "latest_version": "latest",
                            "status": "outdated"
                        })
            except json.JSONDecodeError:
                return {"status": "error", "error": "Invalid JSON"}

        return {
            "status": "success",
            "file": file_path,
            "outdated_packages": outdated_packages,
            "total_packages": len(outdated_packages)
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


