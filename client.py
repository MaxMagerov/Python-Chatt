import socket
import pickle
import logging
import os
import argparse
from hamming import hamming_encode, hamming_decode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Client:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def register(self, name, password):
        request = {'command': 'register', 'name': name, 'password': password}
        self.socket.sendall(pickle.dumps(request))
        response = pickle.loads(self.socket.recv(1024))
        if response['status'] == 'registered':
            self.id = response['id']
            logging.info(f'Registered with ID {self.id}')
            return True, response['message']
        else:
            logging.error(response['message'])
            return False, response['message']

    def send_message(self, recipient, message):
        encoded_message = hamming_encode(message)
        request = {'command': 'send_message', 'recipient': recipient, 'message': encoded_message}
        self.socket.sendall(pickle.dumps(request))
        response = pickle.loads(self.socket.recv(1024))
        if response['status'] == 'delivered':
            logging.info('Message delivered successfully')
            return True
        else:
            logging.error(response['message'])
            return False

def run_client(name, password, recipient=None, message=None):
    client = Client()
    success, message = client.register(name, password)
    if success and recipient and message:
        client.send_message(recipient, message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat Client")
    parser.add_argument("--name", type=str, required=True, help="Your username")
    parser.add_argument("--password", type=str, required=True, help="Your password")
    parser.add_argument("--recipient", type=str, help="Recipient username")
    parser.add_argument("--message", type=str, help="Message to send")
    args = parser.parse_args()

    run_client(args.name, args.password, args.recipient, args.message)
