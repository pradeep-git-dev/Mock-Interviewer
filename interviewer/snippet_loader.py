"""
Loads code snippet questions from JSON files (python, java, cpp)
and converts them into AdvancedQuestion objects for the advanced interview.

Python snippets already have proper newlines and indentation in the JSON.
Java/C++ snippets are on single lines and need brace-based reformatting.
"""
from __future__ import annotations

import json
import os
import re
from typing import List

from .advanced_questions import AdvancedQuestion

_SNIPPET_DIR = os.path.dirname(os.path.abspath(__file__))
_SNIPPET_FILES = [
    "python_code_snippets.json",
    "java_code_snippets.json",
    "cpp_code_snippets.json",
]

_cached_snippets: List[AdvancedQuestion] | None = None


def _format_c_style(raw: str) -> str:
    """
    Reformat single-line Java/C++ code into properly indented multi-line code.
    Splits on statement-level semicolons and braces, then indents by brace depth.
    """
    code = raw.strip()
    if "\n" in code:
        # Already multi-line, return as-is
        return code

    # We need to split at semicolons that are NOT inside parentheses (for loops etc.)
    # Strategy: replace semicolons inside parens with a placeholder, split, restore
    protected = []
    result_chars = []
    paren_depth = 0
    for ch in code:
        if ch == '(':
            paren_depth += 1
        elif ch == ')':
            paren_depth = max(0, paren_depth - 1)

        if ch == ';' and paren_depth > 0:
            result_chars.append('\x00')  # placeholder
        else:
            result_chars.append(ch)

    code = ''.join(result_chars)

    # Insert newlines at statement boundaries
    code = re.sub(r';\s*', ';\n', code)
    code = re.sub(r'\{\s*', '{\n', code)
    code = re.sub(r'\}\s*', '\n}\n', code)

    # Restore protected semicolons
    code = code.replace('\x00', ';')

    lines = [line.strip() for line in code.split('\n') if line.strip()]

    # Apply indentation based on brace depth
    result = []
    indent = 0
    for line in lines:
        # Decrease indent for closing brace
        if line.startswith('}'):
            indent = max(0, indent - 1)

        result.append('    ' * indent + line)

        # Count braces to adjust indent
        opens = line.count('{')
        closes = line.count('}')
        if line.startswith('}'):
            indent += opens - (closes - 1)
        else:
            indent += opens - closes
        indent = max(0, indent)

    return '\n'.join(result)


def _format_snippet(raw: str, language: str) -> str:
    """Format a raw snippet based on language."""
    if language in ("java", "cpp"):
        return _format_c_style(raw)
    # Python snippets already have proper \n and indentation from JSON
    return raw


def load_snippet_questions() -> List[AdvancedQuestion]:
    """Load all code snippet questions from JSON files and return as AdvancedQuestion list."""
    global _cached_snippets
    if _cached_snippets is not None:
        return _cached_snippets

    questions: List[AdvancedQuestion] = []
    qid_offset = 1000  # Start from 1000 to avoid collision with existing qids

    for filename in _SNIPPET_FILES:
        filepath = os.path.join(_SNIPPET_DIR, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        language = data.get("language", "python")
        for item in data.get("questions", []):
            snippet = _format_snippet(item["snippet"], language)

            qid = qid_offset + item["id"]
            q = AdvancedQuestion(
                qid=qid,
                topic=item["topic"],
                difficulty="Medium",
                question_type="debug",
                prompt=f"{item['question']}\n\nFind and fix the bugs in the code below. Submit the corrected code.",
                code_snippet=snippet,
                language=language,
                expected_output="Corrected code",
                hints=[
                    "Read the code carefully line by line",
                    "Check edge cases and off-by-one errors",
                ],
                correct_answer=f"Review the algorithm for {item['question']} and fix any logical errors.",
            )
            questions.append(q)

        qid_offset += 100  # Next language starts at next offset

    _cached_snippets = questions
    return questions
