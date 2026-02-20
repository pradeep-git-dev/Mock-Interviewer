from django.test import Client, SimpleTestCase

from .logic import InterviewSession
from .questions import get_question_bank


class InterviewFlowTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_auth_routes_are_removed(self):
        self.assertEqual(self.client.get("/signin/").status_code, 404)
        self.assertEqual(self.client.get("/signup/").status_code, 404)
        self.assertEqual(self.client.post("/logout/").status_code, 404)

    def test_home_is_public_and_loads_dashboard(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interview Console")

    def test_question_bank_has_more_than_25_and_expected_topics(self):
        questions = get_question_bank()
        topics = {q.topic for q in questions}

        self.assertGreater(len(questions), 25)
        self.assertSetEqual(topics, {"DSA", "CN", "OS", "Behavioral"})

    def test_interview_session_uses_25_questions(self):
        session = InterviewSession()
        self.assertEqual(len(session.questions), 25)

    def test_start_and_submit_answer_without_per_question_feedback(self):
        start = self.client.get("/api/start/")
        self.assertEqual(start.status_code, 200)
        self.assertEqual(start.json()["total_questions"], 25)

        first = self.client.post(
            "/api/answer/",
            data='{"answer":"binary search works on sorted array and takes o(log n)"}',
            content_type="application/json",
        )
        self.assertEqual(first.status_code, 200)
        payload = first.json()
        self.assertFalse(payload["finished"])
        self.assertNotIn("evaluation", payload)
        self.assertIn("question", payload)

    def test_completion_returns_report_without_server_history_endpoint(self):
        start = self.client.get("/api/start/")
        total = start.json()["total_questions"]

        for _ in range(total):
            result = self.client.post(
                "/api/answer/",
                data='{"answer":"sorted divide middle log"}',
                content_type="application/json",
            )

        self.assertEqual(result.status_code, 200)
        payload = result.json()
        self.assertTrue(payload["finished"])
        self.assertIn("report", payload)

        self.assertEqual(self.client.get("/api/history/").status_code, 404)

    def test_past_scores_page_loads_without_auth(self):
        response = self.client.get("/past-scores/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interview Dashboard")
