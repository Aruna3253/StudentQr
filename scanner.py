# scanner.py
import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
import csv
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import textwrap
import pandas as pd

# Check if user already marked attendance today
def already_marked_today(user_id):
    if not os.path.exists("attendance.csv"):
        return False
    df = pd.read_csv("attendance.csv", dtype=str)
    today = datetime.now().strftime("%Y-%m-%d")
    filtered = df[(df["ID"] == str(user_id)) & (df["Date"] == today)]
    return not filtered.empty


# Add new entry to CSV
def log_attendance(name, user_id):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    # Create file if not exists
    if not os.path.exists("attendance.csv"):
        with open("attendance.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "ID", "Date", "Time", "Status"])

    # Write new row
    with open("attendance.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name, user_id, date, time, "IN"])
    print(f"[LOGGED] {name} at {time}")

def draw_wrapped_text(img, text, origin, max_width=35, font=cv2.FONT_HERSHEY_SIMPLEX,
                      font_scale=0.7, color=(0, 0, 255), thickness=2, line_height=25):
    wrapped = textwrap.wrap(text, width=max_width)
    x, y = origin
    for i, line in enumerate(wrapped):
        y_offset = y + i * line_height
        cv2.putText(img, line, (x, y_offset), font, font_scale, color, thickness)

def scan_qr_from_image(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    for obj in decoded_objects:
        data = obj.data.decode("utf-8")
        pts = [tuple(point) for point in obj.polygon]
        cv2.polylines(image, [np.array(pts, dtype=np.int32)], True, (0, 255, 0), 2)

        try:
            name, user_id = data.split(',')
            label = f"Name: {name}\nID: {user_id}"
            draw_wrapped_text(image, label, (pts[0][0], pts[0][1] - 50))

            if already_marked_today(user_id):
                messagebox.showinfo("Duplicate Entry", f"Your attendance is already taken for today.")
                draw_wrapped_text(image, "Already marked today", (pts[0][0], pts[0][1] + 30), color=(0, 0, 255))
            else:
                log_attendance(name, user_id)
                date = datetime.now().strftime("%Y-%m-%d")
                messagebox.showinfo("Success", f"Your attendance is successful for today - {date}")
                draw_wrapped_text(image, "Attendance marked successfully", (pts[0][0], pts[0][1] + 30), color=(0, 255, 0))
        except:
            draw_wrapped_text(image, "Invalid QR Format", (pts[0][0], pts[0][1] - 20))
    return image

def image_scan_mode():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    if file_path:
        scanned_img = scan_qr_from_image(file_path)
        cv2.imshow("Image QR Scanner", scanned_img)
        cv2.waitKey(0)
        cv2.destroyWindow("Image QR Scanner")

def live_scan_mode():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot access camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            data = obj.data.decode("utf-8")
            pts = [tuple(point) for point in obj.polygon]
            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], True, (255, 0, 0), 2)

            try:
                name, user_id = data.split(',')
                label = f"Name: {name}\nID: {user_id}"
                draw_wrapped_text(frame, label, (pts[0][0], pts[0][1] - 50))

                if already_marked_today(user_id):
                    messagebox.showinfo("Duplicate Entry", f"Your attendance is already taken for today.")
                    draw_wrapped_text(frame, "Already marked today", (pts[0][0], pts[0][1] + 30), color=(0, 0, 255))
                else:
                    log_attendance(name, user_id)
                    date = datetime.now().strftime("%Y-%m-%d")
                    messagebox.showinfo("Success", f"Your attendance is successful for today - {date}")
                    draw_wrapped_text(frame, "Attendance marked successfully", (pts[0][0], pts[0][1] + 30), color=(0, 255, 0))
            except:
                draw_wrapped_text(frame, "Invalid QR Format", (pts[0][0], pts[0][1] - 20))

        cv2.putText(frame, "Press 'q' to exit", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow("Live QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow("Live QR Scanner")

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
