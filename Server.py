import socket
import pickle
import logging
import argparse
import csv
from threading import Thread

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Server:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.users = {}
        self.connections = {}

    def load_users(self, filename):
        try:
            with open(filename, 'r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    self.users[row[0]] = row[1]
            logging.info(f"Loaded {len(self.users)} users from {filename}")
        except FileNotFoundError:
            logging.warning("User database file not found. Starting with empty database.")
        except Exception as e:
            logging.error(f"Error loading user database: {e}")

    def save_users(self, filename):
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                for username, password in self.users.items():
                    writer.writerow([username, password])
            logging.info(f"Saved {len(self.users)} users to {filename}")
        except Exception as e:
            logging.error(f"Error saving user database: {e}")

    def register_user(self, username, password):
        if username in self.users:
            return False, "Username already taken"
        self.users[username] = password
        return True, "Registered successfully"

    def authenticate_user(self, username, password):
        if username in self.users and self.users[username] == password:
            return True, "Login successful"
        return False, "Invalid username or password"

    def send_message(self, sender, recipient, message):
        if recipient in self.connections:
            try:
                conn = self.connections[recipient]
                data = {'sender': sender, 'message': message}
                conn.sendall(pickle.dumps(data))
                return True, "Message delivered successfully"
            except Exception as e:
                logging.error(f"Error sending message to {recipient}: {e}")
                return False, "Error delivering message"
        return False, "Recipient not available"

    def handle_request(self, conn, addr):
        username = None
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                request = pickle.loads(data)
                logging.info(f"Received request: {request}")
                if request['command'] == 'register':
                    username = request['username']
                    password = request['password']
                    success, message = self.register_user(username, password)
                    response = {'status': 'registered' if success else 'error', 'message': message}
                elif request['command'] == 'login':
                    username = request['username']
                    password = request['password']
                    success, message = self.authenticate_user(username, password)
                    if success:
                        self.connections[username] = conn
                    response = {'status': 'authenticated' if success else 'error', 'message': message}
                elif request['command'] == 'send_message':
                    sender = request['sender']
                    recipient = request['recipient']
                    message = request['message']
                    success, message = self.send_message(sender, recipient, message)
                    response = {'status': 'delivered' if success else 'error', 'message': message}
                elif request['command'] == 'get_users':
                    response = {'status': 'success', 'users': list(self.connections.keys())}
                else:
                    response = {'status': 'error', 'message': 'Invalid command'}
                conn.sendall(pickle.dumps(response))
        except Exception as e:
            logging.error(f"Error handling request from {addr}: {e}")
            response = {'status': 'error', 'message': 'Server error'}
            try:
                conn.sendall(pickle.dumps(response))
            except Exception as send_error:
                logging.error(f"Error sending error response: {send_error}")
        finally:
            if username and username in self.connections:
                del self.connections[username]
            conn.close()
            logging.info(f"Closed connection to {addr}")

    def start(self):
        self.socket.listen()
        logging.info(f"Server listening on {self.host}:{self.port}")
        try:
            while True:
                conn, addr = self.socket.accept()
                logging.info(f"Connection from {addr}")
                thread = Thread(target=self.handle_request, args=(conn, addr))
                thread.start()
        except KeyboardInterrupt:
            logging.info("Server stopped by user")
        finally:
            self.save_users('users.csv')
            self.socket.close()

def run_server():
    parser = argparse.ArgumentParser(description="Chat Server")
    parser.add_argument("--host", type=str, default='127.0.0.1', help="Host address")
    parser.add_argument("--port", type=int, default=65432, help="Port number")
    args = parser.parse_args()

    server = Server(host=args.host, port=args.port)
    server.load_users('users.csv')
    server.start()

if __name__ == "__main__":
    run_server()
