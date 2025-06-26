# main.py
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
from generator import generate_qr
from scanner import main_ui

def create_qr_gui():
    user_id = simpledialog.askstring("Input", "Enter Unique ID:")
    if user_id:
        generate_qr(user_id)
        messagebox.showinfo("Success", "QR code generated!")

def view_logs():
    try:
        df = pd.read_csv("attendance.csv")
        top = tk.Toplevel()
        top.title("Attendance Logs")
        text = tk.Text(top, wrap='none', bg='white', fg='black', font=('Courier New', 10))
        text.insert(tk.END, df.to_string(index=False))
        text.pack(expand=True, fill='both')
    except FileNotFoundError:
        messagebox.showwarning("No Data", "Attendance file not found.")

def export_excel():
    try:
        df = pd.read_csv("attendance.csv")
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if filepath:
            df.to_excel(filepath, index=False)
            messagebox.showinfo("Exported", f"Data saved to {filepath}")
    except FileNotFoundError:
        messagebox.showwarning("No Data", "Attendance file not found.")

root = tk.Tk()
root.title("Smart Attendance Logger")
root.geometry("900x900")
root.resizable(False, False)

bg_image = Image.open("background1.png").resize((900, 900))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

frame = tk.Frame(root, bg='#f2f2f2', bd=2)
frame.place(relx=0.5, rely=0.5, anchor='center')

tk.Label(frame, text="Smart Attendance Logger", font=("Helvetica", 24, "bold"), bg='#f2f2f2').pack(pady=20)

btn_style = {"font": ("Helvetica", 14), "width": 25, "padx": 10, "pady": 10, "bg": "#4CAF50", "fg": "white", "bd": 0, "activebackground": "#45a049"}

tk.Button(frame, text="Start QR Scan", command=main_ui, **btn_style).pack(pady=10)
tk.Button(frame, text="View Logs", command=view_logs, **btn_style).pack(pady=10)
tk.Button(frame, text="Generate QR Code", command=create_qr_gui, **btn_style).pack(pady=10)
tk.Button(frame, text="Export as Excel", command=export_excel, **btn_style).pack(pady=10)

root.mainloop()
