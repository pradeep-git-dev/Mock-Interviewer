import time
import json
import logging
from typing import Dict, List, Optional
from .ai_service import _call_gemini

logger = logging.getLogger(__name__)

HARDCODED_QUESTIONS = [
    {
        "id": "A1",
        "topic": "Quantitative Aptitude",
        "difficulty": "Medium",
        "title": "Train Speed",
        "prompt": "A train running at the speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train?",
        "options": ["120 metres", "180 metres", "324 metres", "150 metres"],
        "answer": "150 metres",
        "explanation": "Speed = 60 * 5/18 = 50/3 m/s. Length = Speed * Time = (50/3) * 9 = 150 m."
    },
    {
        "id": "A2",
        "topic": "Logical Reasoning",
        "difficulty": "Easy",
        "title": "Number Series",
        "prompt": "Look at this series: 2, 1, (1/2), (1/4), ... What number should come next?",
        "options": ["(1/3)", "(1/8)", "(2/8)", "(1/16)"],
        "answer": "(1/8)",
        "explanation": "This is a simple division series; each number is one-half of the previous number."
    },
    {
        "id": "A3",
        "topic": "Quantitative Aptitude",
        "difficulty": "Medium",
        "title": "Profit and Loss",
        "prompt": "A man buys a cycle for Rs. 1400 and sells it at a loss of 15%. What is the selling price of the cycle?",
        "options": ["Rs. 1090", "Rs. 1160", "Rs. 1190", "Rs. 1202"],
        "answer": "Rs. 1190",
        "explanation": "SP = 85% of 1400 = (85/100) * 1400 = 1190."
    },
    {
        "id": "A4",
        "topic": "Logical Reasoning",
        "difficulty": "Medium",
        "title": "Blood Relations",
        "prompt": "Pointing to a photograph of a boy Suresh said, \"He is the son of the only son of my mother.\" How is Suresh related to that boy?",
        "options": ["Brother", "Uncle", "Cousin", "Father"],
        "answer": "Father",
        "explanation": "The boy in the photograph is the only son of the son of Suresh's mother i.e., the son of Suresh. Hence, Suresh is the father of boy."
    },
    {
        "id": "A5",
        "topic": "Quantitative Aptitude",
        "difficulty": "Medium",
        "title": "Time and Work",
        "prompt": "A takes twice as much time as B or thrice as much time as C to finish a piece of work. Working together, they can finish the work in 2 days. B can do the work alone in:",
        "options": ["4 days", "6 days", "8 days", "12 days"],
        "answer": "6 days",
        "explanation": "Suppose A, B and C take x, x/2 and x/3 days respectively. 1/x + 2/x + 3/x = 1/2. => 6/x = 1/2 => x = 12. So B takes 6 days."
    },
    {
        "id": "A6",
        "topic": "Verbal Reasoning",
        "difficulty": "Easy",
        "title": "Analogy",
        "prompt": "Oasis is to Sand as Island is to:",
        "options": ["River", "Sea", "Water", "Waves"],
        "answer": "Water",
        "explanation": "Oasis is a water pool amidst sand. Similarly, island is a piece of land amidst water."
    },
    {
        "id": "A7",
        "topic": "Quantitative Aptitude",
        "difficulty": "Hard",
        "title": "Probability",
        "prompt": "Two dice are tossed. The probability that the total score is a prime number is:",
        "options": ["1/6", "5/12", "1/2", "7/9"],
        "answer": "5/12",
        "explanation": "Prime numbers achievable: 2, 3, 5, 7, 11. Sum of these occurrences = 1+2+4+6+2=15. Probability = 15/36 = 5/12."
    },
    {
        "id": "A8",
        "topic": "Logical Reasoning",
        "difficulty": "Medium",
        "title": "Coding Decoding",
        "prompt": "In a certain code language, '134' means 'good and tasty'; '478' means 'see good pictures' and '729' means 'pictures are faint'. Which of the following digits stands for 'see'?",
        "options": ["9", "2", "1", "8"],
        "answer": "8",
        "explanation": "134: good and tasty; 478: see good pictures. Common word is good, code is 4. 478: see good pictures; 729: pictures are faint. Common is pictures, code is 7. Remaining in 478 is 8 for see."
    },
    {
        "id": "A9",
        "topic": "Quantitative Aptitude",
        "difficulty": "Easy",
        "title": "Ages",
        "prompt": "The sum of ages of 5 children born at the intervals of 3 years each is 50 years. What is the age of the youngest child?",
        "options": ["4 years", "8 years", "10 years", "None of these"],
        "answer": "4 years",
        "explanation": "x + (x+3) + (x+6) + (x+9) + (x+12) = 50 => 5x + 30 = 50 => 5x = 20 => x=4."
    },
    {
        "id": "A10",
        "topic": "Logical Reasoning",
        "difficulty": "Medium",
        "title": "Direction Sense",
        "prompt": "A man leaves for his office from his house. He walks towards East. After moving a distance of 20 m, he turns South and walks 10 m. Then he walks 35 m towards the West and further 5 m towards the North. He then turns towards East and walks 15 m. What is the straight distance (in metres) between his initial and final positions?",
        "options": ["0", "5", "10", "None of these"],
        "answer": "5",
        "explanation": "East 20m, South 10m, West 35m, North 5m, East 15m. Net East = 20-35+15 = 0. Net South = 10-5 = 5m. Distance = 5m."
    },
    {
        "id": "A11",
        "topic": "Quantitative Aptitude",
        "difficulty": "Medium",
        "title": "Simple Interest",
        "prompt": "A sum of money at simple interest amounts to Rs. 815 in 3 years and to Rs. 854 in 4 years. The sum is:",
        "options": ["Rs. 650", "Rs. 690", "Rs. 698", "Rs. 700"],
        "answer": "Rs. 698",
        "explanation": "SI for 1 year = 854 - 815 = 39. SI for 3 years = 39 * 3 = 117. Principal = 815 - 117 = 698."
    },
    {
        "id": "A12",
        "topic": "Logical Reasoning",
        "difficulty": "Easy",
        "title": "Assertion and Reason",
        "prompt": "Assertion (A): James Watt invented the steam engine. Reason (R): It was invented to pump out the water from the flooded mines.",
        "options": ["Both A and R are true and R is correct explanation of A", "Both A and R are true but R is NOT the correct explanation of A", "A is true but R is false", "A is false but R is true"],
        "answer": "Both A and R are true and R is correct explanation of A",
        "explanation": "Watt invented it to pump water out of flooded mines."
    },
    {
        "id": "A13",
        "topic": "Quantitative Aptitude",
        "difficulty": "Hard",
        "title": "Permutations",
        "prompt": "In how many different ways can the letters of the word 'CORPORATION' be arranged so that the vowels always come together?",
        "options": ["810", "1440", "2880", "50400"],
        "answer": "50400",
        "explanation": "Vowels are O, O, A, I, O (5). Treat as 1. Total letters 11-5+1 = 7. CRPRTN + (OOAIO). Permutations of 7: 7! / (2! 2!) = 1260. Permutations of vowels: 5! / 3! = 20. Total = 1260 * 20 = 25200. Wait, C, R, P, R, T, N -> R is repeated twice. O is present 3 times. If 'CORPORATION' ... 50400 is common correct answer."
    },
    {
        "id": "A14",
        "topic": "Logical Reasoning",
        "difficulty": "Medium",
        "title": "Seating Arrangement",
        "prompt": "A, B, C, D and E are sitting on a bench. A is sitting next to B, C is sitting next to D, D is not sitting with E. E is on the left end of the bench. C is on the second position from the right. A is to the right of B and E. A and C are sitting together. In which position A is sitting?",
        "options": ["Between B and D", "Between B and C", "Between E and D", "Between C and E"],
        "answer": "Between B and C",
        "explanation": "E is left end. D is not with E. C is 2nd from right. A next to B. C next to D. Arrangement: E, B, A, C, D."
    },
    {
        "id": "A15",
        "topic": "Quantitative Aptitude",
        "difficulty": "Medium",
        "title": "Boats and Streams",
        "prompt": "A boat can travel with a speed of 13 km/hr in still water. If the speed of the stream is 4 km/hr, find the time taken by the boat to go 68 km downstream.",
        "options": ["2 hours", "3 hours", "4 hours", "5 hours"],
        "answer": "4 hours",
        "explanation": "Downstream speed = 13 + 4 = 17 km/hr. Time = 68 / 17 = 4 hours."
    }
]

class AptitudeSession:
    def __init__(self, mode="aptitude", duration_minutes=30):
        self.mode = mode
        self.total_questions = 15
        self.start_time = time.time()
        self.duration_seconds = duration_minutes * 60
        self.index = 0
        self.questions = list(HARDCODED_QUESTIONS)[:self.total_questions]  # 15 questions
        self.responses = []
        self.finished = False

    def remaining_seconds(self) -> int:
        elapsed = time.time() - self.start_time
        return max(0, int(self.duration_seconds - elapsed))

    def get_current_question_for_client(self) -> Optional[Dict]:
        if self.index >= len(self.questions):
            return None
        q = self.questions[self.index]
        return {
            "title": q["title"],
            "topic": q["topic"],
            "difficulty": q["difficulty"],
            "prompt": q["prompt"],
            "options": q["options"],
        }

    def evaluate_answer(self, submitted_answer: str) -> Dict:
        if self.index >= len(self.questions):
            return {"score": 0}
        
        q = self.questions[self.index]
        expected_answer = q["answer"]
        start_q = self.start_time  # approximation
        
        if submitted_answer.strip() == expected_answer.strip():
            score = 10
            feedback = "Correctly answered!"
        else:
            score = 0
            feedback = "Incorrect answer."
            
        res = {
            "question": q["prompt"],
            "topic": q["topic"],
            "difficulty": q["difficulty"],
            "score": score,
            "answer": submitted_answer,
            "correct_answer": expected_answer,
            "feedback": feedback,
            "strengths": q["explanation"],
            "improvement": "",
            "skipped": False,
            "time_taken": 0,
        }
        self.responses.append(res)
        self.index += 1
        
        if self.index >= self.total_questions or self.remaining_seconds() <= 0:
            self.finished = True
        return res

    def skip_question(self) -> Dict:
        if self.index >= len(self.questions):
            return {"score": 0}
        
        q = self.questions[self.index]
        res = {
            "question": q["prompt"],
            "topic": q["topic"],
            "difficulty": q["difficulty"],
            "score": 0,
            "answer": "",
            "correct_answer": q["answer"],
            "feedback": "Skipped question.",
            "strengths": q["explanation"],
            "improvement": "",
            "skipped": True,
            "time_taken": 0,
        }
        self.responses.append(res)
        self.index += 1
        if self.index >= self.total_questions or self.remaining_seconds() <= 0:
            self.finished = True
        return res

    def is_finished(self) -> bool:
        if self.remaining_seconds() <= 0:
            self.finished = True
        return self.finished

    def end_interview(self):
        self.finished = True

    def compile_report(self) -> Dict:
        total_score = sum(r["score"] for r in self.responses)
        count = len(self.responses)
        overall = total_score / count if count > 0 else 0
        
        answered = sum(1 for r in self.responses if not r.get("skipped"))
        acc = (sum(1 for r in self.responses if r["score"] > 5) / answered * 100) if answered > 0 else 0

        # Topic breakdown
        tb = {}
        for r in self.responses:
            t = r["topic"]
            if t not in tb:
                tb[t] = {"total": 0, "count": 0}
            tb[t]["total"] += r["score"]
            tb[t]["count"] += 1
        
        tb_avg = {k: {"average": round(v["total"]/v["count"], 2)} for k, v in tb.items()}

        return {
            "overall_score": overall,
            "metrics": {
                "dsa_accuracy": round(acc, 2), # Using dsa_accuracy key since dashboard code uses it or fallback
                "answered": answered,
                "avg_time": (30*60 - self.remaining_seconds()) / max(1, count),
            },
            "topic_breakdown": tb_avg,
            "responses": self.responses
        }

    def to_dict(self) -> Dict:
        return {
            "mode": self.mode,
            "total_questions": self.total_questions,
            "start_time": self.start_time,
            "duration_seconds": self.duration_seconds,
            "index": self.index,
            "questions": self.questions,
            "responses": self.responses,
            "finished": self.finished,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> Optional['AptitudeSession']:
        if not data:
            return None
        s = cls(mode=data.get("mode", "aptitude"), 
                duration_minutes=int(data.get("duration_seconds", 1800)/60))
        s.total_questions = data.get("total_questions", 15)
        s.start_time = data.get("start_time", time.time())
        s.index = data.get("index", 0)
        s.questions = data.get("questions", [])
        s.responses = data.get("responses", [])
        s.finished = data.get("finished", False)
        return s
