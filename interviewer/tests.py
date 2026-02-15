from django.test import Client, TestCase

from .logic import InterviewSession
from .questions import get_question_bank


class InterviewFlowTests(TestCase):
    def test_past_scores_page_loads(self):
        client = Client()
        response = client.get("/past-scores/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Past Scores Dashboard")

    def test_question_bank_has_more_than_25_and_expected_topics(self):
        questions = get_question_bank()
        topics = {q.topic for q in questions}

        self.assertGreater(len(questions), 25)
        self.assertSetEqual(topics, {"DSA", "CN", "OS", "Behavioral"})

    def test_interview_session_uses_25_questions(self):
        session = InterviewSession()
        self.assertEqual(len(session.questions), 25)

    def test_start_and_submit_answer_without_per_question_feedback(self):
        client = Client()

        start = client.get("/api/start/")
        self.assertEqual(start.status_code, 200)
        self.assertEqual(start.json()["total_questions"], 25)

        first = client.post(
            "/api/answer/",
            data='{"answer":"binary search works on sorted array and takes o(log n)"}',
            content_type="application/json",
        )
        self.assertEqual(first.status_code, 200)
        payload = first.json()
        self.assertFalse(payload["finished"])
        self.assertNotIn("evaluation", payload)
        self.assertIn("question", payload)

    def test_history_available_after_completion(self):
        client = Client()
        start = client.get("/api/start/")
        total = start.json()["total_questions"]

        for _ in range(total):
            result = client.post(
                "/api/answer/",
                data='{"answer":"sorted divide middle log"}',
                content_type="application/json",
            )

        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.json()["finished"])

        history = client.get("/api/history/")
        self.assertEqual(history.status_code, 200)
        payload = history.json()
        self.assertEqual(len(payload["history"]), 1)
        self.assertIn("report", payload["history"][0])
