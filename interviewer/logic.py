import random
from typing import Dict, List, Optional

from .evaluation import compile_interview_report, evaluate_answer
from .questions import get_question_bank

INTERVIEW_QUESTION_COUNT = 25


class InterviewSession:
    def __init__(self, questions=None, index=0, responses=None, selected_qids: Optional[List[int]] = None):
        bank = get_question_bank()
        by_qid = {question.qid: question for question in bank}

        if questions is not None:
            self.questions = questions
        elif selected_qids:
            self.questions = [by_qid[qid] for qid in selected_qids if qid in by_qid]
        else:
            count = min(INTERVIEW_QUESTION_COUNT, len(bank))
            self.questions = random.sample(bank, count)

        self.selected_qids = [question.qid for question in self.questions]
        self.index = index
        self.responses = responses or []

    def get_current_question(self):
        return self.questions[self.index]

    def save_response(self, response: str) -> Dict[str, object]:
        question = self.get_current_question()
        evaluation = evaluate_answer(question, response)
        payload = {
            "qid": question.qid,
            "topic": question.topic,
            "question": question.prompt,
            "answer": response,
            "score": evaluation["score"],
            "feedback": evaluation["feedback"],
            "matched_keywords": evaluation["matched_keywords"],
        }
        self.responses.append(payload)
        self.index += 1
        return payload

    def is_finished(self):
        return self.index >= len(self.questions)

    def to_dict(self) -> Dict[str, object]:
        return {
            "index": self.index,
            "responses": self.responses,
            "selected_qids": self.selected_qids,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]):
        return cls(
            index=int(data.get("index", 0)),
            responses=list(data.get("responses", [])),
            selected_qids=[int(qid) for qid in data.get("selected_qids", [])],
        )

    def final_report(self) -> Dict[str, object]:
        return compile_interview_report(self.responses)
