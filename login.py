import customtkinter as ctk
from tkinter import messagebox
from db import authenticate

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success

        # Center Frame
        self.login_box = ctk.CTkFrame(self, width=400, height=500, corner_radius=15)
        self.login_box.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        self.label = ctk.CTkLabel(self.login_box, text="Admin Login", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=(40, 20))

        # Username
        self.username_entry = ctk.CTkEntry(self.login_box, width=250, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        # Password
        self.password_entry = ctk.CTkEntry(self.login_box, width=250, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)
        
        # Bind Enter Key to Login
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        self.username_entry.bind("<Return>", lambda e: self.handle_login())

        # Login Button
        self.login_button = ctk.CTkButton(self.login_box, text="Login", width=250, command=self.handle_login)
        self.login_button.pack(pady=20)

        # Info Label
        self.info_label = ctk.CTkLabel(self.login_box, text="Default: admin / admin123", font=ctk.CTkFont(size=12))
        self.info_label.pack(pady=10)

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Validation Error", "All fields are mandatory!")
            return

        user = authenticate(username, password)
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
