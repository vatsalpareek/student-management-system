import customtkinter as ctk

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, user_data, on_logout):
        super().__init__(parent)
        
        self.label = ctk.CTkLabel(self, text=f"Welcome, {user_data['full_name']}", font=ctk.CTkFont(size=24))
        self.label.pack(pady=20)

        self.logout_btn = ctk.CTkButton(self, text="Logout", command=on_logout)
        self.logout_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Phase 1 Complete: Login Works!\nDashboard implementation is next.", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=20)
