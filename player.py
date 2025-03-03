from client import Client

class Player(Client):
    def __init__(self, server_ip='127.0.0.1', port=12345):
        super().__init__(server_ip, port)
        self.username = None

    def register(self):
        pin = input("Enter game PIN: ")
        self.send_message(pin)
        response = self.receive_message()
        
        if response is None:
            print("Failed to receive response from server.")
            return False
        
        if "Enter your username" in response:
            print(response)
            self.username = input("Enter your username: ")
            self.send_message(self.username)
            print(self.receive_message())  # Successfully joined message
            return True
        else:
            print("Invalid PIN. Could not join the game.")
            return False

    def play_game(self):
        while True:
            question = self.receive_message()
            if "Final Results" in question:
                print(question)
                break
            print(f"Question: {question}")
            answer = input("Enter your answer: ")
            self.send_message(answer)
            print(self.receive_message())  # Score update

    def run(self):
        if self.register():
            self.play_game()
        self.disconnect()

if __name__ == "__main__":
    player = Player()
    player.run()
