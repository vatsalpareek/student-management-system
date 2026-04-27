import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from students import StudentsFrame
from marks import MarksFrame
from attendance import AttendanceFrame
from reports import ReportsFrame
import db

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, user_data, on_logout):
        super().__init__(parent)
        self.user_data = user_data
        self.on_logout = on_logout

        # Configure Grid Layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1) # Push bottom items

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SMS ADMIN", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Sidebar Buttons
        self.btn_home = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self.select_page("home"), corner_radius=0, height=40, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_home.grid(row=1, column=0, sticky="ew")

        self.btn_students = ctk.CTkButton(self.sidebar_frame, text="Students", command=lambda: self.select_page("students"), corner_radius=0, height=40, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_students.grid(row=2, column=0, sticky="ew")

        self.btn_attendance = ctk.CTkButton(self.sidebar_frame, text="Attendance", command=lambda: self.select_page("attendance"), corner_radius=0, height=40, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_attendance.grid(row=3, column=0, sticky="ew")

        self.btn_marks = ctk.CTkButton(self.sidebar_frame, text="Academic Records", command=lambda: self.select_page("marks"), corner_radius=0, height=40, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_marks.grid(row=4, column=0, sticky="ew")

        self.btn_reports = ctk.CTkButton(self.sidebar_frame, text="Reports", command=lambda: self.select_page("reports"), corner_radius=0, height=40, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_reports.grid(row=5, column=0, sticky="ew")

        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode)
        self.appearance_mode_menu.grid(row=9, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_menu.set("Dark") # Sync dropdown with reality

        # Backup Button
        self.backup_button = ctk.CTkButton(self.sidebar_frame, text="Backup Database", fg_color="gray", command=self.handle_backup)
        self.backup_button.grid(row=10, column=0, padx=20, pady=(0, 10))

        # Logout Button
        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", fg_color="transparent", border_width=1, command=self.on_logout)
        self.logout_button.grid(row=11, column=0, padx=20, pady=20)

        # 2. Main Content Frame
        self.main_content = ctk.CTkFrame(self, corner_radius=15)
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.current_page_frame = None
        self.select_page("home")

    def select_page(self, page_name):
        """Switch between internal pages of the dashboard."""
        # Update button colors for visual feedback
        self.btn_home.configure(fg_color=("gray75", "gray25") if page_name == "home" else "transparent")
        self.btn_students.configure(fg_color=("gray75", "gray25") if page_name == "students" else "transparent")
        self.btn_attendance.configure(fg_color=("gray75", "gray25") if page_name == "attendance" else "transparent")
        self.btn_marks.configure(fg_color=("gray75", "gray25") if page_name == "marks" else "transparent")
        self.btn_reports.configure(fg_color=("gray75", "gray25") if page_name == "reports" else "transparent")

        if self.current_page_frame:
            self.current_page_frame.destroy()

        if page_name == "home":
            self.show_home()
        elif page_name == "students":
            self.show_students()
        elif page_name == "attendance":
            self.show_attendance()
        elif page_name == "marks":
            self.show_marks()
        elif page_name == "reports":
            self.show_reports()

    def show_reports(self):
        """Show the Reports module."""
        self.current_page_frame = ReportsFrame(self.main_content)
        self.current_page_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_students(self):
        """Show the Students Management module."""
        self.current_page_frame = StudentsFrame(self.main_content)
        self.current_page_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_marks(self):
        """Show the Academic Records module."""
        self.current_page_frame = MarksFrame(self.main_content)
        self.current_page_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_attendance(self):
        """Show the Attendance Tracking module."""
        self.current_page_frame = AttendanceFrame(self.main_content)
        self.current_page_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_home(self):
        """Show the main stats dashboard."""
        self.current_page_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.current_page_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Welcome Header
        header = ctk.CTkLabel(self.current_page_frame, text=f"Welcome back, {self.user_data['full_name']}", font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(anchor="w", pady=(0, 20))

        # Real Stats from DB
        stats = db.get_stats()

        # Stats Container
        stats_frame = ctk.CTkFrame(self.current_page_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)

        # Create Stat Cards
        self.create_stat_card(stats_frame, "Total Students", str(stats['students']), 0)
        self.create_stat_card(stats_frame, "Departments", str(stats['depts']), 1)
        self.create_stat_card(stats_frame, "Avg Marks", stats['avg_marks'], 2)
        self.create_stat_card(stats_frame, "System Status", "Live", 3)

    def create_stat_card(self, parent, title, value, column):
        card = ctk.CTkFrame(parent, width=180, height=100, corner_radius=10)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        t_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        t_label.pack(pady=(15, 0))
        
        v_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color="#3B8ED0")
        v_label.pack(pady=(5, 15))

    def show_placeholder(self, title):
        self.current_page_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.current_page_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        label = ctk.CTkLabel(self.current_page_frame, text=title, font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=50)
        
        desc = ctk.CTkLabel(self.current_page_frame, text=f"The {title} module will be implemented in the next phase.", font=ctk.CTkFont(size=14))
        desc.pack()

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)

    def handle_backup(self):
        dest = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database Files", "*.db")])
        if dest:
            if db.backup_db(dest):
                messagebox.showinfo("Success", f"Backup created: {os.path.basename(dest)}")
            else:
                messagebox.showerror("Error", "Backup failed!")
