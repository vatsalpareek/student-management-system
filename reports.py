import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
import db
import csv
import os

class ReportsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- TOP: EXPORT CONTROLS ---
        self.top_frame = ctk.CTkFrame(self, corner_radius=15, height=80)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(self.top_frame, text="System Reports", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=20)
        
        ctk.CTkButton(self.top_frame, text="Export Student CSV", fg_color="#27AE60", hover_color="#219150", command=self.export_csv).pack(side="right", padx=20)

        # --- LEFT: TOP PERFORMERS ---
        self.left_frame = ctk.CTkFrame(self, corner_radius=15)
        self.left_frame.grid(row=1, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(self.left_frame, text="🏆 Top Students (by Avg Marks)", font=ctk.CTkFont(size=16)).pack(pady=10)
        
        self.top_tree = ttk.Treeview(self.left_frame, columns=("name", "score"), show="headings", height=10)
        self.top_tree.heading("name", text="Student Name")
        self.top_tree.heading("score", text="Avg Score")
        self.top_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # --- RIGHT: ATTENDANCE ALERTS ---
        self.right_frame = ctk.CTkFrame(self, corner_radius=15)
        self.right_frame.grid(row=1, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(self.right_frame, text="⚠️ Low Attendance (< 75%)", font=ctk.CTkFont(size=16)).pack(pady=10)
        
        self.alert_tree = ttk.Treeview(self.right_frame, columns=("name", "perc"), show="headings", height=10)
        self.alert_tree.heading("name", text="Student Name")
        self.alert_tree.heading("perc", text="Attendance %")
        self.alert_tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_data()

    def refresh_data(self):
        # Refresh Top Students
        self.top_tree.delete(*self.top_tree.get_children())
        for row in db.get_top_students():
            self.top_tree.insert("", "end", values=(row['name'], f"{row['avg_score']:.1f}%"))

        # Refresh Attendance Alerts
        self.alert_tree.delete(*self.alert_tree.get_children())
        for row in db.get_attendance_alerts():
            self.alert_tree.insert("", "end", values=(row['name'], f"{row['perc']:.1f}%"))

    def export_csv(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if not filename: return
            
            students = db.get_all_students()
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Roll No", "Name", "Email", "Phone", "Department", "Semester"])
                for s in students:
                    writer.writerow([s['roll_no'], s['name'], s['email'], s['phone'], s['dept_name'], s['semester']])
            
            messagebox.showinfo("Success", f"Data exported successfully to {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
