from typing import Dict, List

from .evaluation import compile_interview_report, evaluate_answer
from .questions import get_question_bank


class InterviewSession:
    def __init__(self, questions=None, index=0, responses=None):
        self.questions = questions or get_question_bank()
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
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]):
        return cls(index=int(data.get("index", 0)), responses=list(data.get("responses", [])))

    def final_report(self) -> Dict[str, object]:
        return compile_interview_report(self.responses)
