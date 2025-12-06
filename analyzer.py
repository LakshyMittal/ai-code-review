# analyzer.py

"""
Static code analysis module.
This performs non-LLM analysis on Python code and returns:
- unused imports
- long functions
- long lines
- risky patterns
- cyclomatic complexity heuristic
Enterprise-grade structure, simple & clean.
"""

import ast
import re
from typing import List, Dict, Any


class StaticAnalyzer:

    def __init__(self):
        pass

    # --------------------------------------------------------------
    # MAIN ENTRY POINT
    # --------------------------------------------------------------
    def analyze(self, code: str) -> Dict[str, Any]:
        tree = self._parse_ast(code)

        return {
            "unused_imports": self._detect_unused_imports(tree, code),
            "long_functions": self._detect_long_functions(tree),
            "long_lines": self._detect_long_lines(code),
            "risky_patterns": self._detect_risky_patterns(code),
            "complexity_score": self._complexity_score(tree),
        }

    # --------------------------------------------------------------
    # INTERNAL FUNCTIONS
    # --------------------------------------------------------------
    def _parse_ast(self, code: str):
        try:
            return ast.parse(code)
        except Exception:
            # If code is broken, return empty AST
            return ast.parse("")

    # --------------------------------------------------------------
    # UNUSED IMPORTS
    # --------------------------------------------------------------
    def _detect_unused_imports(self, tree, code: str) -> List[str]:
        imports = []
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name.split(".")[0])

            if isinstance(node, ast.ImportFrom):
                for name in node.names:
                    imports.append(name.name)

            if isinstance(node, ast.Name):
                used_names.add(node.id)

        unused = [imp for imp in imports if imp not in used_names]
        return unused

    # --------------------------------------------------------------
    # LONG FUNCTIONS (> 20 lines)
    # --------------------------------------------------------------
    def _detect_long_functions(self, tree) -> List[Dict[str, Any]]:
        results = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, "body") and len(node.body) > 20:
                    results.append({
                        "function": node.name,
                        "lines": len(node.body)
                    })

        return results

    # --------------------------------------------------------------
    # LONG LINES (> 100 chars)
    # --------------------------------------------------------------
    def _detect_long_lines(self, code: str) -> List[int]:
        long_lines = []
        for i, line in enumerate(code.split("\n"), start=1):
            if len(line) > 100:
                long_lines.append(i)
        return long_lines

    # --------------------------------------------------------------
    # RISKY PATTERNS (security)
    # --------------------------------------------------------------
    RISKY_REGEX = {
        "eval_usage": r"\beval\(",
        "exec_usage": r"\bexec\(",
        "hardcoded_password": r"(password|passwd|pwd)\s*=",
        "hardcoded_secret": r"(api_key|secret|token)\s*=",
        "os_system": r"os\.system\(",
    }

    def _detect_risky_patterns(self, code: str) -> Dict[str, List[int]]:
        results = {}

        for name, pattern in self.RISKY_REGEX.items():
            matches = []
            for i, line in enumerate(code.split("\n"), start=1):
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(i)
            if matches:
                results[name] = matches

        return results

    # --------------------------------------------------------------
    # COMPLEXITY SCORE (rough heuristic)
    # --------------------------------------------------------------
    def _complexity_score(self, tree) -> int:
        score = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                score += 1
        return score
