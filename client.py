import socket
import pickle
import logging
import argparse
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Client:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = None
        self.username = None
        self.messages = []

    def connect(self):
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((self.host, self.port))
                logging.info("Connected to server")
                return True
            except Exception as e:
                logging.error(f"Error connecting to server: {e}")
                self.socket = None
                return False
        else:
            logging.info("Already connected")
            return True

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def register(self, username, password):
        if not self.connect():
            return False, "Failed to connect to server"
        request = {'command': 'register', 'username': username, 'password': password}
        self.socket.sendall(pickle.dumps(request))
        response = self.receive_data()
        if response is None:
            return False, "No response from server"
        return response['status'] == 'registered', response['message']

    def login(self, username, password):
        if not self.connect():
            return False, "Failed to connect to server"
        request = {'command': 'login', 'username': username, 'password': password}
        try:
            self.socket.sendall(pickle.dumps(request))
            response = self.receive_data()
            if response is None:
                return False, "No response from server"
            if response['status'] == 'authenticated':
                self.username = username
                self.start_receiving_messages()
            return response['status'] == 'authenticated', response['message']
        finally:
            self.close()

    def send_message(self, recipient, message):
        if not self.connect():
            return False, "Failed to connect to server"
        request = {'command': 'send_message', 'recipient': recipient, 'message': message, 'sender': self.username}
        self.socket.sendall(pickle.dumps(request))
        response = self.receive_data()
        if response is None:
            return False, "No response from server"
        return response['status'] == 'delivered', response['message']

    def receive_data(self):
        try:
            data = self.socket.recv(1024)
            if not data:
                return None
            return pickle.loads(data)
        except Exception as e:
            logging.error(f"Error receiving data: {e}")
            return None

    def get_user_list(self):
        if not self.connect():
            return []
        request = {'command': 'get_users'}
        self.socket.sendall(pickle.dumps(request))
        response = self.receive_data()
        if response is None or response['status'] != 'success':
            return []
        return response['users']

    def start_receiving_messages(self):
        thread = threading.Thread(target=self.receive_messages)
        thread.daemon = True
        thread.start()

    def receive_messages(self):
        while True:
            try:
                data = self.socket.recv(1024)
                if data:
                    message = pickle.loads(data)
                    self.messages.append(message)
            except Exception as e:
                logging.error(f"Error receiving messages: {e}")
                break
