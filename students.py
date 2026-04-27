import customtkinter as ctk
from tkinter import ttk, messagebox
import db

class StudentsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT: ENTRY FORM ---
        self.form_frame = ctk.CTkFrame(self, corner_radius=15)
        self.form_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")

        ctk.CTkLabel(self.form_frame, text="Student Information", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        self.vars = {
            "roll_no": ctk.StringVar(),
            "name": ctk.StringVar(),
            "email": ctk.StringVar(),
            "phone": ctk.StringVar(),
            "dob": ctk.StringVar(),
            "gender": ctk.StringVar(value="Male"),
            "address": ctk.StringVar(),
            "dept": ctk.StringVar(),
            "semester": ctk.StringVar(value="Semester 1")
        }

        # Form Fields
        self.create_field("Roll Number", self.vars["roll_no"])
        self.create_field("Full Name", self.vars["name"])
        self.create_field("Email", self.vars["email"])
        self.create_field("Phone", self.vars["phone"])
        self.create_field("DOB (YYYY-MM-DD)", self.vars["dob"])
        
        # Gender Selection
        ctk.CTkLabel(self.form_frame, text="Gender").pack(anchor="w", padx=20)
        ctk.CTkSegmentedButton(self.form_frame, values=["Male", "Female", "Other"], variable=self.vars["gender"]).pack(fill="x", padx=20, pady=(0, 10))

        # Department Selection
        ctk.CTkLabel(self.form_frame, text="Department").pack(anchor="w", padx=20)
        self.dept_dropdown = ctk.CTkOptionMenu(self.form_frame, variable=self.vars["dept"])
        self.dept_dropdown.pack(fill="x", padx=20, pady=(0, 10))
        self.refresh_departments()

        # Semester
        ctk.CTkLabel(self.form_frame, text="Semester").pack(anchor="w", padx=20)
        ctk.CTkOptionMenu(self.form_frame, values=["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6"], variable=self.vars["semester"]).pack(fill="x", padx=20, pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(btn_frame, text="Add", width=100, command=self.add_student).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Update", width=100, command=self.update_student).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Delete", width=100, fg_color="#E74C3C", hover_color="#C0392B", command=self.delete_student).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Clear", width=100, fg_color="gray", hover_color="#555", command=self.clear_fields).grid(row=1, column=1, padx=5, pady=5)

        # --- RIGHT: TABLE VIEW ---
        self.table_frame = ctk.CTkFrame(self, corner_radius=15)
        self.table_frame.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")

        # Search Bar
        search_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=20)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by Roll No or Name...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(search_frame, text="Search", width=80, command=self.search).pack(side="left")
        ctk.CTkButton(search_frame, text="Reset", width=80, fg_color="gray", command=self.load_students).pack(side="left", padx=5)

        # Table (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.map("Treeview", background=[('selected', '#3B8ED0')])

        self.tree = ttk.Treeview(self.table_frame, columns=("roll", "name", "email", "dept", "sem"), show="headings")
        self.tree.heading("roll", text="Roll No")
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="Email")
        self.tree.heading("dept", text="Department")
        self.tree.heading("sem", text="Semester")
        
        self.tree.column("roll", width=80)
        self.tree.column("name", width=150)
        self.tree.column("email", width=150)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.tree.bind("<<TreeviewSelect>>", self.get_cursor)

        self.load_students()

    def create_field(self, label, variable):
        ctk.CTkLabel(self.form_frame, text=label).pack(anchor="w", padx=20)
        ctk.CTkEntry(self.form_frame, variable=variable).pack(fill="x", padx=20, pady=(0, 10))

    def refresh_departments(self):
        depts = db.get_departments()
        self.dept_map = {d['name']: d['id'] for d in depts}
        names = list(self.dept_map.keys())
        if names:
            self.dept_dropdown.configure(values=names)
            self.vars["dept"].set(names[0])

    def add_student(self):
        data = (
            self.vars["roll_no"].get(),
            self.vars["name"].get(),
            self.vars["email"].get(),
            self.vars["phone"].get(),
            self.vars["dob"].get(),
            self.vars["gender"].get(),
            self.vars["address"].get(),
            self.dept_map.get(self.vars["dept"].get()),
            self.vars["semester"].get()
        )
        if not data[0] or not data[1]:
            messagebox.showwarning("Error", "Roll No and Name are mandatory!")
            return
            
        success, msg = db.add_student(data)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_students()
            self.clear_fields()
        else:
            messagebox.showerror("Error", msg)

    def load_students(self):
        self.tree.delete(*self.tree.get_children())
        for row in db.get_all_students():
            self.tree.insert("", "end", values=(row['roll_no'], row['name'], row['email'], row['dept_name'], row['semester']))

    def search(self):
        query = self.search_entry.get()
        self.tree.delete(*self.tree.get_children())
        for row in db.search_students(query):
            self.tree.insert("", "end", values=(row['roll_no'], row['name'], row['email'], row['dept_name'], row['semester']))

    def get_cursor(self, event):
        cursor_row = self.tree.focus()
        contents = self.tree.item(cursor_row)
        row = contents['values']
        if row:
            # We need to fetch full details from DB or store more in tree
            self.vars["roll_no"].set(row[0])
            self.vars["name"].set(row[1])
            self.vars["email"].set(row[2])
            self.vars["dept"].set(row[3])
            self.vars["semester"].set(row[4])

    def update_student(self):
        # Implementation similar to add but with UPDATE query
        # For brevity in Phase 3, we'll focus on Add/Delete/View
        # and full Update in next iteration if needed
        messagebox.showinfo("Info", "Update feature - Use Delete and Add for now. Full update coming in next polish!")

    def delete_student(self):
        roll = self.vars["roll_no"].get()
        if not roll:
            messagebox.showwarning("Error", "Select a student to delete!")
            return
            
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete student {roll}?"):
            db.delete_student(roll)
            self.load_students()
            self.clear_fields()

    def clear_fields(self):
        for var in self.vars.values():
            if isinstance(var, ctk.StringVar):
                var.set("")
        self.vars["gender"].set("Male")
        self.vars["semester"].set("Semester 1")
