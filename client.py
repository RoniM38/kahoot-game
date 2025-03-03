import socket
from comm_utils import comm_utils

class Client:
    DEFAULT_PORT = 12345
    LOCALHOST = '127.0.0.1'

    def __init__(self, server_ip=LOCALHOST, port=DEFAULT_PORT):
        self.player_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_socket.connect((server_ip, port))
        print(f"Connected to server at {server_ip}:{port}")

    def send_message(self, msg):
        comm_utils.send_message(self.player_socket, msg)

    def receive_message(self):
        return comm_utils.receive_msg(self.player_socket)

    def disconnect(self):
        self.send_message("Disconnecting...")
        self.player_socket.close()

    def run(self):
        print(self.receive_message())
        print(self.receive_message())
        choice = input("Enter choice: ")
        self.send_message(choice)

        if choice.lower().strip() == 'h':
            print(self.receive_message())
        elif choice.lower().strip() == 'j':
            print(self.receive_message())
            pin = input("Enter game PIN: ")
            self.send_message(pin)
            
            response = self.receive_message()
            if "Enter your username" in response:
                print(response)
                username = input("Enter your username: ")
                self.send_message(username)
                print(self.receive_message())  # Successfully joined message
                self.play_game()
            else:
                print(response)  # Invalid PIN message
                self.disconnect()

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

if __name__ == "__main__":
    client = Client()
    client.run()
