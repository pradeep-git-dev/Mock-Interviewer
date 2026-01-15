class InterviewSession:
    def __init__(self, questions):
        self.questions = questions
        self.index = 0
        self.responses = []

    def get_current_question(self):
        return self.questions[self.index]

    def save_response(self, response):
        self.responses.append(response)
        self.index += 1

    def is_finished(self):
        return self.index >= len(self.questions)
