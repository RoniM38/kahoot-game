class comm_utils:
    @staticmethod
    def send_message(soc, msg):
        try:
            msg_size = str(len(msg)).zfill(4)
            msg = msg_size + msg
            print(f"Sending message: {msg}")  # Debugging line
            soc.send(msg.encode())
        except Exception as e:
            print(f"Error sending message: {e}")

    @staticmethod
    def receive_msg(soc):
        try:
            length_str = soc.recv(4).decode()
            if not length_str:
                return None
            length = int(length_str)
            msg = soc.recv(length).decode()
            return msg
        except Exception as e:
            return None
