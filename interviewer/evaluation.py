from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Dict, List

from .questions import Question


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def evaluate_answer(question: Question, answer: str) -> Dict[str, object]:
    normalized = _normalize(answer)
    if not normalized:
        return {
            "score": 0,
            "feedback": "No answer captured. Try speaking clearly and include key concepts.",
            "matched_keywords": [],
        }

    keywords = [word.lower() for word in question.expected_keywords]
    matched = [word for word in keywords if word in normalized]

    keyword_ratio = len(matched) / max(len(keywords), 1)
    length_score = min(len(normalized.split()) / 60.0, 1.0)

    total = int(round((keyword_ratio * 0.7 + length_score * 0.3) * 10))
    total = max(0, min(10, total))

    if total >= 8:
        feedback = "Strong answer with good coverage of core ideas."
    elif total >= 5:
        feedback = "Decent answer. Add more technical detail and concrete terminology."
    else:
        feedback = "Answer is too shallow. Cover definitions, mechanism, and one example."

    return {
        "score": total,
        "feedback": feedback,
        "matched_keywords": matched,
    }


def compile_interview_report(responses: List[Dict[str, object]]) -> Dict[str, object]:
    if not responses:
        return {
            "overall_score": 0,
            "overall_feedback": "No responses submitted.",
            "topic_breakdown": {},
        }

    by_topic: Dict[str, List[int]] = defaultdict(list)
    for item in responses:
        by_topic[str(item["topic"])].append(int(item["score"]))

    topic_breakdown = {}
    for topic, scores in sorted(by_topic.items()):
        average = round(mean(scores), 2)
        if average >= 8:
            topic_feedback = "Strong performance in this topic. Keep answers concise and example-driven."
        elif average >= 6:
            topic_feedback = "Good baseline. Add deeper reasoning and clearer structure for better impact."
        else:
            topic_feedback = "Needs improvement. Revisit fundamentals and practice with concrete examples."

        topic_breakdown[topic] = {
            "average": average,
            "count": len(scores),
            "feedback": topic_feedback,
        }

    overall = round(mean(int(item["score"]) for item in responses), 2)
    if overall >= 8:
        message = "Interview performance is strong. Keep practicing concise delivery."
    elif overall >= 6:
        message = "Interview performance is moderate. Improve depth and structure in answers."
    else:
        message = "Interview performance needs improvement. Focus on fundamentals and STAR framing."

    return {
        "overall_score": overall,
        "overall_feedback": message,
        "topic_breakdown": topic_breakdown,
    }
