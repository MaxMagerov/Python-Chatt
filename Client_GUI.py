import tkinter as tk
from tkinter import messagebox, scrolledtext
from client import Client
import threading

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x150")
        self.client = Client()
        
        tk.Label(root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)
        
        tk.Label(root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)
        
        tk.Button(root, text="Login", command=self.login).pack(pady=5)
        tk.Button(root, text="Register", command=self.register_window).pack(pady=5)

    def register_window(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("300x150")
        
        tk.Label(register_window, text="Username:").pack(pady=5)
        self.reg_username_entry = tk.Entry(register_window)
        self.reg_username_entry.pack(pady=5)
        
        tk.Label(register_window, text="Password:").pack(pady=5)
        self.reg_password_entry = tk.Entry(register_window, show="*")
        self.reg_password_entry.pack(pady=5)
        
        tk.Button(register_window, text="Register", command=self.register).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username and password:
            self.root.destroy()
            chat_window = tk.Tk()
            ChatApp(chat_window, username)
            chat_window.mainloop()
        else:
            messagebox.showwarning("Input Error", "Please enter a username and password.")

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        
        if username and password:
            success, message = self.client.register(username, password)
            if success:
                messagebox.showinfo("Registration Success", message)
            else:
                messagebox.showerror("Registration Error", message)
        else:
            messagebox.showwarning("Input Error", "Please enter a username and password.")

class ChatApp:
    def __init__(self, root, username):
        self.client = Client()
        self.username = username
        self.root = root
        self.root.title("Chat Application")

        self.create_chat_window()

    def create_chat_window(self):
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(pady=10)

        self.chat_box = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_box.pack(padx=10, pady=10)

        self.msg_entry = tk.Entry(self.chat_frame, width=50)
        self.msg_entry.pack(side=tk.LEFT, padx=10)
        self.send_btn = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.LEFT)

        self.recipient_entry = tk.Entry(self.chat_frame, width=20)
        self.recipient_entry.pack(side=tk.LEFT, padx=10)
        self.recipient_entry.insert(0, "Recipient")

    def send_message(self):
        recipient = self.recipient_entry.get()
        message = self.msg_entry.get()
        if recipient and message:
            threading.Thread(target=self.send_message_in_background, args=(recipient, message)).start()

    def send_message_in_background(self, recipient, message):
        success = self.client.send_message(recipient, message)
        if success:
            self.root.after(0, self.update_chat_box, recipient, message)
        else:
            messagebox.showerror("Send Error", "Failed to send message.")

    def update_chat_box(self, recipient, message):
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"You to {recipient}: {message}\n")
        self.chat_box.configure(state=tk.DISABLED)
        self.msg_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
