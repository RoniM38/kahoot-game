import random
from client import Client

class GameHost(Client):
    def __init__(self, server_ip='127.0.0.1', port=12345):
        super().__init__(server_ip, port)
        self.game_pin = random.randint(100000, 999999)
        self.questions = []

    def create_questions(self):
        num_questions = int(input("Enter the number of questions: "))
        for _ in range(num_questions):
            question = input("Enter question: ")
            answer = input("Enter correct answer: ")
            self.questions.append({"question": question, "answer": answer})
        self.send_message("START")

    def send_questions(self):
        for q in self.questions:
            self.send_message(q["question"])
            print("Waiting for responses...")
            correct_answer = q["answer"]
            response = self.receive_message()
            if response.lower().strip() == correct_answer.lower().strip():
                print("Correct answer received!")
            else:
                print("No correct answers!")
        self.send_message("END")

    def run(self):
        print(f"Game PIN: {self.game_pin}")
        self.create_questions()
        # No send_questions() call; it will be handled by the server.
        self.send_message("START")

if __name__ == "__main__":
    host = GameHost()
    host.run()
