import customtkinter as ctk
from tkinter import messagebox, ttk
import db
from datetime import date

class AttendanceFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- TOP: FILTERS ---
        self.top_frame = ctk.CTkFrame(self, corner_radius=15, height=100)
        self.top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(self.top_frame, text="Daily Attendance", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=20)
        
        self.date_label = ctk.CTkLabel(self.top_frame, text=f"Date: {date.today()}", font=ctk.CTkFont(size=14))
        self.date_label.pack(side="left", padx=20)

        ctk.CTkButton(self.top_frame, text="Submit Attendance", command=self.submit_attendance).pack(side="right", padx=20)

        # --- MAIN: STUDENT LIST ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=1, column=0, sticky="nsew")

        # Scrollable container for student rows
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Student List")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.attendance_vars = {} # {roll_no: IntVar}
        self.load_students()

    def load_students(self):
        students = db.get_all_students()
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        for s in students:
            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=f"{s['roll_no']} - {s['name']}", width=250, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=s['dept_name'], width=150, anchor="w").pack(side="left")
            
            var = ctk.StringVar(value="Present")
            self.attendance_vars[s['roll_no']] = var
            
            ctk.CTkSegmentedButton(row, values=["Present", "Absent"], variable=var).pack(side="right", padx=20)

    def submit_attendance(self):
        today = str(date.today())
        for roll, var in self.attendance_vars.items():
            db.mark_attendance(roll, today, var.get())
        
        messagebox.showinfo("Success", f"Attendance for {today} submitted successfully!")
