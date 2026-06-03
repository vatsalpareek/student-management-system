import customtkinter as ctk
from tkinter import messagebox
import db
import re

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success

        # Center Frame
        self.login_box = ctk.CTkFrame(self, width=420, height=540, corner_radius=15)
        self.login_box.place(relx=0.5, rely=0.5, anchor="center")
        
        # Show default login view
        self.show_login_view()

    def clear_box(self):
        for widget in self.login_box.winfo_children():
            widget.destroy()

    def show_login_view(self):
        self.clear_box()

        # Title
        self.label = ctk.CTkLabel(self.login_box, text="Admin Login", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=(30, 20))

        # Username
        self.username_entry = ctk.CTkEntry(self.login_box, width=280, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        # Password
        self.password_entry = ctk.CTkEntry(self.login_box, width=280, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)
        
        # Bind Enter Key to Login
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        self.username_entry.bind("<Return>", lambda e: self.handle_login())

        # Login Button
        self.login_button = ctk.CTkButton(self.login_box, text="Login", width=280, command=self.handle_login)
        self.login_button.pack(pady=15)

        # Register Button / Link
        self.signup_btn = ctk.CTkButton(self.login_box, text="New Admin? Create Account", fg_color="transparent", hover_color=("gray75", "gray25"), width=280, command=self.show_register_view)
        self.signup_btn.pack(pady=5)

        # Forgot Credentials Button / Link
        self.forgot_btn = ctk.CTkButton(self.login_box, text="Forgot Password / Username?", fg_color="transparent", text_color="gray", hover_color=("gray75", "gray25"), font=ctk.CTkFont(size=11), width=280, command=self.show_forgot_view)
        self.forgot_btn.pack(pady=5)

        # Info Label
        self.info_label = ctk.CTkLabel(self.login_box, text="Default: admin / admin123", font=ctk.CTkFont(size=12), text_color="gray")
        self.info_label.pack(pady=15)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Validation Error", "All fields are mandatory!")
            return

        user = db.authenticate(username, password)
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_register_view(self):
        self.clear_box()

        # Title
        self.label = ctk.CTkLabel(self.login_box, text="Register New Admin", font=ctk.CTkFont(size=22, weight="bold"))
        self.label.pack(pady=(20, 15))

        # Full Name
        self.reg_fullname = ctk.CTkEntry(self.login_box, width=280, placeholder_text="Full Name")
        self.reg_fullname.pack(pady=6)

        # Email
        self.reg_email = ctk.CTkEntry(self.login_box, width=280, placeholder_text="Email Address")
        self.reg_email.pack(pady=6)

        # Username
        self.reg_username = ctk.CTkEntry(self.login_box, width=280, placeholder_text="Username")
        self.reg_username.pack(pady=6)

        # Password
        self.reg_password = ctk.CTkEntry(self.login_box, width=280, placeholder_text="Password", show="*")
        self.reg_password.pack(pady=6)

        # Security Question Dropdown
        self.sec_questions = [
            "What is your mother's maiden name?",
            "What was the name of your first pet?",
            "In what city were you born?",
            "What is your favorite book?"
        ]
        self.question_var = ctk.StringVar(value=self.sec_questions[0])
        self.reg_question = ctk.CTkOptionMenu(self.login_box, width=280, values=self.sec_questions, variable=self.question_var)
        self.reg_question.pack(pady=6)

        # Security Answer
        self.reg_answer = ctk.CTkEntry(self.login_box, width=280, placeholder_text="Answer to Security Question")
        self.reg_answer.pack(pady=6)

        # Register Button
        self.register_button = ctk.CTkButton(self.login_box, text="Register", width=280, command=self.handle_register)
        self.register_button.pack(pady=15)

        # Back to Login Button
        self.back_btn = ctk.CTkButton(self.login_box, text="Back to Login", fg_color="transparent", hover_color=("gray75", "gray25"), width=280, command=self.show_login_view)
        self.back_btn.pack(pady=5)

    def handle_register(self):
        fullname = self.reg_fullname.get().strip()
        email = self.reg_email.get().strip()
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        question = self.question_var.get()
        answer = self.reg_answer.get().strip()

        if not fullname or not email or not username or not password or not answer:
            messagebox.showwarning("Validation Error", "All fields are mandatory!")
            return

        # Simple email regex validation
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_pattern, email):
            messagebox.showwarning("Validation Error", "Please enter a valid email address!")
            return

        if len(password) < 6:
            messagebox.showwarning("Validation Error", "Password must be at least 6 characters long!")
            return

        success, msg = db.register_user(username, password, fullname, email, question, answer)
        if success:
            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login_view()
        else:
            messagebox.showerror("Registration Failed", msg)

    def show_forgot_view(self):
        self.clear_box()

        # Title
        self.label = ctk.CTkLabel(self.login_box, text="Credential Recovery", font=ctk.CTkFont(size=22, weight="bold"))
        self.label.pack(pady=(20, 15))

        # Segmented control
        self.recovery_mode = ctk.StringVar(value="Reset Password")
        self.seg_btn = ctk.CTkSegmentedButton(self.login_box, values=["Reset Password", "Find Username"], variable=self.recovery_mode, command=self.toggle_recovery_mode)
        self.seg_btn.pack(pady=10)

        # Dynamic container frame
        self.recovery_container = ctk.CTkFrame(self.login_box, fg_color="transparent")
        self.recovery_container.pack(fill="both", expand=True, padx=20)

        # Bottom Back button
        self.back_btn = ctk.CTkButton(self.login_box, text="Back to Login", fg_color="transparent", hover_color=("gray75", "gray25"), width=280, command=self.show_login_view)
        self.back_btn.pack(pady=15)

        self.toggle_recovery_mode()

    def toggle_recovery_mode(self, val=None):
        # Clear recovery container
        for widget in self.recovery_container.winfo_children():
            widget.destroy()

        mode = self.recovery_mode.get()
        if mode == "Reset Password":
            # 1. Username field
            self.rec_username = ctk.CTkEntry(self.recovery_container, width=280, placeholder_text="Enter Username")
            self.rec_username.pack(pady=5)

            # 2. Get Question Button
            self.get_q_btn = ctk.CTkButton(self.recovery_container, text="Retrieve Security Question", command=self.fetch_security_question)
            self.get_q_btn.pack(pady=5)

            # 3. Label to display question
            self.q_display_label = ctk.CTkLabel(self.recovery_container, text="", text_color="yellow", wraplength=260)
            self.q_display_label.pack(pady=5)

            # 4. Answer field (disabled initially)
            self.rec_answer = ctk.CTkEntry(self.recovery_container, width=280, placeholder_text="Security Answer", state="disabled")
            self.rec_answer.pack(pady=5)

            # 5. New Password field (disabled initially)
            self.rec_new_password = ctk.CTkEntry(self.recovery_container, width=280, placeholder_text="New Password", show="*", state="disabled")
            self.rec_new_password.pack(pady=5)

            # 6. Reset button (disabled initially)
            self.reset_btn = ctk.CTkButton(self.recovery_container, text="Reset Password", state="disabled", command=self.handle_password_reset)
            self.reset_btn.pack(pady=10)

        else:
            # Retrieve Username mode
            self.rec_email = ctk.CTkEntry(self.recovery_container, width=280, placeholder_text="Enter Registered Email")
            self.rec_email.pack(pady=10)

            self.find_user_btn = ctk.CTkButton(self.recovery_container, text="Find Username", command=self.handle_find_username)
            self.find_user_btn.pack(pady=10)

    def fetch_security_question(self):
        username = self.rec_username.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Please enter a username!")
            return

        question = db.get_user_security_question(username)
        if question:
            self.q_display_label.configure(text=f"Question:\n{question}")
            self.rec_answer.configure(state="normal")
            self.rec_new_password.configure(state="normal")
            self.reset_btn.configure(state="normal")
        else:
            messagebox.showerror("Error", "Username not found or no security question set.")
            self.q_display_label.configure(text="")
            self.rec_answer.configure(state="disabled")
            self.rec_new_password.configure(state="disabled")
            self.reset_btn.configure(state="disabled")

    def handle_password_reset(self):
        username = self.rec_username.get().strip()
        answer = self.rec_answer.get().strip()
        new_password = self.rec_new_password.get()

        if not answer or not new_password:
            messagebox.showwarning("Validation Error", "All fields are mandatory!")
            return

        if len(new_password) < 6:
            messagebox.showwarning("Validation Error", "Password must be at least 6 characters long!")
            return

        success, msg = db.reset_password(username, answer, new_password)
        if success:
            messagebox.showinfo("Success", msg)
            self.show_login_view()
        else:
            messagebox.showerror("Error", msg)

    def handle_find_username(self):
        email = self.rec_email.get().strip()
        if not email:
            messagebox.showwarning("Warning", "Please enter your email!")
            return

        username = db.retrieve_username_by_email(email)
        if username:
            messagebox.showinfo("Username Found", f"The username associated with this email is:\n\n{username}")
            self.show_login_view()
        else:
            messagebox.showerror("Error", "No account registered with this email address.")
