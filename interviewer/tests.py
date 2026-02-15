from django.contrib.auth.models import User
from django.test import Client, TestCase

from .logic import InterviewSession
from .questions import get_question_bank


class InterviewFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            password="pass12345",
            first_name="Tester",
        )

    def test_auth_pages_load(self):
        signin = self.client.get("/signin/")
        signup = self.client.get("/signup/")
        self.assertEqual(signin.status_code, 200)
        self.assertEqual(signup.status_code, 200)

    def test_home_requires_authentication(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/signin/"))

    def test_signup_flow_creates_user(self):
        response = self.client.post(
            "/signup/submit/",
            data={"name": "Alice", "username": "alice1", "password": "securePass123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertTrue(User.objects.filter(username="alice1").exists())

    def test_signin_and_logout_flow(self):
        signin = self.client.post(
            "/signin/submit/",
            data={"username": "tester", "password": "pass12345"},
        )
        self.assertEqual(signin.status_code, 302)
        self.assertEqual(signin.url, "/")

        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)

        logout = self.client.post("/logout/")
        self.assertEqual(logout.status_code, 302)
        self.assertEqual(logout.url, "/signin/")

    def test_question_bank_has_more_than_25_and_expected_topics(self):
        questions = get_question_bank()
        topics = {q.topic for q in questions}

        self.assertGreater(len(questions), 25)
        self.assertSetEqual(topics, {"DSA", "CN", "OS", "Behavioral"})

    def test_interview_session_uses_25_questions(self):
        session = InterviewSession()
        self.assertEqual(len(session.questions), 25)

    def test_start_and_submit_answer_without_per_question_feedback(self):
        self.client.login(username="tester", password="pass12345")

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

    def test_history_available_after_completion(self):
        self.client.login(username="tester", password="pass12345")

        start = self.client.get("/api/start/")
        total = start.json()["total_questions"]

        for _ in range(total):
            result = self.client.post(
                "/api/answer/",
                data='{"answer":"sorted divide middle log"}',
                content_type="application/json",
            )

        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.json()["finished"])

        history = self.client.get("/api/history/")
        self.assertEqual(history.status_code, 200)
        payload = history.json()
        self.assertEqual(len(payload["history"]), 1)
        self.assertIn("report", payload["history"][0])

    def test_past_scores_page_loads_for_authenticated_user(self):
        self.client.login(username="tester", password="pass12345")
        response = self.client.get("/past-scores/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Past Scores Dashboard")
