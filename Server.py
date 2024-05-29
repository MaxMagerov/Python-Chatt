import socket
import pickle
import logging
import argparse
import csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Server:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.users = {}  # Словарь для хранения пользователей {username: password}

    def load_users(self, filename):
        try:
            with open(filename, 'r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    self.users[row[0]] = row[1]  # username: password
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

    def handle_request(self, conn, addr):
        try:
            data = conn.recv(1024)
            request = pickle.loads(data)
            if request['command'] == 'register':
                username = request['name']
                password = request['password']
                success, message = self.register_user(username, password)
                response = {'status': 'registered' if success else 'error', 'message': message}
                conn.sendall(pickle.dumps(response))
            else:
                response = {'status': 'error', 'message': 'Invalid command'}
                conn.sendall(pickle.dumps(response))
        except Exception as e:
            logging.error(f"Error handling request from {addr}: {e}")
            response = {'status': 'error', 'message': 'Server error'}
            conn.sendall(pickle.dumps(response))

    def start(self):
        self.socket.listen()
        logging.info(f"Server listening on {self.host}:{self.port}")
        try:
            while True:
                conn, addr = self.socket.accept()
                logging.info(f"Connection from {addr}")
                self.handle_request(conn, addr)
                conn.close()
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
