"""
Advanced interview session logic with two modes:
  Mode 1 – Debugging Round: Fix buggy code
  Mode 2 – Logical Round: Solve reasoning & logic puzzles

Questions are dynamically generated via AI with static fallbacks.
"""
from __future__ import annotations

import time
import random
from collections import defaultdict
from statistics import mean
from typing import Dict, List, Optional

from .ai_service import evaluate_code_with_ai, evaluate_with_ai
from .ai_question_generator import (
    generate_debug_question,
    generate_coding_question,
    generate_logical_question,
    get_fallback_debug,
    get_fallback_coding,
    get_fallback_logical,
)


QUESTIONS_PER_ROUND = 5
INTERVIEW_DURATION = 30 * 60  # 30 minutes


class AdvancedSession:
    """
    Manages an advanced interview session.
    Supports modes: 'debug' and 'logical'.
    Questions are generated one at a time (on-demand) from AI.
    """

    def __init__(
        self,
        mode: str = "debug",
        lang: str = "python",
        index: int = 0,
        responses: Optional[List[Dict]] = None,
        questions: Optional[List[Dict]] = None,
        start_time: Optional[float] = None,
        ended: bool = False,
        used_topics: Optional[List[str]] = None,
        fallback_idx: int = 0,
    ):
        self.mode = mode  # "debug" or "logical"
        self.lang = lang
        self.index = index
        self.responses: List[Dict] = responses or []
        self.questions: List[Dict] = questions or []
        self.start_time = start_time or time.time()
        self.ended = ended
        self.used_topics: List[str] = used_topics or []
        self.fallback_idx = fallback_idx
        self.total_questions = QUESTIONS_PER_ROUND

    def _generate_next_question(self) -> Optional[Dict]:
        """Generate the next question using AI, falling back to static bank."""
        qnum = self.index + 1

        if self.mode == "debug":
            q = generate_debug_question(
                self.lang, self.used_topics, qnum, self.total_questions
            )
            if not q:
                q = get_fallback_debug(self.lang, list(range(self.fallback_idx)))
                self.fallback_idx += 1
        else:
            # Logical mode
            q = generate_logical_question(
                self.used_topics, qnum, self.total_questions
            )
            if not q:
                q = get_fallback_logical(list(range(self.fallback_idx)))
                self.fallback_idx += 1

        if q:
            q["q_index"] = qnum
            q["q_start"] = time.time()
            self.used_topics.append(q.get("topic", ""))
            self.questions.append(q)

        return q

    def get_current_question(self) -> Optional[Dict]:
        """Get the current question, generating it if needed."""
        if self.index < len(self.questions):
            q = self.questions[self.index]
            q["q_start"] = time.time()
            return q
        return self._generate_next_question()

    def get_current_question_for_client(self) -> Optional[Dict]:
        """Return a sanitized question dict safe for the client (no solutions)."""
        q = self.get_current_question()
        if not q:
            return None

        if self.mode == "debug":
            return {
                "type": "debug",
                "topic": q.get("topic", ""),
                "title": q.get("title", ""),
                "difficulty": q.get("difficulty", "Medium"),
                "description": q.get("description", ""),
                "buggy_code": q.get("buggy_code", ""),
                "language": q.get("language", self.lang),
                "hints": q.get("hints", []),
            }
        else:
            # Logical mode
            return {
                "type": "logical",
                "topic": q.get("topic", ""),
                "title": q.get("title", ""),
                "difficulty": q.get("difficulty", "Medium"),
                "description": q.get("description", ""),
                "hints": q.get("hints", []),
            }

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def remaining_seconds(self) -> float:
        return max(0, INTERVIEW_DURATION - self.elapsed_seconds())

    def is_time_up(self) -> bool:
        return self.remaining_seconds() <= 0

    def is_finished(self) -> bool:
        return self.ended or self.index >= self.total_questions or self.is_time_up()

    def evaluate_answer(self, submitted_code: str) -> Dict:
        """Evaluate the candidate's submitted answer using AI."""
        if self.index >= len(self.questions):
            return {"score": 0, "feedback": "No question to evaluate."}

        question = self.questions[self.index]
        q_start = question.get("q_start", time.time())
        time_taken = round(time.time() - q_start, 1)

        if self.mode == "debug":
            # Debug mode: AI code evaluation
            ai_result = evaluate_code_with_ai(
                problem_description=question.get("description", ""),
                language=self.lang,
                submitted_code=submitted_code,
                test_cases=question.get("test_cases", []),
                original_code=question.get("buggy_code", ""),
                question_type="debug",
            )
        else:
            # Logical mode: AI text-based evaluation
            ai_result = evaluate_with_ai(
                question.get("topic", "Logic"),
                question.get("description", ""),
                submitted_code,
            )

        if ai_result:
            score = ai_result.get("score", 0)
            feedback = ai_result.get("feedback", "")
            strengths = ai_result.get("strengths", "")
            improvement = ai_result.get("improvement", "")
            bugs_found = ai_result.get("bugs_found", [])
            passed_tests = ai_result.get("passed_tests", 0)
            total_tests = ai_result.get("total_tests", 0)
            complexity = ai_result.get("complexity_analysis", "")
        else:
            # Basic fallback
            score = self._fallback_score(submitted_code, question)
            feedback = "Response evaluated using basic comparison."
            strengths = "Submitted a response for evaluation." if submitted_code.strip() else ""
            improvement = "Provide more detailed reasoning."
            bugs_found = []
            passed_tests = 0
            total_tests = 0
            complexity = ""

        payload = {
            "q_index": question.get("q_index", self.index + 1),
            "topic": question.get("topic", ""),
            "title": question.get("title", ""),
            "difficulty": question.get("difficulty", ""),
            "type": self.mode,
            "language": self.lang,
            "answer": submitted_code,
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "improvement": improvement,
            "bugs_found": bugs_found,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "complexity_analysis": complexity,
            "time_taken": time_taken,
            "skipped": False,
        }

        # Add question-specific data
        if self.mode == "debug":
            payload["buggy_code"] = question.get("buggy_code", "")
            payload["fixed_code"] = question.get("fixed_code", "")
            payload["bug_explanation"] = question.get("bug_explanation", "")
            payload["description"] = question.get("description", "")
        else:
            # Logical mode
            payload["description"] = question.get("description", "")
            payload["correct_answer"] = question.get("correct_answer", "")

        self.responses.append(payload)
        self.index += 1
        return payload

    def _fallback_score(self, submitted: str, question: Dict) -> int:
        """Basic scoring when AI is unavailable."""
        if not submitted.strip():
            return 0

        solution = question.get("fixed_code", "") or question.get("solution_code", "")
        if not solution:
            return 3  # Can't compare, give partial credit for attempt

        # Structural similarity
        sub_lines = set(submitted.strip().lower().split("\n"))
        sol_lines = set(solution.strip().lower().split("\n"))
        if not sol_lines:
            return 3

        overlap = len(sub_lines & sol_lines) / len(sol_lines)
        return max(1, min(10, int(round(overlap * 10))))

    def skip_question(self) -> Dict:
        """Skip the current question."""
        if self.index >= len(self.questions):
            return {"score": 0, "feedback": "No question to skip."}

        question = self.questions[self.index]
        payload = {
            "q_index": question.get("q_index", self.index + 1),
            "topic": question.get("topic", ""),
            "title": question.get("title", ""),
            "difficulty": question.get("difficulty", ""),
            "type": self.mode,
            "language": self.lang,
            "answer": "",
            "score": 0,
            "feedback": "Question skipped.",
            "strengths": "",
            "improvement": "Attempt every question to maximize your score.",
            "time_taken": 0,
            "skipped": True,
        }
        if self.mode == "debug":
            payload["buggy_code"] = question.get("buggy_code", "")
            payload["fixed_code"] = question.get("fixed_code", "")
            payload["bug_explanation"] = question.get("bug_explanation", "")
            payload["description"] = question.get("description", "")
        else:
            payload["description"] = question.get("description", "")
            payload["correct_answer"] = question.get("correct_answer", "")

        self.responses.append(payload)
        self.index += 1
        return payload

    def end_interview(self):
        self.ended = True

    def compile_report(self) -> Dict:
        if not self.responses:
            return {
                "overall_score": 0, "mode": self.mode,
                "metrics": {}, "topic_breakdown": {}, "responses": [],
            }

        answered = [r for r in self.responses if not r.get("skipped")]
        skipped = len(self.responses) - len(answered)
        scores = [r["score"] for r in answered] if answered else [0]
        times = [r["time_taken"] for r in answered if r.get("time_taken", 0) > 0]

        by_topic: Dict[str, List[int]] = defaultdict(list)
        for r in self.responses:
            by_topic[r.get("topic", "General")].append(r["score"])

        topic_breakdown = {}
        for topic, sc in sorted(by_topic.items()):
            avg = round(mean(sc), 1)
            topic_breakdown[topic] = {
                "average": avg,
                "count": len(sc),
                "max": max(sc),
                "min": min(sc),
            }

        overall = round(mean(scores), 1) if scores else 0

        return {
            "overall_score": overall,
            "mode": self.mode,
            "language": self.lang,
            "metrics": {
                "total_questions": len(self.responses),
                "answered": len(answered),
                "skipped": skipped,
                "completion_pct": round(len(answered) / max(len(self.responses), 1) * 100),
                "avg_score": overall,
                "avg_time": round(mean(times), 1) if times else 0,
                "total_time": round(self.elapsed_seconds()),
            },
            "topic_breakdown": topic_breakdown,
            "responses": self.responses,
        }

    def to_dict(self) -> Dict:
        return {
            "mode": self.mode,
            "lang": self.lang,
            "index": self.index,
            "responses": self.responses,
            "questions": self.questions,
            "start_time": self.start_time,
            "ended": self.ended,
            "used_topics": self.used_topics,
            "fallback_idx": self.fallback_idx,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AdvancedSession":
        return cls(
            mode=str(data.get("mode", "debug")),
            lang=str(data.get("lang", "python")),
            index=int(data.get("index", 0)),
            responses=list(data.get("responses", [])),
            questions=list(data.get("questions", [])),
            start_time=float(data.get("start_time", time.time())),
            ended=bool(data.get("ended", False)),
            used_topics=list(data.get("used_topics", [])),
            fallback_idx=int(data.get("fallback_idx", 0)),
        )
