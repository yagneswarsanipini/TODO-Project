# ================================
# IMPORT REQUIRED MODULES
# ================================
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


# ================================
# DATABASE SETUP
# ================================
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    priority TEXT,
    deadline TEXT,
    status TEXT
)
""")
conn.commit()


# ================================
# FUNCTION: ADD TASK
# ================================
def add_task():
    name = entry_name.get()
    priority = priority_var.get()
    deadline = entry_deadline.get()

    if not name or not deadline:
        messagebox.showwarning("Error", "All fields required")
        return

    cursor.execute(
        "INSERT INTO tasks (name, priority, deadline, status) VALUES (?, ?, ?, ?)",
        (name, priority, deadline, "pending")
    )
    conn.commit()

    messagebox.showinfo("Success", "Task added!")
    clear_fields()
    view_tasks()


# ================================
# FUNCTION: VIEW TASKS (WITH SEARCH)
# ================================
def view_tasks():
    for row in tree.get_children():
        tree.delete(row)

    search_text = search_var.get()

    if search_text:
        cursor.execute("SELECT * FROM tasks WHERE name LIKE ?", ('%' + search_text + '%',))
    else:
        cursor.execute("SELECT * FROM tasks")

    tasks = cursor.fetchall()

    for t in tasks:
        color = "black"
        if t[2] == "High":
            color = "red"
        elif t[2] == "Medium":
            color = "orange"
        elif t[2] == "Low":
            color = "green"

        tree.insert("", tk.END, values=t, tags=(color,))

    tree.tag_configure("red", foreground="red")
    tree.tag_configure("orange", foreground="orange")
    tree.tag_configure("green", foreground="green")


# ================================
# FUNCTION: MARK TASK AS DONE
# ================================
def mark_done():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Error", "Select a task")
        return

    item = tree.item(selected[0])
    task_id = item["values"][0]

    cursor.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()

    view_tasks()


# ================================
# FUNCTION: DELETE TASK
# ================================
def delete_task():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Error", "Select a task")
        return

    item = tree.item(selected[0])
    task_id = item["values"][0]

    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

    view_tasks()
    messagebox.showinfo("Deleted", "Task deleted")


# ================================
# FUNCTION: AUTO UPDATE PRIORITY
# ================================
def auto_update_priority():
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("SELECT id, deadline, priority FROM tasks WHERE status='pending'")
    tasks = cursor.fetchall()

    for t in tasks:
        task_id, deadline, priority = t

        if deadline < today:
            if priority == "Low":
                new_priority = "Medium"
            elif priority == "Medium":
                new_priority = "High"
            else:
                new_priority = "High"

            cursor.execute(
                "UPDATE tasks SET priority=? WHERE id=?",
                (new_priority, task_id)
            )

    conn.commit()
    view_tasks()
    messagebox.showinfo("Updated", "Priority updated for overdue tasks")


# ================================
# FUNCTION: CLEAR INPUT FIELDS
# ================================
def clear_fields():
    entry_name.delete(0, tk.END)
    entry_deadline.delete(0, tk.END)
    priority_var.set("Low")


# ================================
# UI SETUP
# ================================
root = tk.Tk()
root.title("Smart To-Do Tracker")
root.geometry("650x550")


# ================================
# INPUT FRAME
# ================================
frame = tk.Frame(root)
frame.pack(pady=10)

# Task Name
tk.Label(frame, text="Task Name").grid(row=0, column=0)
entry_name = tk.Entry(frame, width=25)
entry_name.grid(row=0, column=1)

# Priority Dropdown
tk.Label(frame, text="Priority").grid(row=1, column=0)
priority_var = tk.StringVar()
priority_dropdown = ttk.Combobox(frame, textvariable=priority_var, state="readonly")
priority_dropdown['values'] = ("Low", "Medium", "High")
priority_dropdown.current(0)
priority_dropdown.grid(row=1, column=1)

# Deadline
tk.Label(frame, text="Deadline (YYYY-MM-DD)").grid(row=2, column=0)
entry_deadline = tk.Entry(frame)
entry_deadline.grid(row=2, column=1)

# Buttons
tk.Button(frame, text="Add Task", width=20, command=add_task).grid(row=3, column=0, pady=5)
tk.Button(frame, text="Mark Done", width=20, command=mark_done).grid(row=3, column=1)
tk.Button(frame, text="Auto Update", width=20, command=auto_update_priority).grid(row=4, column=0)
tk.Button(frame, text="Delete Task", width=20, command=delete_task).grid(row=4, column=1)


# ================================
# SEARCH BAR
# ================================
search_var = tk.StringVar()

tk.Label(root, text="Search Task").pack()
search_entry = tk.Entry(root, textvariable=search_var, width=30)
search_entry.pack()

tk.Button(root, text="Search", command=view_tasks).pack(pady=5)


# ================================
# TABLE (TREEVIEW)
# ================================
columns = ("ID", "Task", "Priority", "Deadline", "Status")
tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)

tree.pack(pady=20)


# ================================
# INITIAL LOAD
# ================================
view_tasks()


# ================================
# RUN APPLICATION
# ================================
root.mainloop()


# ================================
# CLOSE DATABASE
# ================================
conn.close()