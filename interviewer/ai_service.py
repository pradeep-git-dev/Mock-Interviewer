"""
AI evaluation service using Google Gemini.
Supports answer evaluation, code evaluation, and question generation.
Falls back to keyword-based evaluation if the API key is not set or the call fails.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY")


def _call_gemini(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.1,
) -> Optional[str]:
    """Call the Gemini API and return the text response, or None on failure."""
    if not GEMINI_API_KEY:
        return None

    try:
        import urllib.request
        import urllib.error

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        )
        payload = json.dumps({
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "response_mime_type": "application/json",
            },
        })

        req = urllib.request.Request(
            url,
            data=payload.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        candidates = body.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "")
    except Exception as exc:
        logger.warning("Gemini API call failed: %s", exc)

    return None


def evaluate_with_ai(topic: str, question: str, answer: str) -> Optional[Dict[str, object]]:
    """
    Use Gemini to evaluate an answer.
    Returns a dict with score/feedback/matched_concepts/strengths/improvement,
    or None if AI evaluation is unavailable.
    """
    from .prompts import EVALUATE_ANSWER_SYSTEM, EVALUATE_ANSWER_USER

    user_prompt = EVALUATE_ANSWER_USER.format(
        topic=topic, question=question, answer=answer
    )
    raw = _call_gemini(EVALUATE_ANSWER_SYSTEM, user_prompt)
    if not raw:
        return None

    try:
        text = raw.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        score = int(result.get("score", 0))
        score = max(0, min(10, score))
        return {
            "score": score,
            "feedback": str(result.get("feedback", "")),
            "matched_keywords": list(result.get("matched_concepts", [])),
            "strengths": str(result.get("strengths", "")),
            "improvement": str(result.get("improvement", "")),
        }
    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning("Failed to parse Gemini eval response: %s", exc)
        return None


def evaluate_code_with_ai(
    problem_description: str,
    language: str,
    submitted_code: str,
    test_cases: list,
    original_code: str = "",
    question_type: str = "coding",
) -> Optional[Dict]:
    """
    Use Gemini to evaluate submitted code against a problem.
    Works for both debug fixes and coding solutions.
    """
    from .prompts import EVALUATE_CODE_SYSTEM, EVALUATE_CODE_USER

    if question_type == "debug":
        original_section = f"Original Buggy Code:\n```{language}\n{original_code}\n```"
    else:
        original_section = ""

    tc_text = "\n".join(
        f"  - Input: {tc.get('input', '')}, Expected: {tc.get('expected', '')}"
        for tc in test_cases[:5]
    )

    user_prompt = EVALUATE_CODE_USER.format(
        problem_description=problem_description,
        language=language,
        original_code_section=original_section,
        submitted_code=submitted_code,
        test_cases=tc_text or "No specific test cases provided.",
    )

    raw = _call_gemini(EVALUATE_CODE_SYSTEM, user_prompt, max_tokens=800)
    if not raw:
        return None

    try:
        text = raw.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        score = int(result.get("score", 0))
        score = max(0, min(10, score))
        return {
            "score": score,
            "passed_tests": int(result.get("passed_tests", 0)),
            "total_tests": int(result.get("total_tests", len(test_cases))),
            "feedback": str(result.get("feedback", "")),
            "strengths": str(result.get("strengths", "")),
            "improvement": str(result.get("improvement", "")),
            "bugs_found": list(result.get("bugs_found", [])),
            "complexity_analysis": str(result.get("complexity_analysis", "")),
        }
    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning("Failed to parse code eval response: %s", exc)
        return None
