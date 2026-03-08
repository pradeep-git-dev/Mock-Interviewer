"""
AI evaluation service using Google Gemini.
Falls back to keyword-based evaluation if the API key is not set or the call fails.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY")


def _call_gemini(system_prompt: str, user_prompt: str) -> Optional[str]:
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
                "temperature": 0.1,
                "maxOutputTokens": 512,
                "response_mime_type": "application/json",
            },
        })

        req = urllib.request.Request(
            url,
            data=payload.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
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
        # Strip markdown fences if present
        text = raw.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        result = json.loads(text)
        # Validate essential keys
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
        logger.warning("Failed to parse Gemini response: %s", exc)
        return None
