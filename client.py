# client.py
import socket
import pickle
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Client:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = None  # Initialize socket as None

    def connect(self):
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((self.host, self.port))
                logging.info("Connected to server")
                return True
            except Exception as e:
                logging.error(f"Error connecting to server: {e}")
                return False
        else:
            logging.info("Already connected")
            return True

    def register(self, username, password):
        if not self.connect():
            return False, "Failed to connect to server"
        request = {'command': 'register', 'username': username, 'password': password}
        self.socket.sendall(pickle.dumps(request))
        response = self.receive_data()
        return response['status'] == 'registered', response['message']

    def login(self, username, password):
        if not self.connect():
            return False, "Failed to connect to server"
        request = {'command': 'login', 'username': username, 'password': password}
        self.socket.sendall(pickle.dumps(request))
        response = self.receive_data()
        return response['status'] == 'authenticated', response['message']

    def send_message(self, recipient, message):
        if not self.connect():
            return False, "Failed to connect to server"
        encoded_message = hamming_encode(message)
        request = {'command': 'send_message', 'recipient': recipient, 'message': encoded_message}
        self.socket.sendall(pickle.dumps(request))
        response = self.receive_data()
        return response['status'] == 'delivered', response['message']

    def receive_data(self):
        data = self.socket.recv(4096)
        if not data:
            return {'status': 'error', 'message': 'No data received from server'}
        return pickle.loads(data)

def run_client(username, password, recipient=None, message=None):
    client = Client()
    success, response = client.login(username, password)
    if not success:
        logging.error(response)
        return
    logging.info(response)
    if recipient and message:
        success, response = client.send_message(recipient, message)
        if success:
            logging.info(response)
        else:
            logging.error(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat Client")
    parser.add_argument("--username", type=str, required=True, help="Your username")
    parser.add_argument("--password", type=str, required=True, help="Your password")
    parser.add_argument("--recipient", type=str, help="Recipient username")
    parser.add_argument("--message", type=str, help="Message to send")
    args = parser.parse_args()

    run_client(args.username, args.password, args.recipient, args.message)
