import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from client import Client
import threading

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.client = Client()

        self.username_label = ttk.Label(root, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = ttk.Entry(root)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = ttk.Label(root, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = ttk.Entry(root, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_button = ttk.Button(root, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.register_button = ttk.Button(root, text="Register", command=self.register)
        self.register_button.grid(row=3, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = self.client.login(username, password)
        if success:
            self.open_chat_window()
        else:
            messagebox.showerror("Login Failed", message)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = self.client.register(username, password)
        if success:
            messagebox.showinfo("Registration Successful", message)
        else:
            messagebox.showerror("Registration Failed", message)

    def open_chat_window(self):
        self.root.destroy()
        ChatWindow(self.client)

class ChatWindow:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("Chat")

        self.users_listbox = tk.Listbox(self.root)
        self.users_listbox.grid(row=0, column=0, padx=10, pady=10)

        self.chat_display = scrolledtext.ScrolledText(self.root)
        self.chat_display.grid(row=0, column=1, padx=10, pady=10)

        self.message_entry = ttk.Entry(self.root)
        self.message_entry.grid(row=1, column=1, padx=10, pady=10)

        self.send_button = ttk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.grid(row=2, column=1, padx=10, pady=10)

        self.update_users()
        self.update_messages()

        self.root.mainloop()

    def update_users(self):
        users = self.client.get_user_list()
        self.users_listbox.delete(0, tk.END)
        for user in users:
            self.users_listbox.insert(tk.END, user)
        self.root.after(5000, self.update_users)  # Update user list every 5 seconds

    def update_messages(self):
        for message in self.client.messages:
            self.chat_display.insert(tk.END, f"{message['sender']}: {message['message']}\n")
        self.client.messages.clear()
        self.root.after(1000, self.update_messages)  # Check for new messages every second

    def send_message(self):
        recipient = self.users_listbox.get(tk.ACTIVE)
        message = self.message_entry.get()
        if recipient and message:
            self.client.send_message(recipient, message)
            self.message_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    login_window = LoginWindow(root)
    root.mainloop()
