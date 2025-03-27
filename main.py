import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk
import sqlite3
import re
import datetime

# --- Database Setup ---
conn = sqlite3.connect('students.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    name TEXT,
    gender TEXT,
    former_class INTEGER,
    current_class INTEGER,
    phone TEXT,
    health_issues TEXT,
    submission_date TEXT
)
''')
conn.commit()

# --- Submission Function with Validations ---
def submit_data():
    student_id = sid_entry.get().strip()
    name = name_entry.get().strip()
    gender = gender_var.get().strip()
    former_class = former_class_entry.get().strip()
    current_class = current_class_entry.get().strip()
    phone = phone_entry.get().strip()
    health_issues = health_text.get("1.0", tk.END).strip()

    # Check required fields
    if not student_id or not name or not gender or not former_class or not current_class or not phone:
        messagebox.showerror("Input Error", "Please fill in all required fields.")
        return

    # Validate name: only letters and spaces
    if not re.fullmatch(r'[A-Za-z\s]+', name):
        messagebox.showerror("Input Error", "Name must contain only letters and spaces.")
        return

    # Validate phone: exactly 10 digits
    if not re.fullmatch(r'\d{10}', phone):
        messagebox.showerror("Input Error", "Phone Number must be exactly 10 digits.")
        return
    if not re.fullmatch(r'\d+', student_id):
        messagebox.showerror("Input Error", "Student ID must contain only numbers.")
        return

    # Validate former and current class: must be integer from 1 to 12
    try:
        former_class_int = int(former_class)
        current_class_int = int(current_class)
        if not (1 <= former_class_int <= 12):
            messagebox.showerror("Input Error", "Former Class must be an integer between 1 and 12.")
            return
        if not (1 <= current_class_int <= 12):
            messagebox.showerror("Input Error", "Current Class must be an integer between 1 and 12.")
            return
    except ValueError:
        messagebox.showerror("Input Error", "Former Class and Current Class must be integers.")
        return

    # Validate health issues: should not contain digits if provided (optional field)
    if health_issues and re.search(r'\d', health_issues):
        messagebox.showerror("Input Error", "Health Issues should be written in words (no numbers allowed).")
        return

    # Record the current timestamp
    submission_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert into the database
    c.execute('''
        INSERT INTO students (student_id, name, gender, former_class, current_class, phone, health_issues, submission_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, name, gender, former_class_int, current_class_int, phone, health_issues, submission_date))
    conn.commit()

    messagebox.showinfo("Success", "Registration successful!")

    # Clear fields
    sid_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    gender_var.set("")
    former_class_entry.delete(0, tk.END)
    current_class_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    health_text.delete("1.0", tk.END)

    refresh_dashboard()


# --- Delete Function ---
def delete_selected():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a record to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected record?")
    if confirm:
        item = tree.item(selected_item)
        record_id = item["values"][0]
        c.execute("DELETE FROM students WHERE id = ?", (record_id,))
        conn.commit()
        refresh_dashboard()
        messagebox.showinfo("Deleted", "Record has been deleted.")


# --- Dashboard Refresh Function ---
def refresh_dashboard():
    for item in tree.get_children():
        tree.delete(item)
    c.execute(
        "SELECT id, student_id, name, gender, former_class, current_class, phone, health_issues, submission_date FROM students")
    rows = c.fetchall()
    for row in rows:
        tree.insert('', tk.END, values=row)


# --- GUI Setup ---
root = tk.Tk()
root.title("Enhanced Student Registration Dashboard")
root.geometry("1000x700")

# Create Notebook for tabbed interface
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Registration Tab
registration_frame = ttk.Frame(notebook)
notebook.add(registration_frame, text="Registration")

# Dashboard Tab
dashboard_frame = ttk.Frame(notebook)
notebook.add(dashboard_frame, text="Dashboard")

# ----- Registration Tab Layout -----
reg_inner = ttk.Frame(registration_frame, padding=20)
reg_inner.pack(expand=True, fill='both')

# Row 0: Student ID and Name
ttk.Label(reg_inner, text="Student ID (Identification):").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
sid_entry = ttk.Entry(reg_inner, width=30)
sid_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(reg_inner, text="Name:").grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
name_entry = ttk.Entry(reg_inner, width=30)
name_entry.grid(row=0, column=3, padx=10, pady=5)

# Row 1: Gender and Former Class
ttk.Label(reg_inner, text="Gender:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
gender_var = tk.StringVar()
gender_frame = ttk.Frame(reg_inner)
gender_frame.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
ttk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side=tk.LEFT, padx=5)
ttk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side=tk.LEFT, padx=5)

ttk.Label(reg_inner, text="Former Class (1-12):").grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
former_class_entry = ttk.Entry(reg_inner, width=30)
former_class_entry.grid(row=1, column=3, padx=10, pady=5)

# Row 2: Current Class and Phone Number
ttk.Label(reg_inner, text="Current Class (1-12):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
current_class_entry = ttk.Entry(reg_inner, width=30)
current_class_entry.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(reg_inner, text="Phone Number (10 digits):").grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)
phone_entry = ttk.Entry(reg_inner, width=30)
phone_entry.grid(row=2, column=3, padx=10, pady=5)

# Row 3: Health Issues (multiline)
ttk.Label(reg_inner, text="Health Related Issues (no numbers):").grid(row=3, column=0, padx=10, pady=5, sticky=tk.NW)
health_text = scrolledtext.ScrolledText(reg_inner, width=70, height=5, wrap=tk.WORD)
health_text.grid(row=3, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

# Row 4: Register Button
submit_button = ttk.Button(reg_inner, text="Register", command=submit_data)
submit_button.grid(row=4, column=0, columnspan=4, pady=20)

# ----- Dashboard Tab Layout -----
dash_inner = ttk.Frame(dashboard_frame, padding=20)
dash_inner.pack(expand=True, fill='both')

# Treeview to display student information
columns = ("DB_ID", "Student_ID", "Name", "Gender", "Former_Class", "Current_Class", "Phone", "Health_Issues", "Submission_Date")
tree = ttk.Treeview(dash_inner, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor=tk.CENTER)
tree.pack(expand=True, fill='both', pady=10)

refresh_dashboard()

root.mainloop()
conn.close()
