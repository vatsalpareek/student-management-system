import customtkinter as ctk
from db import initialize_db
from login import LoginFrame

# Set appearance and theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Student Database Management System")
        self.geometry("1100x700")
        self.minsize(1000, 650) # Safety Wall: Prevents cutting off boxes

        # Initialize Database
        initialize_db()

        # Main Container
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.current_frame = None
        self.show_login()

    def show_login(self):
        """Switch to login screen."""
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = LoginFrame(self.container, self.on_login_success)
        self.current_frame.pack(fill="both", expand=True)

    def on_login_success(self, user_data):
        """Switch to dashboard after successful login."""
        print(f"Login successful for {user_data['username']}")
        # We will implement Dashboard in Phase 2
        from dashboard import DashboardFrame
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = DashboardFrame(self.container, user_data, self.show_login)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
