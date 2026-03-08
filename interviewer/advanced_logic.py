"""
Advanced interview session logic with timer, skip, and per-question metrics.
"""
from __future__ import annotations

import time
import random
from typing import Dict, List, Optional

from .advanced_questions import AdvancedQuestion, get_advanced_bank, get_snippet_bank, get_full_advanced_bank
from .ai_service import evaluate_with_ai


ADVANCED_COUNT = 8
MIN_SNIPPET_COUNT = 5  # Minimum code snippet questions per interview
INTERVIEW_DURATION = 30 * 60  # 30 minutes in seconds


class AdvancedSession:
    def __init__(self, questions=None, index=0, responses=None,
                 selected_qids=None, start_time=None, ended=False, lang=None):
        full_bank = get_full_advanced_bank()
        snippet_bank = get_snippet_bank(lang)
        builtin_bank = get_advanced_bank()

        if lang:
            builtin_bank = [q for q in builtin_bank if q.language.lower() == lang.lower()]

        by_qid = {q.qid: q for q in full_bank}

        if questions is not None:
            self.questions = questions
        elif selected_qids:
            self.questions = [by_qid[qid] for qid in selected_qids if qid in by_qid]
        else:
            # Guarantee at least MIN_SNIPPET_COUNT code snippet questions
            snippet_count = min(MIN_SNIPPET_COUNT, len(snippet_bank))
            snippet_picks = random.sample(snippet_bank, snippet_count) if snippet_bank else []

            # Fill remaining slots from built-in bank
            remaining = max(0, ADVANCED_COUNT - len(snippet_picks))
            builtin_picks = random.sample(builtin_bank, min(remaining, len(builtin_bank))) if builtin_bank and remaining > 0 else []

            self.questions = snippet_picks + builtin_picks
            random.shuffle(self.questions)

        self.selected_qids = [q.qid for q in self.questions]
        self.index = index
        self.responses: List[Dict] = responses or []
        self.start_time = start_time or time.time()
        self.ended = ended

    def get_current_question(self) -> AdvancedQuestion:
        return self.questions[self.index]

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def remaining_seconds(self) -> float:
        return max(0, INTERVIEW_DURATION - self.elapsed_seconds())

    def is_time_up(self) -> bool:
        return self.remaining_seconds() <= 0

    def is_finished(self) -> bool:
        return self.ended or self.index >= len(self.questions) or self.is_time_up()

    def evaluate_answer(self, answer: str) -> Dict:
        question = self.get_current_question()
        q_start = self.responses[-1]["q_start"] if self.responses and "q_start" in self.responses[-1] else time.time()
        time_taken = round(time.time() - q_start, 1)

        # Try AI evaluation
        ai_result = evaluate_with_ai(
            question.topic,
            f"[{question.question_type.upper()}] {question.prompt}\n\nCode:\n{question.code_snippet}",
            answer
        )

        if ai_result:
            score = ai_result["score"]
            feedback = ai_result["feedback"]
            strengths = ai_result.get("strengths", "")
            improvement = ai_result.get("improvement", "")
        else:
            # Keyword fallback
            answer_lower = answer.lower()
            correct_lower = question.correct_answer.lower()
            keywords = [w for w in correct_lower.split() if len(w) > 3]
            matched = [k for k in keywords if k in answer_lower]
            ratio = len(matched) / max(len(keywords), 1)
            length_bonus = min(len(answer.split()) / 40.0, 1.0)
            score = int(round((ratio * 0.7 + length_bonus * 0.3) * 10))
            score = max(0, min(10, score))
            feedback = "Good analysis." if score >= 7 else "Try to be more specific about the code behavior."
            strengths = f"Matched {len(matched)} key concepts." if matched else ""
            improvement = "Include more detail about time complexity and edge cases."

        is_debug = question.question_type == "debug"
        payload = {
            "qid": question.qid,
            "topic": question.topic,
            "difficulty": question.difficulty,
            "question_type": question.question_type,
            "prompt": question.prompt,
            "code_snippet": question.code_snippet,
            "language": question.language,
            "answer": answer,
            "correct_answer": question.correct_answer,
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "improvement": improvement,
            "time_taken": time_taken,
            "is_debug": is_debug,
            "debug_success": is_debug and score >= 6,
            "skipped": False,
        }
        self.responses.append(payload)
        self.index += 1
        return payload

    def skip_question(self) -> Dict:
        question = self.get_current_question()
        payload = {
            "qid": question.qid,
            "topic": question.topic,
            "difficulty": question.difficulty,
            "question_type": question.question_type,
            "prompt": question.prompt,
            "code_snippet": question.code_snippet,
            "language": question.language,
            "answer": "",
            "correct_answer": question.correct_answer,
            "score": 0,
            "feedback": "Question skipped.",
            "strengths": "",
            "improvement": "Attempt every question to maximize your score.",
            "time_taken": 0,
            "is_debug": question.question_type == "debug",
            "debug_success": False,
            "skipped": True,
        }
        self.responses.append(payload)
        self.index += 1
        return payload

    def end_interview(self):
        self.ended = True

    def compile_report(self) -> Dict:
        if not self.responses:
            return {"overall_score": 0, "metrics": {}, "topic_breakdown": {}, "responses": []}

        total = len(self.responses)
        answered = [r for r in self.responses if not r.get("skipped")]
        skipped = total - len(answered)
        scores = [r["score"] for r in answered] if answered else [0]
        debug_qs = [r for r in self.responses if r.get("is_debug")]
        debug_ok = sum(1 for r in debug_qs if r.get("debug_success"))
        times = [r["time_taken"] for r in answered if r["time_taken"] > 0]

        from collections import defaultdict
        from statistics import mean
        by_topic: Dict[str, List[int]] = defaultdict(list)
        for r in self.responses:
            by_topic[r["topic"]].append(r["score"])

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
            "metrics": {
                "total_questions": total,
                "answered": len(answered),
                "skipped": skipped,
                "completion_pct": round(len(answered) / max(total, 1) * 100),
                "avg_score": overall,
                "avg_time": round(mean(times), 1) if times else 0,
                "total_time": round(self.elapsed_seconds()),
                "debug_total": len(debug_qs),
                "debug_success": debug_ok,
                "debug_accuracy": round(debug_ok / max(len(debug_qs), 1) * 100),
                "dsa_accuracy": round(overall * 10),
            },
            "topic_breakdown": topic_breakdown,
            "responses": self.responses,
        }

    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "responses": self.responses,
            "selected_qids": self.selected_qids,
            "start_time": self.start_time,
            "ended": self.ended,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            index=int(data.get("index", 0)),
            responses=list(data.get("responses", [])),
            selected_qids=[int(q) for q in data.get("selected_qids", [])],
            start_time=float(data.get("start_time", time.time())),
            ended=bool(data.get("ended", False)),
        )
