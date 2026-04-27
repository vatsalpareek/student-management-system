import customtkinter as ctk
from tkinter import messagebox, ttk
import db

class MarksFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT: SELECTION & FORM ---
        self.left_frame = ctk.CTkFrame(self, corner_radius=15)
        self.left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(self.left_frame, text="Academic Entry", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        # Student Selection
        search_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20)
        
        self.roll_search = ctk.CTkEntry(search_frame, placeholder_text="Enter Roll No...")
        self.roll_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.roll_search.bind("<Return>", lambda e: self.find_student())
        
        ctk.CTkButton(search_frame, text="Find", width=60, command=self.find_student).pack(side="left")

        # Info Display
        self.info_label = ctk.CTkLabel(self.left_frame, text="Search a student to begin", text_color="gray")
        self.info_label.pack(pady=10)

        # Marks Form (Hidden until student found)
        self.form_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        
        self.subject_var = ctk.StringVar()
        self.marks_var = ctk.StringVar()

        ctk.CTkLabel(self.form_container, text="Subject Name").pack(anchor="w", padx=20)
        ctk.CTkEntry(self.form_container, textvariable=self.subject_var).pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.form_container, text="Marks Obtained").pack(anchor="w", padx=20)
        ctk.CTkEntry(self.form_container, textvariable=self.marks_var).pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(self.form_container, text="Save Marks", command=self.save_marks).pack(fill="x", padx=20, pady=20)

        # --- RIGHT: MARKS LIST & CALCULATION ---
        self.right_frame = ctk.CTkFrame(self, corner_radius=15)
        self.right_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(self.right_frame, text="Marksheet Preview", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        self.tree = ttk.Treeview(self.right_frame, columns=("subject", "marks", "max"), show="headings")
        self.tree.heading("subject", text="Subject")
        self.tree.heading("marks", text="Marks")
        self.tree.heading("max", text="Max Marks")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.summary_label = ctk.CTkLabel(self.right_frame, text="Total: -- | Percentage: --%", font=ctk.CTkFont(size=16, weight="bold"))
        self.summary_label.pack(pady=20)

        self.selected_student = None

    def find_student(self):
        roll = self.roll_search.get()
        results = db.search_students(roll)
        if results:
            self.selected_student = results[0]
            self.info_label.configure(text=f"Student: {self.selected_student['name']} | Dept: {self.selected_student['dept_name']}", text_color="white")
            self.form_container.pack(fill="x")
            self.load_marks()
        else:
            messagebox.showerror("Error", "Student not found!")
            self.form_container.pack_forget()

    def save_marks(self):
        if not self.selected_student: return
        
        sub = self.subject_var.get()
        mks = self.marks_var.get()
        
        if not sub or not mks:
            messagebox.showwarning("Warning", "Fill all fields")
            return
            
        try:
            mks_int = int(mks)
            db.add_marks(self.selected_student['roll_no'], sub, mks_int)
            self.load_marks()
            self.subject_var.set("")
            self.marks_var.set("")
        except ValueError:
            messagebox.showerror("Error", "Marks must be a number")

    def load_marks(self):
        if not self.selected_student: return
        
        self.tree.delete(*self.tree.get_children())
        marks_list = db.get_student_marks(self.selected_student['roll_no'])
        
        total = 0
        count = 0
        for row in marks_list:
            self.tree.insert("", "end", values=(row['subject'], row['marks_obtained'], row['max_marks']))
            total += row['marks_obtained']
            count += 1
            
        if count > 0:
            perc = (total / (count * 100)) * 100
            self.summary_label.configure(text=f"Total: {total} | Percentage: {perc:.2f}%")
        else:
            self.summary_label.configure(text="Total: 0 | Percentage: 0%")
