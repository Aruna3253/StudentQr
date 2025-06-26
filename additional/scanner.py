# scanner.py
import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
import csv
import os
import numpy as np
import pandas as pd
import textwrap
from tkinter import filedialog, messagebox
import tkinter as tk

import os
import pandas as pd
print("[DEBUG] Current Working Directory:", os.getcwd())


def get_student_info(user_id):
    user_id = str(user_id).strip()

    if not os.path.exists("student.csv"):
        print("[ERROR] student.csv file not found!")
        return None

    try:
        df = pd.read_csv("student.csv", dtype=str)
        print("[DEBUG] students.csv loaded successfully")
    except Exception as e:
        print("[ERROR] Failed to load students.csv:", e)
        return None

    df["ID"] = df["ID"].astype(str).str.strip()
    print("[DEBUG] All IDs from CSV:", df["ID"].tolist())
    print("[DEBUG] Looking for ID:", user_id)

    match = df[df["ID"] == user_id]
    print("[DEBUG] Match row(s):\n", match)

    if not match.empty:
        return match.iloc[0].to_dict()
    else:
        return None




def get_today_status(user_id):
    if not os.path.exists("attendance.csv"):
        return None
    df = pd.read_csv("attendance.csv", dtype=str)
    today = datetime.now().strftime("%Y-%m-%d")
    logs = df[(df["ID"] == str(user_id)) & (df["Date"] == today)]
    if "OUT" in logs["Status"].values:
        return "DONE"
    elif "IN" in logs["Status"].values:
        return "IN"
    return None

def calculate_stay_duration(user_id):
    df = pd.read_csv("attendance.csv", dtype=str)
    today = datetime.now().strftime("%Y-%m-%d")
    logs = df[(df["ID"] == user_id) & (df["Date"] == today)]

    in_time = out_time = None
    for _, row in logs.iterrows():
        if row["Status"] == "IN":
            in_time = datetime.strptime(row["Time"], "%H:%M:%S")
        elif row["Status"] == "OUT":
            out_time = datetime.strptime(row["Time"], "%H:%M:%S")

    if in_time and out_time:
        return str(out_time - in_time)
    return None

def log_attendance(student, status):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    user_id = student["ID"]
    name = student["Name"]
    _class = student["Class"]
    contact = student["Contact"]

    # Cutoff check
    if status == "IN" and now.time() > datetime.strptime("16:00:00", "%H:%M:%S").time():
        messagebox.showwarning("Late", "Attendance is closed after 4 PM.")
        return False

    # File creation
    if not os.path.exists("attendance.csv"):
        with open("attendance.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Class", "Contact", "Date", "Time", "Status", "Remarks"])

    # Remarks
    remarks = ""
    if status == "IN" and now.time() > datetime.strptime("10:00:00", "%H:%M:%S").time():
        remarks = "Late Entry"
    elif status == "OUT" and now.time() < datetime.strptime("15:00:00", "%H:%M:%S").time():
        remarks = "Left Early"

    with open("attendance.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, name, _class, contact, date, time, status, remarks])

    print(f"[{status}] {name} at {time}")
    return True

def draw_wrapped_text(img, text, origin, max_width=35, font=cv2.FONT_HERSHEY_SIMPLEX,
                      font_scale=0.7, color=(0, 0, 255), thickness=2, line_height=25):
    lines = textwrap.wrap(text, width=max_width)
    x, y = origin
    for i, line in enumerate(lines):
        cv2.putText(img, line, (x, y + i * line_height), font, font_scale, color, thickness)

def process_qr(data, frame, pts):
    try:
        user_id = data.strip()
        print(f"[DEBUG] Scanned ID: '{user_id}'")
        student = get_student_info(user_id)
        if not student:
            raise ValueError("Student not found.")

        name = student["Name"]
        label = f"Name: {name}\nID: {user_id}"
        draw_wrapped_text(frame, label, (pts[0][0], pts[0][1] - 50))

        status = get_today_status(user_id)
        if status == "DONE":
            draw_wrapped_text(frame, "IN & OUT already marked", (pts[0][0], pts[0][1] + 30), color=(0, 0, 255))
            messagebox.showinfo("Info", "IN and OUT already recorded for today.")
        elif status == "IN":
            if log_attendance(student, "OUT"):
                duration = calculate_stay_duration(user_id)
                draw_wrapped_text(frame, f"OUT marked\nStay: {duration}", (pts[0][0], pts[0][1] + 30), color=(255, 140, 0))
                messagebox.showinfo("OUT", f"Goodbye {name}, stayed {duration}.")
        else:
            if log_attendance(student, "IN"):
                draw_wrapped_text(frame, "IN marked", (pts[0][0], pts[0][1] + 30), color=(0, 255, 0))
                messagebox.showinfo("IN", f"Welcome {name}, IN marked.")
    except Exception as e:
        draw_wrapped_text(frame, "Invalid QR Format", (pts[0][0], pts[0][1] - 20))
        print("QR Error:", e)

def image_scan_mode():
    tk.Tk().withdraw()
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        decoded = decode(image)
        for obj in decoded:
            data = obj.data.decode("utf-8")
            pts = [tuple(p) for p in obj.polygon]
            cv2.polylines(image, [np.array(pts, dtype=np.int32)], True, (0, 255, 0), 2)
            process_qr(data, image, pts)
        cv2.imshow("Image QR Scanner", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def live_scan_mode():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        decoded = decode(frame)
        for obj in decoded:
            data = obj.data.decode("utf-8")
            pts = [tuple(p) for p in obj.polygon]
            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], True, (255, 0, 0), 2)
            process_qr(data, frame, pts)

        cv2.putText(frame, "Press 'q' to exit", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow("Live QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main_ui():
    while True:
        frame = np.zeros((300, 600, 3), dtype=np.uint8)
        cv2.rectangle(frame, (50, 100), (250, 200), (100, 200, 100), -1)
        cv2.putText(frame, "Image Scan (i)", (60, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        cv2.rectangle(frame, (350, 100), (550, 200), (100, 100, 255), -1)
        cv2.putText(frame, "Live Scan (l)", (370, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(frame, "Press 'q' to Quit", (200, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.imshow("Attendance Scanner", frame)

        key = cv2.waitKey(0)
        if key == ord('i'):
            cv2.destroyWindow("Attendance Scanner")
            image_scan_mode()
        elif key == ord('l'):
            cv2.destroyWindow("Attendance Scanner")
            live_scan_mode()
        elif key == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main_ui()
