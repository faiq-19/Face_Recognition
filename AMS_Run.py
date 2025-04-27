import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import csv
import os
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time

# Define color scheme
PRIMARY_COLOR = "#3498db"       # Blue for primary elements
SECONDARY_COLOR = "#2c3e50"     # Dark blue/gray for headers
ACCENT_COLOR = "#e74c3c"        # Red for important buttons/highlights
BG_COLOR = "#ecf0f1"            # Light gray for background
TEXT_COLOR = "#2c3e50"          # Dark text color
BUTTON_TEXT_COLOR = "white"     # White text for buttons

# Window is our Main frame of system
window = tk.Tk()
window.title("Catalyst1122 - Face Recognition Attendance System")
window.geometry('1280x720')
window.configure(background=BG_COLOR)

# Function to center windows on screen
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

center_window(window, 1280, 720)

# Create custom button style
def create_button(parent, text, command, width=15, height=2, bg_color=PRIMARY_COLOR, 
                 fg_color=BUTTON_TEXT_COLOR, font_size=12, bold=True):
    if bold:
        font_style = ('Helvetica', font_size, 'bold')
    else:
        font_style = ('Helvetica', font_size)
    
    button = tk.Button(
        parent, 
        text=text,
        command=command,
        width=width,
        height=height,
        bg=bg_color,
        fg=fg_color,
        font=font_style,
        relief=tk.RAISED,
        borderwidth=2,
        activebackground="#2980b9",  # Darker blue when active
        cursor="hand2"  # Hand cursor on hover
    )
    return button

# Create custom label style
def create_label(parent, text, width=15, height=2, bg_color=BG_COLOR, 
                fg_color=TEXT_COLOR, font_size=12, bold=True):
    if bold:
        font_style = ('Helvetica', font_size, 'bold')
    else:
        font_style = ('Helvetica', font_size)
    
    label = tk.Label(
        parent,
        text=text,
        width=width,
        height=height,
        bg=bg_color,
        fg=fg_color,
        font=font_style
    )
    return label

# Create custom entry style
def create_entry(parent, width=20, font_size=14, validate_command=None):
    entry = tk.Entry(
        parent,
        width=width,
        font=('Helvetica', font_size),
        bg="white",
        fg=TEXT_COLOR,
        relief=tk.SUNKEN,
        borderwidth=2
    )
    
    if validate_command:
        entry['validatecommand'] = validate_command
        entry['validate'] = 'key'
        
    return entry

# Function to load and resize images
def load_image(path, width, height):
    try:
        img = Image.open(path)
        img = img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None

# Department management
departments = ["HR", "IT", "Finance", "Marketing", "Operations", "Sales"]

def manage_departments():
    dept_window = tk.Toplevel(window)
    dept_window.title("Department Management")
    dept_window.configure(background=BG_COLOR)
    center_window(dept_window, 600, 500)
    
    # Title
    title_label = create_label(dept_window, "Department Management", width=30, 
                              bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
    title_label.pack(pady=20)
    
    # Frame for departments list
    list_frame = tk.Frame(dept_window, bg=BG_COLOR)
    list_frame.pack(pady=10, fill="both", expand=True)
    
    # Departments listbox
    dept_listbox = tk.Listbox(list_frame, width=40, height=15, font=('Helvetica', 12))
    dept_listbox.pack(side=tk.LEFT, padx=20, pady=10)
    
    # Scrollbar
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20))
    
    # Configure scrollbar
    dept_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=dept_listbox.yview)
    
    # Populate listbox with departments
    for dept in departments:
        dept_listbox.insert(tk.END, dept)
    
    # Frame for add department
    add_frame = tk.Frame(dept_window, bg=BG_COLOR)
    add_frame.pack(pady=10)
    
    # Entry for new department
    dept_label = create_label(add_frame, "New Department:", width=15, height=1, font_size=12)
    dept_label.pack(side=tk.LEFT, padx=5)
    
    new_dept_entry = create_entry(add_frame, width=20, font_size=12)
    new_dept_entry.pack(side=tk.LEFT, padx=5)
    
    # Function to add department
    def add_department():
        new_dept = new_dept_entry.get().strip()
        if new_dept:
            if new_dept not in departments:
                departments.append(new_dept)
                dept_listbox.insert(tk.END, new_dept)
                new_dept_entry.delete(0, tk.END)
                messagebox.showinfo("Success", f"Department '{new_dept}' added successfully!")
            else:
                messagebox.showwarning("Warning", "Department already exists!")
        else:
            messagebox.showwarning("Warning", "Please enter a department name!")
    
    # Function to remove department
    def remove_department():
        try:
            selected_idx = dept_listbox.curselection()[0]
            selected_dept = dept_listbox.get(selected_idx)
            
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{selected_dept}'?"):
                departments.remove(selected_dept)
                dept_listbox.delete(selected_idx)
                messagebox.showinfo("Success", f"Department '{selected_dept}' removed!")
        except IndexError:
            messagebox.showwarning("Warning", "Please select a department to remove!")
    
    # Add department button
    add_btn = create_button(add_frame, "Add Department", add_department, width=15, height=1, font_size=12)
    add_btn.pack(side=tk.LEFT, padx=5)
    
    # Button frame
    btn_frame = tk.Frame(dept_window, bg=BG_COLOR)
    btn_frame.pack(pady=10)
    
    # Remove department button
    remove_btn = create_button(btn_frame, "Remove Department", remove_department, width=15, height=1, 
                              bg_color=ACCENT_COLOR, font_size=12)
    remove_btn.pack(side=tk.LEFT, padx=10)
    
    # Close button
    close_btn = create_button(btn_frame, "Close", dept_window.destroy, width=15, height=1, font_size=12)
    close_btn.pack(side=tk.LEFT, padx=10)

# GUI for manually fill attendance
def manually_fill():
    sb = tk.Toplevel(window)
    sb.title("Manual Attendance - Catalyst1122")
    sb.geometry('600x400')
    sb.configure(background=BG_COLOR)
    center_window(sb, 600, 400)

    def fill_attendance():
        department = department_var.get()
        
        if not department:
            messagebox.showwarning("Warning", "Please select a department!")
            return
            
        ts = time.time()
        Date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")
        
        # Creating csv of attendance
        DB_table_name = str(department + "_" + Date + "_Time_" +
                        Hour + "_" + Minute + "_" + Second)

        try:
            connection = pymysql.connect(
                host='localhost', user='root', password='', db='manually_fill_attendance')
            cursor = connection.cursor()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {str(e)}")
            return

        sql = f"""CREATE TABLE IF NOT EXISTS `{DB_table_name}` (
                ID INT NOT NULL AUTO_INCREMENT,
                EMPLOYEE_ID varchar(100) NOT NULL,
                NAME VARCHAR(50) NOT NULL,
                DATE VARCHAR(20) NOT NULL,
                TIME VARCHAR(20) NOT NULL,
                PRIMARY KEY (ID)
                );"""

        try:
            cursor.execute(sql)
        except Exception as ex:
            messagebox.showerror("Database Error", f"Error creating table: {str(ex)}")
            return

        sb.destroy()
        
        # Create manual fill window
        MFW = tk.Toplevel(window)
        MFW.title(f"Manual Attendance for {department} - Catalyst1122")
        MFW.geometry('880x500')
        MFW.configure(background=BG_COLOR)
        center_window(MFW, 880, 500)
        
        # Title
        title_label = create_label(MFW, f"Manual Attendance Entry - {department}", width=40, 
                                  bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
        title_label.pack(pady=20)

        # Entry frame
        entry_frame = tk.Frame(MFW, bg=BG_COLOR)
        entry_frame.pack(pady=20)
        
        # Employee ID
        emp_id_label = create_label(entry_frame, "Employee ID:", width=15, height=1, bg_color=BG_COLOR)
        emp_id_label.grid(row=0, column=0, padx=10, pady=20)
        
        def validate_id(P, d):
            if d == '1':  # insert
                if not P.isdigit():
                    return False
            return True
        
        emp_id_entry = create_entry(entry_frame, width=20, font_size=14)
        emp_id_entry['validatecommand'] = (emp_id_entry.register(validate_id), '%P', '%d')
        emp_id_entry['validate'] = 'key'
        emp_id_entry.grid(row=0, column=1, padx=10, pady=20)
        
        # Clear employee ID
        def clear_emp_id():
            emp_id_entry.delete(0, tk.END)
        
        clear_emp_btn = create_button(entry_frame, "Clear", clear_emp_id, width=8, height=1, font_size=12)
        clear_emp_btn.grid(row=0, column=2, padx=10, pady=20)
        
        # Employee Name
        emp_name_label = create_label(entry_frame, "Employee Name:", width=15, height=1, bg_color=BG_COLOR)
        emp_name_label.grid(row=1, column=0, padx=10, pady=20)
        
        emp_name_entry = create_entry(entry_frame, width=20, font_size=14)
        emp_name_entry.grid(row=1, column=1, padx=10, pady=20)
        
        # Clear employee name
        def clear_emp_name():
            emp_name_entry.delete(0, tk.END)
        
        clear_name_btn = create_button(entry_frame, "Clear", clear_emp_name, width=8, height=1, font_size=12)
        clear_name_btn.grid(row=1, column=2, padx=10, pady=20)
        
        # Notification label
        notification_label = create_label(MFW, "", width=40, height=1, bg_color=BG_COLOR)
        notification_label.pack(pady=10)

        # Enter data in database
        def enter_data():
            employee_id = emp_id_entry.get().strip()
            employee_name = emp_name_entry.get().strip()
            
            if not employee_id or not employee_name:
                notification_label.config(text="Employee ID and Name required!", 
                                         fg="red", bg=BG_COLOR)
                return
                
            current_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            
            # Insert data
            insert_data = f"INSERT INTO `{DB_table_name}` (ID, EMPLOYEE_ID, NAME, DATE, TIME) VALUES (0, %s, %s, %s, %s)"
            values = (employee_id, employee_name, Date, current_time)
            
            try:
                cursor.execute(insert_data, values)
                connection.commit()
                notification_label.config(text=f"Added: {employee_name} (ID: {employee_id})", 
                                         fg="green", bg=BG_COLOR)
                emp_id_entry.delete(0, tk.END)
                emp_name_entry.delete(0, tk.END)
                emp_id_entry.focus()
            except Exception as e:
                notification_label.config(text=f"Error: {str(e)}", fg="red", bg=BG_COLOR)

        # Create CSV function
        def create_csv():
            try:
                cursor.execute(f"SELECT * FROM `{DB_table_name}`;")
                csv_path = f'Attendance/Manual/{DB_table_name}.csv'
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(csv_path), exist_ok=True)
                
                with open(csv_path, "w", newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([i[0] for i in cursor.description])  # Write headers
                    csv_writer.writerows(cursor)
                
                notification_label.config(text=f"CSV created: {csv_path}", fg="green", bg=BG_COLOR)
                
                # Show the CSV in new window
                view_csv(csv_path, department)
                
            except Exception as e:
                notification_label.config(text=f"Error creating CSV: {str(e)}", fg="red", bg=BG_COLOR)

        # View CSV function
        def view_csv(csv_path, dept_name):
            try:
                csv_window = tk.Toplevel(MFW)
                csv_window.title(f"Attendance for {dept_name} - Catalyst1122")
                csv_window.configure(background=BG_COLOR)
                
                # Title
                title = create_label(csv_window, f"Attendance for {dept_name}", width=30, 
                                   bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
                title.pack(pady=20)
                
                # Create frame for table
                table_frame = tk.Frame(csv_window, bg=BG_COLOR)
                table_frame.pack(padx=20, pady=20)
                
                with open(csv_path, newline="") as file:
                    reader = csv.reader(file)
                    r = 0
                    
                    for col in reader:
                        c = 0
                        for row in col:
                            cell = tk.Label(table_frame, width=15, height=1, 
                                          font=('Helvetica', 12),
                                          bg="white", fg=TEXT_COLOR, 
                                          text=row, relief=tk.RIDGE,
                                          borderwidth=1)
                            cell.grid(row=r, column=c, padx=1, pady=1)
                            c += 1
                        r += 1
                
                # Adjust window size based on data
                csv_window.update()
                w = table_frame.winfo_width() + 60
                h = table_frame.winfo_height() + 100
                center_window(csv_window, w, h)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open CSV file: {str(e)}")

        # Buttons frame
        button_frame = tk.Frame(MFW, bg=BG_COLOR)
        button_frame.pack(pady=20)
        
        # Submit button
        submit_btn = create_button(button_frame, "Submit Entry", enter_data, width=15, height=2, font_size=14)
        submit_btn.grid(row=0, column=0, padx=20)
        
        # Create CSV button
        csv_btn = create_button(button_frame, "Export to CSV", create_csv, width=15, height=2, font_size=14)
        csv_btn.grid(row=0, column=1, padx=20)
        
        # Close button
        close_btn = create_button(button_frame, "Close", MFW.destroy, width=15, height=2, 
                                 bg_color=ACCENT_COLOR, font_size=14)
        close_btn.grid(row=0, column=2, padx=20)
        
        # Set focus to employee ID
        emp_id_entry.focus()

    # Title
    title_label = create_label(sb, "Select Department", width=20, 
                              bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
    title_label.pack(pady=20)
    
    # Department selection frame
    dept_frame = tk.Frame(sb, bg=BG_COLOR)
    dept_frame.pack(pady=20)
    
    dept_label = create_label(dept_frame, "Department:", width=15, height=1, bg_color=BG_COLOR)
    dept_label.pack(side=tk.LEFT, padx=10)
    
    department_var = tk.StringVar()
    department_dropdown = ttk.Combobox(dept_frame, textvariable=department_var, 
                                      values=departments, width=25, font=('Helvetica', 12))
    department_dropdown.pack(side=tk.LEFT, padx=10)
    
    # Button frame
    button_frame = tk.Frame(sb, bg=BG_COLOR)
    button_frame.pack(pady=30)
    
    # Fill attendance button
    fill_btn = create_button(button_frame, "Fill Attendance", fill_attendance, width=15, height=2, font_size=14)
    fill_btn.pack(side=tk.LEFT, padx=10)
    
    # Manage departments button
    dept_btn = create_button(button_frame, "Manage Departments", manage_departments, width=15, height=2, font_size=14)
    dept_btn.pack(side=tk.LEFT, padx=10)
    
    # Cancel button
    cancel_btn = create_button(button_frame, "Cancel", sb.destroy, width=15, height=2, 
                              bg_color=ACCENT_COLOR, font_size=14)
    cancel_btn.pack(side=tk.LEFT, padx=10)

# Clear textboxes
def clear():
    txt.delete(0, tk.END)

def clear1():
    txt2.delete(0, tk.END)

# Error screens
def show_error(message):
    error_window = tk.Toplevel(window)
    error_window.title("Warning")
    error_window.configure(background=BG_COLOR)
    center_window(error_window, 400, 150)
    
    # Error icon (you can use an actual image here)
    #error_icon = load_image("error_icon.png", 40, 40)
    #if error_icon:
    #    icon_label = tk.Label(error_window, image=error_icon, bg=BG_COLOR)
    #    icon_label.image = error_icon
    #    icon_label.pack(pady=(10, 0))
    
    # Error message
    error_label = create_label(error_window, message, width=30, height=2, 
                              fg_color="red", font_size=14)
    error_label.pack(pady=20)
    
    # OK button
    ok_btn = create_button(error_window, "OK", error_window.destroy, width=10, height=1, font_size=12)
    ok_btn.pack(pady=10)

# For take images for datasets
def take_img():
    employee_id = txt.get().strip()
    employee_name = txt2.get().strip()
    
    if not employee_id:
        show_error("Employee ID is required!")
        return
    elif not employee_name:
        show_error("Employee Name is required!")
        return
    
    try:
        cam = cv2.VideoCapture(0)
        detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        sampleNum = 0
        
        # Notification window for instructions
        info_window = tk.Toplevel(window)
        info_window.title("Capturing Images")
        info_window.configure(background=BG_COLOR)
        center_window(info_window, 400, 200)
        
        info_label = create_label(info_window, "Capturing face images...\nPlease look at the camera.\nPress 'q' to stop.", 
                                width=30, height=3, font_size=14)
        info_label.pack(pady=20)
        
        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(info_window, variable=progress_var, maximum=70)
        progress_bar.pack(pady=20, padx=40, fill=tk.X)
        
        while True:
            ret, img = cam.read()
            if not ret:
                show_error("Cannot access camera!")
                cam.release()
                info_window.destroy()
                return
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sampleNum = sampleNum + 1
                
                # Save the captured face
                os.makedirs("TrainingImage", exist_ok=True)
                cv2.imwrite(f"TrainingImage/{employee_name}.{employee_id}.{sampleNum}.jpg",
                          gray[y:y+h, x:x+w])
                
                # Update progress
                progress_var.set(sampleNum)
                info_window.update()
            
            cv2.imshow('Face Capturing', img)
            
            # Wait for 100 milliseconds
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            
            # Break if the sample number is more than 70
            elif sampleNum >= 70:
                break

        cam.release()
        cv2.destroyAllWindows()
        info_window.destroy()
        
        # Save details to CSV
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        
        # Ensure directory exists
        os.makedirs("EmployeeDetails", exist_ok=True)
        
        csv_path = 'EmployeeDetails/EmployeeDetails.csv'
        
        # Create file if it doesn't exist
        if not os.path.isfile(csv_path):
            with open(csv_path, 'w', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(["EmployeeID", "Name", "RegisterDate", "RegisterTime"])
        
        # Add employee details
        row = [employee_id, employee_name, date, time_stamp]
        with open(csv_path, 'a+', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        
        # Show success message
        msg = f"Images Saved for Employee ID: {employee_id}, Name: {employee_name}"
        Notification.config(text=msg, bg="green", fg="white")
        Notification.place(x=250, y=400)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        Notification.config(text=error_msg, bg="red", fg="white")
        Notification.place(x=250, y=400)

# For choosing department and filling attendance
def subjectchoose():
    department_window = tk.Toplevel(window)
    department_window.title("Select Department - Catalyst1122")
    department_window.geometry('600x400')
    department_window.configure(background=BG_COLOR)
    center_window(department_window, 600, 400)
    
    # Title
    title_label = create_label(department_window, "Automatic Attendance", width=20, 
                              bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
    title_label.pack(pady=20)
    
    # Notification
    notification = create_label(department_window, "", width=40, height=1, bg_color=BG_COLOR)
    notification.pack(pady=10)
    
    # Department selection frame
    dept_frame = tk.Frame(department_window, bg=BG_COLOR)
    dept_frame.pack(pady=20)
    
    dept_label = create_label(dept_frame, "Department:", width=15, height=1, bg_color=BG_COLOR)
    dept_label.pack(side=tk.LEFT, padx=10)
    
    department_var = tk.StringVar()
    department_dropdown = ttk.Combobox(dept_frame, textvariable=department_var, 
                                     values=departments, width=25, font=('Helvetica', 12))
    department_dropdown.pack(side=tk.LEFT, padx=10)
    
    def fill_attendance():
        department = department_var.get()
        
        if not department:
            notification.config(text="Please select a department!", fg="red")
            return
            
        # Process for automatic attendance using face recognition
        try:
            # Initialize face recognizer
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            
            try:
                recognizer.read("TrainingImageLabel/Trainner.yml")
            except:
                notification.config(text="Model not found, please train the model first!", 
                                  fg="red", bg=BG_COLOR)
                return
            
            # Start face detection process
            harcascadePath = "haarcascade_frontalface_default.xml"
            faceCascade = cv2.CascadeClassifier(harcascadePath)
            
            # Read employee details
            try:
                df = pd.read_csv("EmployeeDetails/EmployeeDetails.csv")
            except:
                notification.config(text="Employee details file not found!", 
                                  fg="red", bg=BG_COLOR)
                return
            
            # Start camera
            cam = cv2.VideoCapture(0)
            
            # Info window for attendance process
            info_window = tk.Toplevel(department_window)
            info_window.title("Processing Attendance")
            info_window.configure(background=BG_COLOR)
            center_window(info_window, 400, 200)
            
            info_label = create_label(info_window, "Processing attendance...\nPlease look at the camera.", 
                                    width=30, height=2, font_size=14)
            info_label.pack(pady=20)
            
            # Create attendance dataframe
            col_names = ['EmployeeID', 'Name', 'Date', 'Time']
            attendance = pd.DataFrame(columns=col_names)
            
            # Set time limit for attendance
            now = time.time()
            end_time = now + 20  # 20 seconds limit
            
            # Status label
            status_var = tk.StringVar()
            status_var.set("Waiting for faces...")
            status_label = create_label(info_window, "", width=30, height=1, 
                                      bg_color=BG_COLOR, font_size=12)
            status_label.pack(pady=10)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            # For live updating
            def update_status():
                status_label.config(text=status_var.get())
                info_window.after(100, update_status)
            
            update_status()
            
            while time.time() < end_time:
                ret, im = cam.read()
                if not ret:
                    status_var.set("Cannot access camera!")
                    continue
                    
                gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray, 1.2, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Recognize face
                    Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                    
                    if conf < 70:  # If confidence is low enough to be a match
                        ts = time.time()
                        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                        
                        # Get name from dataframe
                        try:
                            aa = df.loc[df['EmployeeID'] == Id]['Name'].values[0]
                            status_var.set(f"Recognized: {aa} (ID: {Id})")
                            
                            # Add to attendance
                            attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]
                            
                            # Draw rectangle and name
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(im, f"{aa} ({Id})", (x, y - 10), font, 0.75, (0, 255, 0), 2)
                        except:
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            cv2.putText(im, "Unknown", (x, y - 10), font, 0.75, (0, 0, 255), 2)
                    else:
                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(im, "Unknown", (x, y - 10), font, 0.75, (0, 0, 255), 2)
                        
                cv2.imshow('Attendance', im)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Close the camera
            cam.release()
            cv2.destroyAllWindows()
            info_window.destroy()
            
            # Create directory structure if not exists
            os.makedirs("Attendance/Auto", exist_ok=True)
            
            # Save attendance to CSV
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            Hour, Minute, Second = timeStamp.split(":")
            
            # File name with department
            fileName = f"Attendance/Auto/{department}_{date}_{Hour}_{Minute}_{Second}.csv"
            
            # Remove duplicates and save
            attendance = attendance.drop_duplicates(subset=['EmployeeID'], keep='first')
            attendance.to_csv(fileName, index=False)
            
            # Update notification
            notification.config(text=f"Attendance Completed! File saved: {fileName}", 
                              fg="green", bg=BG_COLOR)
            
            # Display attendance
            show_attendance(fileName, department)
            
        except Exception as e:
            notification.config(text=f"Error: {str(e)}", fg="red", bg=BG_COLOR)
    
    # Function to display attendance
    def show_attendance(csv_path, dept_name):
        try:
            attendance_window = tk.Toplevel(department_window)
            attendance_window.title(f"Attendance for {dept_name} - Catalyst1122")
            attendance_window.configure(background=BG_COLOR)
            
            # Title
            title = create_label(attendance_window, f"Attendance for {dept_name}", width=30, 
                               bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
            title.pack(pady=20)
            
            # Create table frame
            table_frame = tk.Frame(attendance_window, bg=BG_COLOR)
            table_frame.pack(padx=20, pady=20)
            
            # Read CSV
            data = pd.read_csv(csv_path)
            
            # Create table headers
            headers = list(data.columns)
            for i, header in enumerate(headers):
                header_label = tk.Label(table_frame, width=15, height=2, 
                                      font=('Helvetica', 12, 'bold'),
                                      bg=SECONDARY_COLOR, fg="white", 
                                      text=header, relief=tk.RIDGE)
                header_label.grid(row=0, column=i, sticky="nsew")
            
            # Fill table with data
            for i, row in data.iterrows():
                for j, value in enumerate(row):
                    cell = tk.Label(table_frame, width=15, height=1, 
                                  font=('Helvetica', 12),
                                  bg="white", fg=TEXT_COLOR, 
                                  text=str(value), relief=tk.RIDGE)
                    cell.grid(row=i+1, column=j, sticky="nsew")
            
            # Close button
            btn_frame = tk.Frame(attendance_window, bg=BG_COLOR)
            btn_frame.pack(pady=20)
            
            close_btn = create_button(btn_frame, "Close", attendance_window.destroy, 
                                    width=10, height=1, font_size=12)
            close_btn.pack()
            
            # Adjust window size
            attendance_window.update()
            w = table_frame.winfo_width() + 60
            h = table_frame.winfo_height() + 140
            center_window(attendance_window, w, h)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not display attendance: {str(e)}")
    
    # Button frame
    button_frame = tk.Frame(department_window, bg=BG_COLOR)
    button_frame.pack(pady=30)
    
    # Start attendance button
    start_btn = create_button(button_frame, "Start Attendance", fill_attendance, 
                            width=15, height=2, font_size=14)
    start_btn.pack(side=tk.LEFT, padx=10)
    
    # Manage departments button
    dept_btn = create_button(button_frame, "Manage Departments", manage_departments, 
                           width=15, height=2, font_size=14)
    dept_btn.pack(side=tk.LEFT, padx=10)
    
    # Cancel button
    cancel_btn = create_button(button_frame, "Cancel", department_window.destroy, 
                             width=15, height=2, bg_color=ACCENT_COLOR, font_size=14)
    cancel_btn.pack(side=tk.LEFT, padx=10)

# Train the model
def trainimg():
    try:
        # Check if TrainingImage folder exists
        if not os.path.isdir("TrainingImage"):
            show_error("Training folder not found! Please capture images first.")
            return
            
        # Get the training images
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        
        # Show progress window
        progress_window = tk.Toplevel(window)
        progress_window.title("Training Model")
        progress_window.configure(background=BG_COLOR)
        center_window(progress_window, 400, 200)
        
        info_label = create_label(progress_window, "Training face recognition model...\nPlease wait.", 
                                width=30, height=2, font_size=14)
        info_label.pack(pady=20)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(pady=20, padx=40, fill=tk.X)
        
        status_label = create_label(progress_window, "Starting...", width=30, height=1, 
                                  bg_color=BG_COLOR, font_size=12)
        status_label.pack(pady=10)
        
        # Function to update progress status
        def update_progress(progress, status_text):
            progress_var.set(progress)
            status_label.config(text=status_text)
            progress_window.update()
        
        # Now training
        update_progress(10, "Getting faces...")
        
        # Get faces and IDs
        faces, ids = get_images_and_labels("TrainingImage")
        
        update_progress(50, "Training model...")
        
        # Train the model
        recognizer.train(faces, np.array(ids))
        
        # Save the model
        os.makedirs("TrainingImageLabel", exist_ok=True)
        recognizer.write("TrainingImageLabel/Trainner.yml")
        
        update_progress(100, "Training completed!")
        
        # Wait a moment before closing
        progress_window.after(2000, progress_window.destroy)
        
        Notification.config(text="Model trained successfully!", bg="green", fg="white")
        Notification.place(x=250, y=400)
        
    except Exception as e:
        if 'progress_window' in locals():
            progress_window.destroy()
        Notification.config(text=f"Error training model: {str(e)}", bg="red", fg="white")
        Notification.place(x=250, y=400)

# Function to get images and labels for training
def get_images_and_labels(path):
    # Get all file paths
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    face_samples = []
    ids = []
    
    # Create face detector
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    # For each image
    for image_path in image_paths:
        # Read image and convert to grayscale
        PIL_img = Image.open(image_path).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')
        
        # Get the label (ID)
        id = int(os.path.split(image_path)[-1].split('.')[1])
        
        # Detect faces
        faces = detector.detectMultiScale(img_numpy)
        
        # Add each face to samples
        for (x, y, w, h) in faces:
            face_samples.append(img_numpy[y:y+h, x:x+w])
            ids.append(id)
            
    return face_samples, ids

# View attendance records
def view_attendance():
    attendance_window = tk.Toplevel(window)
    attendance_window.title("View Attendance Records - Catalyst1122")
    attendance_window.configure(background=BG_COLOR)
    center_window(attendance_window, 600, 400)
    
    # Title
    title_label = create_label(attendance_window, "Attendance Records", width=20, 
                            bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
    title_label.pack(pady=20)
    
    # Frame for selection
    selection_frame = tk.Frame(attendance_window, bg=BG_COLOR)
    selection_frame.pack(pady=20)
    
    # Radiobuttons for type
    type_var = tk.StringVar(value="Auto")
    auto_radio = tk.Radiobutton(selection_frame, text="Automatic Attendance", variable=type_var, 
                              value="Auto", bg=BG_COLOR, font=('Helvetica', 12))
    auto_radio.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    
    manual_radio = tk.Radiobutton(selection_frame, text="Manual Attendance", variable=type_var, 
                                value="Manual", bg=BG_COLOR, font=('Helvetica', 12))
    manual_radio.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    
    # Button to view files
    def show_files():
        attendance_type = type_var.get()
        path = f"Attendance/{attendance_type}"
        
        if not os.path.exists(path):
            messagebox.showwarning("Warning", f"No {attendance_type} attendance records found!")
            return
            
        files = os.listdir(path)
        
        if not files:
            messagebox.showwarning("Warning", f"No {attendance_type} attendance records found!")
            return
            
        # Show file selection window
        file_window = tk.Toplevel(attendance_window)
        file_window.title(f"{attendance_type} Attendance Records - Catalyst1122")
        file_window.configure(background=BG_COLOR)
        center_window(file_window, 600, 400)
        
        # Title
        title = create_label(file_window, f"{attendance_type} Attendance Records", width=30, 
                          bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
        title.pack(pady=20)
        
        # Listbox frame
        list_frame = tk.Frame(file_window, bg=BG_COLOR)
        list_frame.pack(pady=10, fill="both", expand=True)
        
        # Files listbox
        file_listbox = tk.Listbox(list_frame, width=50, height=15, font=('Helvetica', 12))
        file_listbox.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20))
        
        # Configure scrollbar
        file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=file_listbox.yview)
        
        # Populate listbox with files
        for file in files:
            if file.endswith('.csv'):
                file_listbox.insert(tk.END, file)
        
        # Function to open selected file
        def open_file():
            try:
                selected_idx = file_listbox.curselection()[0]
                selected_file = file_listbox.get(selected_idx)
                
                file_path = os.path.join(path, selected_file)
                
                # Extract department name from filename
                parts = selected_file.split('_')
                department = parts[0]
                
                # View the attendance
                view_attendance_file(file_path, department)
                
            except IndexError:
                messagebox.showwarning("Warning", "Please select a file to open!")
        
        # Button frame
        btn_frame = tk.Frame(file_window, bg=BG_COLOR)
        btn_frame.pack(pady=10)
        
        # Open file button
        open_btn = create_button(btn_frame, "Open File", open_file, width=15, height=1, font_size=12)
        open_btn.pack(side=tk.LEFT, padx=10)
        
        # Close button
        close_btn = create_button(btn_frame, "Close", file_window.destroy, width=15, height=1, font_size=12)
        close_btn.pack(side=tk.LEFT, padx=10)
    
    # Function to view attendance file
    def view_attendance_file(file_path, department):
        try:
            view_window = tk.Toplevel(window)
            view_window.title(f"Attendance for {department} - Catalyst1122")
            view_window.configure(background=BG_COLOR)
            
            # Title
            title = create_label(view_window, f"Attendance for {department}", width=30, 
                              bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
            title.pack(pady=20)
            
            # Create table frame
            table_frame = tk.Frame(view_window, bg=BG_COLOR)
            table_frame.pack(padx=20, pady=20)
            
            # Read CSV
            data = pd.read_csv(file_path)
            
            # Create table headers
            headers = list(data.columns)
            for i, header in enumerate(headers):
                header_label = tk.Label(table_frame, width=15, height=2, 
                                      font=('Helvetica', 12, 'bold'),
                                      bg=SECONDARY_COLOR, fg="white", 
                                      text=header, relief=tk.RIDGE)
                header_label.grid(row=0, column=i, sticky="nsew")
            
            # Fill table with data
            for i, row in data.iterrows():
                for j, value in enumerate(row):
                    cell = tk.Label(table_frame, width=15, height=1, 
                                  font=('Helvetica', 12),
                                  bg="white", fg=TEXT_COLOR, 
                                  text=str(value), relief=tk.RIDGE)
                    cell.grid(row=i+1, column=j, sticky="nsew")
            
            # Close button
            btn_frame = tk.Frame(view_window, bg=BG_COLOR)
            btn_frame.pack(pady=20)
            
            close_btn = create_button(btn_frame, "Close", view_window.destroy, 
                                    width=10, height=1, font_size=12)
            close_btn.pack()
            
            # Adjust window size
            view_window.update()
            w = table_frame.winfo_width() + 60
            h = table_frame.winfo_height() + 140
            center_window(view_window, w, h)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    # Button frame
    button_frame = tk.Frame(attendance_window, bg=BG_COLOR)
    button_frame.pack(pady=30)
    
    # View files button
    view_btn = create_button(button_frame, "View Records", show_files, width=15, height=2, font_size=14)
    view_btn.pack(side=tk.LEFT, padx=10)
    
    # Close button
    close_btn = create_button(button_frame, "Close", attendance_window.destroy, width=15, height=2, 
                            bg_color=ACCENT_COLOR, font_size=14)
    close_btn.pack(side=tk.LEFT, padx=10)

# Show about information
def about():
    about_window = tk.Toplevel(window)
    about_window.title("About - Catalyst1122")
    about_window.configure(background=BG_COLOR)
    center_window(about_window, 600, 400)
    
    # Title
    title_label = create_label(about_window, "About the System", width=20, 
                             bg_color=SECONDARY_COLOR, fg_color="white", font_size=16)
    title_label.pack(pady=20)
    
    # Logo image (placeholder)
    #logo_img = load_image("logo.png", 150, 150)
    #if logo_img:
    #    logo_label = tk.Label(about_window, image=logo_img, bg=BG_COLOR)
    #    logo_label.image = logo_img
    #    logo_label.pack(pady=10)
    
    # About text
    about_text = """Face Recognition Attendance System
    
Version 1.0
    
This system uses facial recognition technology to automate the
attendance marking process. It can also handle manual attendance
entry when needed.
    
Features:
• Automatic face detection and recognition
• Manual attendance entry
• Department management
• Attendance records viewing
    
Created by Catalyst1122"""
    
    text_label = tk.Label(about_window, text=about_text, bg=BG_COLOR, fg=TEXT_COLOR,
                        font=('Helvetica', 12), justify=tk.LEFT)
    text_label.pack(pady=20)
    
    # Close button
    close_btn = create_button(about_window, "Close", about_window.destroy, width=15, height=1, font_size=12)
    close_btn.pack(pady=10)

# Create main UI components
title = create_label(window, "Face Recognition Attendance System", width=40, 
                   bg_color=SECONDARY_COLOR, fg_color="white", font_size=22)
title.place(x=400, y=20)

# Employee ID
employee_id_label = create_label(window, "Employee ID:", width=10, height=1, 
                               bg_color=BG_COLOR, font_size=14)
employee_id_label.place(x=400, y=100)

txt = create_entry(window, width=20, font_size=14)
txt.place(x=550, y=100)

# Employee Name
employee_name_label = create_label(window, "Employee Name:", width=13, height=1, 
                                 bg_color=BG_COLOR, font_size=14)
employee_name_label.place(x=400, y=150)

txt2 = create_entry(window, width=20, font_size=14)
txt2.place(x=550, y=150)

# Notification label
Notification = create_label(window, "", width=50, height=1, bg_color=BG_COLOR, font_size=14)
Notification.place(x=250, y=400)

# Buttons

# Take Images button
takeImg = create_button(window, "Take Images", take_img, width=15, height=2, font_size=14)
takeImg.place(x=200, y=300)

# Train Images button
trainImg = create_button(window, "Train Model", trainimg, width=15, height=2, font_size=14)
trainImg.place(x=450, y=300)

# Automatic Attendance button
trackImg = create_button(window, "Auto Attendance", subjectchoose, width=15, height=2, font_size=14)
trackImg.place(x=700, y=300)

# Manual Attendance button
manual_attendance = create_button(window, "Manual Attendance", manually_fill, width=15, height=2, font_size=14)
manual_attendance.place(x=200, y=500)

# View Attendance button
view_records = create_button(window, "View Records", view_attendance, width=15, height=2, font_size=14)
view_records.place(x=450, y=500)

# About button
about_btn = create_button(window, "About", about, width=15, height=2, font_size=14)
about_btn.place(x=700, y=500)

# Exit button
quit_btn = create_button(window, "Exit", window.destroy, width=15, height=2, 
                       bg_color=ACCENT_COLOR, font_size=14)
quit_btn.place(x=950, y=500)

# Clear ID button
clearButton = create_button(window, "Clear", clear, width=8, height=1, font_size=12)
clearButton.place(x=800, y=100)

# Clear Name button
clearButton2 = create_button(window, "Clear", clear1, width=8, height=1, font_size=12)
clearButton2.place(x=800, y=150)

# Start the application
window.mainloop()