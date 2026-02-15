from django.test import Client, TestCase

from .questions import get_question_bank


class InterviewFlowTests(TestCase):
    def test_question_bank_has_25_and_all_topics(self):
        questions = get_question_bank()
        topics = {q.topic for q in questions}

        self.assertEqual(len(questions), 25)
        self.assertSetEqual(topics, {"DSA", "CN", "OS", "Behavioral"})

    def test_start_and_submit_answer(self):
        client = Client()

        start = client.get("/api/start/")
        self.assertEqual(start.status_code, 200)

        first = client.post("/api/answer/", data='{"answer":"binary search works on sorted array and takes o(log n)"}', content_type="application/json")
        self.assertEqual(first.status_code, 200)
        payload = first.json()
        self.assertIn("evaluation", payload)
        self.assertFalse(payload["finished"])
