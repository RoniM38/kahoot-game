import socket
import select
import threading
import time
from game_host import GameHost
from player import Player
from comm_utils import comm_utils

class Server:
    MAX_CLIENTS = 10
    DEFAULT_PORT = 12345

    def __init__(self, host='0.0.0.0', port=DEFAULT_PORT, max_clients=MAX_CLIENTS):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(max_clients)
        
        self.host = None
        self.players = []
        self.scores = {}
        self.game_active = False
        
        print(f"Server listening on {host}:{port}")
    
    def run(self):
        while True:
            ready_to_read, _, _ = select.select([self.server_socket] + [p.player_socket for p in self.players], [], [])
            
            for soc in ready_to_read:
                if soc == self.server_socket:
                    connection_socket, connection_address = self.server_socket.accept()
                    threading.Thread(target=self.manage_connection, args=(connection_socket, connection_address)).start()
                else:
                    self.receive_message(soc)

    def manage_connection(self, connection_socket, connection_address):
        print(f"New connection from: {connection_address}")
        
        self.send_message(connection_socket, "Welcome to Kahoot!")
        self.send_message(connection_socket, "Enter 'h' to host a new game, or 'j' to join an existing game: ")
        
        choice = self.receive_message(connection_socket)
        if choice is None:
            connection_socket.close()
            return

        choice = choice.lower().strip()

        if choice == 'h':
            if self.host is None:
                self.host = GameHost(connection_socket, connection_address)
                self.send_message(connection_socket, f"Game created! Your PIN is: {self.host.game_pin}")
                threading.Thread(target=self.start_game).start()
            else:
                self.send_message(connection_socket, "A game is already running. Try joining instead.")

        elif choice == 'j':
            if self.host is None:
                self.send_message(connection_socket, "No active game. Please wait for a host to create one.")
                connection_socket.close()
                return
            
            self.send_message(connection_socket, "Please enter the game PIN: ")
            pin = self.receive_message(connection_socket).strip()

            if pin == str(self.host.game_pin):
                self.send_message(connection_socket, "Enter your username: ")
                username = self.receive_message(connection_socket)
                player = Player(connection_socket, connection_address, username)
                self.players.append(player)
                self.scores[username] = 0
                self.send_message(connection_socket, "Successfully joined the game!")
            else:
                self.send_message(connection_socket, "Invalid PIN. Try again.")
                connection_socket.close()

    def start_game(self):
        self.game_active = True
        while self.game_active:
            question_data = self.host.get_question()
            if question_data is None:  # No more questions
                self.end_game()
                break
            
            self.send_to_all(question_data['question'])
            self.collect_answers(question_data['answer'])
        
    def collect_answers(self, correct_answer):
        responses = []
        answer_times = {}
        
        for player in self.players:
            answer = self.receive_message(player.player_socket)
            if answer:
                answer_times[player.username] = time.time()  # Capture the time they answered
                responses.append((player.username, answer))
            
        responses.sort(key=lambda x: answer_times.get(x[0], float('inf')))  # Sort the responses by time

        # Update points logic
        self.assign_points(responses, correct_answer)
        self.send_scores()
    
    def assign_points(self, responses, correct_answer):
        points = [10, 5, 3]
        for username, answer in responses:
            if answer.lower().strip() == correct_answer.lower().strip() and points:
                self.scores[username] += points.pop(0)
    
    def send_scores(self):
        scoreboard = "Current Scores:\n" + "\n".join(f"{user}: {score}" for user, score in sorted(self.scores.items(), key=lambda x: x[1], reverse=True))
        self.send_to_all(scoreboard)
    
    def end_game(self):
        self.game_active = False
        final_scores = "Final Results:\n" + "\n".join(f"{user}: {score}" for user, score in sorted(self.scores.items(), key=lambda x: x[1], reverse=True))
        self.send_to_all(final_scores)
        self.host = None
        self.players.clear()
        self.scores.clear()
    
    def send_to_all(self, msg):
        for player in self.players:
            self.send_message(player.player_socket, msg)
    
    def receive_message(self, soc):
        msg = comm_utils.receive_msg(soc)
        if msg is None:
            self.disconnect(soc)
            return None
        return msg

    def send_message(self, soc, msg):
        try:
            msg_size = str(len(msg)).zfill(4)
            complete_msg = msg_size + msg
            soc.send(complete_msg.encode())
        except OSError:
            pass

    def disconnect(self, soc):
        for player in self.players:
            if player.player_socket == soc:
                self.players.remove(player)
                del self.scores[player.username]
                break
        soc.close()

if __name__ == "__main__":
    server = Server()
    server.run()
