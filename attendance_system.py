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

# Define color scheme (modern palette)
PRIMARY_COLOR = "#4361ee"        # Vibrant blue for primary elements
SECONDARY_COLOR = "#3a0ca3"      # Deep purple for headers
ACCENT_COLOR = "#f72585"         # Bright pink for important buttons
BG_COLOR = "#f8f9fa"             # Light gray background
CARD_BG_COLOR = "#ffffff"        # White for cards
TEXT_COLOR = "#212529"           # Dark text
BUTTON_TEXT_COLOR = "white"      # White text for buttons
LIGHT_ACCENT = "#4cc9f0"         # Light blue accent
GRADIENT_TOP = "#4361ee"         # Gradient top color
GRADIENT_BOTTOM = "#3a0ca3"      # Gradient bottom color

# Set up styles for ttk widgets
def setup_styles():
    style = ttk.Style()
    
    # Configure the progress bar style
    style.configure("TProgressbar", 
                   thickness=15,
                   troughcolor="#e9ecef",
                   background=PRIMARY_COLOR,
                   borderwidth=0)
    
    # Configure the button style
    style.configure("TButton",
                   foreground=BUTTON_TEXT_COLOR,
                   background=PRIMARY_COLOR,
                   font=('Segoe UI', 10, 'bold'))
    
    # Rounded button style (only works partially in tkinter)
    style.configure("Rounded.TButton",
                  padding=6,
                  relief="flat",
                  background=PRIMARY_COLOR)

# Window is our Main frame of system
window = tk.Tk()
window.title("Face Recognition Attendance System")
window.configure(background=BG_COLOR)

# Setup ttk styles
setup_styles()

# Make the window resizable
window.resizable(True, True)

# First improve the center_window function for better automatic sizing
def center_window(window, width=None, height=None):
    # If width and height are not provided, use the window's requested dimensions
    if width is None or height is None:
        window.update_idletasks()  # Update to get actual dimensions
        if width is None:
            width = window.winfo_reqwidth()
        if height is None:
            height = window.winfo_reqheight()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set geometry
    window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Allow window to resize based on content
    window.update_idletasks()

# Custom Canvas for drawing rounded rectangles
class RoundedCanvas(tk.Canvas):
    def __init__(self, parent, width, height, radius=20, bg=CARD_BG_COLOR, **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.radius = radius

    def create_rounded_rect(self, x1, y1, x2, y2, radius=None, fill=CARD_BG_COLOR, outline=None, width=0):
        if radius is None:
            radius = self.radius
            
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        
        return self.create_polygon(points, fill=fill, outline=outline, width=width, smooth=True)

# Create a round button with icon
def create_round_button(parent, text, command, icon=None, width=15, height=2, bg_color=PRIMARY_COLOR, 
                       fg_color=BUTTON_TEXT_COLOR, font_size=12, bold=True, radius=10):
    if bold:
        font_style = ('Segoe UI', font_size, 'bold')
    else:
        font_style = ('Segoe UI', font_size)
    
    # Create frame to hold the button and provide rounded effect
    btn_frame = tk.Frame(parent, bg=BG_COLOR, bd=0, highlightthickness=0)
    
    # Create the button with rounded style
    button = tk.Button(
        btn_frame,
        text=text,
        command=command,
        font=font_style,
        bg=bg_color,
        fg=fg_color,
        relief=tk.FLAT,
        activebackground=LIGHT_ACCENT,
        activeforeground=BUTTON_TEXT_COLOR,
        cursor="hand2",
        bd=0,
        padx=20,
        pady=8,
    )
    
    # Apply rounded button effect using custom tkinter canvas hack
    def _on_enter(e):
        button['background'] = LIGHT_ACCENT
        
    def _on_leave(e):
        button['background'] = bg_color
    
    button.bind("<Enter>", _on_enter)
    button.bind("<Leave>", _on_leave)
    
    button.pack(padx=2, pady=2)
    
    return btn_frame

# Create a rounded card frame
def create_rounded_card(parent, width=300, height=300, padding_x=20, padding_y=20, bg_color=CARD_BG_COLOR, radius=15):
    # Create a frame to hold the canvas
    frame = tk.Frame(parent, bg=BG_COLOR, bd=0, highlightthickness=0)
    
    # Create the canvas with rounded corners
    canvas = RoundedCanvas(frame, width=width, height=height, radius=radius, bg=BG_COLOR)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Create the rounded rectangle on the canvas
    rect_id = canvas.create_rounded_rect(2, 2, width-2, height-2, radius=radius, fill=bg_color)
    
    # Create a frame inside the canvas to hold content
    inner_frame = tk.Frame(canvas, bg=bg_color, bd=0, highlightthickness=0)
    inner_frame.pack(fill=tk.BOTH, expand=True, padx=padding_x, pady=padding_y)
    
    # Return the frame and canvas so both can be configured if needed
    return {"frame": frame, "canvas": canvas, "inner_frame": inner_frame}

# Create custom label style
def create_label(parent, text, width=15, height=2, bg_color=CARD_BG_COLOR, 
                fg_color=TEXT_COLOR, font_size=12, bold=True):
    if bold:
        font_style = ('Segoe UI', font_size, 'bold')
    else:
        font_style = ('Segoe UI', font_size)
    
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

# Create custom rounded entry style
def create_rounded_entry(parent, width=20, font_size=14, validate_command=None):
    entry_frame = tk.Frame(parent, bg=CARD_BG_COLOR, bd=0, highlightthickness=0)
    
    entry = tk.Entry(
        entry_frame,
        width=width,
        font=('Segoe UI', font_size),
        bg="white",
        fg=TEXT_COLOR,
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground="#ced4da",
        highlightcolor=PRIMARY_COLOR,
        insertbackground=PRIMARY_COLOR,
        bd=8,  # Inner padding
    )
    
    if validate_command:
        entry['validatecommand'] = validate_command
        entry['validate'] = 'key'
    
    # Add focus event to change border color
    def on_focus_in(event):
        entry.config(highlightbackground=PRIMARY_COLOR, highlightthickness=2)
        
    def on_focus_out(event):
        entry.config(highlightbackground="#ced4da", highlightthickness=1)
        
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    
    entry.pack(fill=tk.X, expand=True)
    
    return entry_frame, entry

# Function to create gradient header with centered text
def create_gradient_header(parent, text, font_size=22, height=100):
    # Create a canvas for the gradient
    header_canvas = tk.Canvas(parent, height=height, bg=BG_COLOR, highlightthickness=0)
    header_canvas.pack(fill=tk.X)
    
    # Get the window width
    width = parent.winfo_width()
    if width <= 1:  # If the window hasn't been drawn yet
        width = parent.winfo_reqwidth()
        if width <= 1:  # If still not available, use a default
            width = 1000
    
    # Draw gradient background
    for i in range(height):
        # Calculate color based on position
        r1, g1, b1 = int(GRADIENT_TOP[1:3], 16), int(GRADIENT_TOP[3:5], 16), int(GRADIENT_TOP[5:7], 16)
        r2, g2, b2 = int(GRADIENT_BOTTOM[1:3], 16), int(GRADIENT_BOTTOM[3:5], 16), int(GRADIENT_BOTTOM[5:7], 16)
        
        ratio = i / height
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        
        color = f'#{r:02x}{g:02x}{b:02x}'
        header_canvas.create_line(0, i, width, i, fill=color)
    
    # Add text centered in the header
    header_canvas.create_text(
        width // 2, height // 2,  # Center the text horizontally and vertically
        text=text,
        fill="white",
        font=('Segoe UI', font_size, 'bold'),
        anchor="center"  # Ensure text is anchored at its center point
    )
    
    # Force the canvas to update and redraw after parent size changes
    def update_canvas(event):
        # Get the new width
        new_width = parent.winfo_width()
        
        # Clear the canvas
        header_canvas.delete("all")
        
        # Redraw gradient
        for i in range(height):
            r1, g1, b1 = int(GRADIENT_TOP[1:3], 16), int(GRADIENT_TOP[3:5], 16), int(GRADIENT_TOP[5:7], 16)
            r2, g2, b2 = int(GRADIENT_BOTTOM[1:3], 16), int(GRADIENT_BOTTOM[3:5], 16), int(GRADIENT_BOTTOM[5:7], 16)
            
            ratio = i / height
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            header_canvas.create_line(0, i, new_width, i, fill=color)
        
        # Redraw text in the center
        header_canvas.create_text(
            new_width // 2, height // 2,
            text=text,
            fill="white",
            font=('Segoe UI', font_size, 'bold'),
            anchor="center"
        )
    
    # Bind the update function to window size changes
    parent.bind("<Configure>", update_canvas)
    
    return header_canvas

# Function to register employee
def register_employee():
    register_window = tk.Toplevel(window)
    register_window.title("Register Employee")
    register_window.configure(background=BG_COLOR)
    register_window.transient(window)  # Make it float on top of the main window
    register_window.grab_set()  # Make it modal
    
    # Gradient header
    header = create_gradient_header(register_window, "Register New Employee", font_size=20, height=80)
    
    # Main content area with padding
    content_frame = tk.Frame(register_window, bg=BG_COLOR)
    content_frame.pack(fill="both", expand=True, padx=40, pady=30)
    
    # Create a rounded card for the form
    card = create_rounded_card(content_frame, width=600, height=400, padding_x=30, padding_y=30)
    card["frame"].pack(pady=10)
    
    # Form frame inside the card
    form_frame = tk.Frame(card["inner_frame"], bg=CARD_BG_COLOR)
    form_frame.pack(pady=20, fill="x")
    
    # Employee ID
    id_label = create_label(form_frame, "Employee ID:", width=15, height=1, 
                           font_size=12, bg_color=CARD_BG_COLOR)
    id_label.grid(row=0, column=0, padx=10, pady=15, sticky="w")
    
    id_frame, id_entry = create_rounded_entry(form_frame, width=25, font_size=12)
    id_frame.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
    
    # Employee Name
    name_label = create_label(form_frame, "Employee Name:", width=15, height=1, 
                             font_size=12, bg_color=CARD_BG_COLOR)
    name_label.grid(row=1, column=0, padx=10, pady=15, sticky="w")
    
    name_frame, name_entry = create_rounded_entry(form_frame, width=25, font_size=12)
    name_frame.grid(row=1, column=1, padx=10, pady=15, sticky="ew")
    
    # Status frame with style
    status_frame = tk.Frame(card["inner_frame"], bg=CARD_BG_COLOR)
    status_frame.pack(fill="x", pady=10)
    
    status_label = create_label(status_frame, "", width=50, height=1, 
                               font_size=11, bold=False, bg_color=CARD_BG_COLOR)
    status_label.pack()
    
    # Function to take images
    def start_image_capture():
        emp_id = id_entry.get().strip()
        emp_name = name_entry.get().strip()
        
        # Validation
        if not emp_id:
            messagebox.showwarning("Warning", "Please enter Employee ID")
            return
        elif not emp_id.isdigit():
            messagebox.showwarning("Warning", "Employee ID must be numeric")
            return
        elif not emp_name:
            messagebox.showwarning("Warning", "Please enter Employee Name")
            return
        
        # Confirm before starting
        if not messagebox.askyesno("Confirm", "Camera will start capturing 100 images.\n\nPlease be ready and face the camera.\n\nDo you want to continue?"):
            return
        
        try:
            # Create directory for training images if it doesn't exist
            if not os.path.exists("TrainingImage"):
                os.makedirs("TrainingImage")
                
            # Check if an employee with this ID already exists
            employee_exists = False
            if os.path.exists("EmployeeDetails.csv"):
                df = pd.read_csv("EmployeeDetails.csv")
                if int(emp_id) in df["ID"].values:
                    employee_exists = True
            
            if employee_exists:
                if not messagebox.askyesno("Warning", "Employee ID already exists. Do you want to overwrite?"):
                    return
            
            # Get the face detector
            detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            
            # Start camera
            cam = cv2.VideoCapture(0)
            
            # Sample count
            sample_num = 0
            total_samples = 100  # Reduced from 200 to 100 for efficiency
            
            # Progress tracking
            progress_frame = tk.Frame(card["inner_frame"], bg=CARD_BG_COLOR)
            progress_frame.pack(fill="x", pady=20)
            
            progress_bar = ttk.Progressbar(
                progress_frame, 
                orient="horizontal", 
                length=350, 
                mode="determinate",
                style="TProgressbar"
            )
            progress_bar.pack(pady=5)
            
            while True:
                ret, img = cam.read()
                if not ret:
                    break
                    
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    sample_num += 1
                    
                    # Save the captured face
                    img_path = f"TrainingImage/User.{emp_id}.{sample_num}.jpg"
                    cv2.imwrite(img_path, gray[y:y+h, x:x+w])
                    
                    # Update status and progress bar
                    progress = f"Capturing image {sample_num}/{total_samples}"
                    status_label.config(text=progress)
                    progress_value = int((sample_num / total_samples) * 100)
                    progress_bar["value"] = progress_value
                    register_window.update()
                
                cv2.imshow('Capture', img)
                
                # Wait for 100ms
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                elif sample_num >= total_samples:
                    break
            
            cam.release()
            cv2.destroyAllWindows()
            
            # Save employee details to CSV
            csv_path = "EmployeeDetails.csv"
            
            if not os.path.exists(csv_path):
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Name"])
                    writer.writerow([emp_id, emp_name])
            else:
                df = pd.read_csv(csv_path)
                
                # Check if employee exists and update or add
                if int(emp_id) in df["ID"].values:
                    df.loc[df["ID"] == int(emp_id), "Name"] = emp_name
                else:
                    df = df._append({"ID": int(emp_id), "Name": emp_name}, ignore_index=True)
                
                df.to_csv(csv_path, index=False)
            
            # Train the model
            status_label.config(text="Training model... Please wait.")
            progress_bar["value"] = 100
            register_window.update()
            
            # Run the training function
            train_model()
            
            messagebox.showinfo("Success", f"Employee {emp_name} registered successfully with ID {emp_id}.\n\nThe model has been trained.")
            register_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    # Button frame with modern styling
    btn_frame = tk.Frame(card["inner_frame"], bg=CARD_BG_COLOR)
    btn_frame.pack(pady=30)
    
    # Register button
    register_btn = create_round_button(btn_frame, "Register", start_image_capture, 
                          width=12, height=1, font_size=12)
    register_btn.pack(side=tk.LEFT, padx=15)
    
    # Cancel button
    cancel_btn = create_round_button(btn_frame, "Cancel", register_window.destroy, 
                              width=12, height=1, bg_color=ACCENT_COLOR, font_size=12)
    cancel_btn.pack(side=tk.LEFT, padx=15)

# Function to train the model
def train_model():
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        
        # Create directory for training labels if it doesn't exist
        if not os.path.exists("TrainingImageLabel"):
            os.makedirs("TrainingImageLabel")
        
        # Get faces and IDs
        faces, ids = get_images_and_labels("TrainingImage")
        
        # Train the model
        recognizer.train(faces, np.array(ids))
        
        # Save the model
        recognizer.save("TrainingImageLabel/trainer.yml")
        
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error training model: {str(e)}")
        return False

# Function to get images and labels for training
def get_images_and_labels(path):
    # Get all file paths
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    face_samples = []
    ids = []
    
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    for image_path in image_paths:
        try:
            # Load image and convert to grayscale
            pil_img = Image.open(image_path).convert('L')
            img_numpy = np.array(pil_img, 'uint8')
            
            # Get the ID from the image file name
            id = int(os.path.split(image_path)[-1].split(".")[1])
            
            # Detect faces
            faces = detector.detectMultiScale(img_numpy)
            
            # Store face samples and IDs
            for (x, y, w, h) in faces:
                face_samples.append(img_numpy[y:y+h, x:x+w])
                ids.append(id)
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
    
    return face_samples, ids

# Function to start automatic attendance
def start_attendance():
    attendance_window = tk.Toplevel(window)
    attendance_window.title("Automatic Attendance")
    # Make it the same size as the main window
    main_width = window.winfo_width()
    main_height = window.winfo_height()
    attendance_window.configure(background=BG_COLOR)
    attendance_window.transient(window)  # Make it float on top of the main window
    attendance_window.grab_set()  # Make it modal
    
    # Gradient header
    header = create_gradient_header(attendance_window, "Automatic Attendance", font_size=20, height=80)
    
    # Add instructions at the top
    instructions_frame = tk.Frame(attendance_window, bg=BG_COLOR)
    instructions_frame.pack(fill="x", padx=30, pady=20)
    
    instructions_label = tk.Label(
        instructions_frame,
        text="Please select one of the following attendance modes:",
        font=('Segoe UI', 12),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    instructions_label.pack(pady=5)
    
    instructions_detail = tk.Label(
        instructions_frame,
        text="• Make sure your camera is connected and working\n• You need registered employees in the system\n• Face the camera clearly for best recognition",
        font=('Segoe UI', 10),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        justify="left"
    )
    instructions_detail.pack(pady=5)
    
    # Main content area
    content_frame = tk.Frame(attendance_window, bg=BG_COLOR)
    content_frame.pack(fill="both", expand=True, pady=10)
    
    # Create card container with fixed size
    card_container = tk.Frame(content_frame, bg=BG_COLOR)
    card_container.pack(pady=10)
    
    # ------------------- Single Attendance Card -------------------
    single_card_data = create_rounded_card(card_container, width=350, height=340, padding_x=25, padding_y=25, radius=20)
    single_card = single_card_data["frame"]
    single_card.grid(row=0, column=0, padx=20, pady=20)
    
    single_inner = single_card_data["inner_frame"]
    
    # Icon
    single_icon_label = create_label(single_inner, "👤", width=5, height=2, 
                                   bg_color=CARD_BG_COLOR, font_size=42)
    single_icon_label.pack(pady=10)
    
    # Title
    single_title = create_label(single_inner, "Single Attendance", width=20, height=1, 
                              bg_color=CARD_BG_COLOR, font_size=16)
    single_title.pack(pady=10)
    
    # Description
    single_desc = create_label(single_inner, "Mark attendance for a\nsingle employee quickly", 
                             width=25, height=2, bg_color=CARD_BG_COLOR, 
                             font_size=11, bold=False)
    single_desc.pack(pady=15)
    
    # Function to show confirmation before starting
    def confirm_single_mode():
        if messagebox.askyesno("Confirm", "Ready to start Single Attendance Mode?\n\nThis will open your camera for a single attendance check."):
            # Destroy the attendance window before opening the single attendance window
            attendance_window.destroy()
            mark_single_attendance()
    
    # Button
    single_btn = create_round_button(single_inner, "Start Single Mode", confirm_single_mode, 
                                   width=15, height=1, font_size=12)
    single_btn.pack(pady=20)
    
    # ------------------- Continuous Attendance Card -------------------
    continuous_card_data = create_rounded_card(card_container, width=350, height=340, padding_x=25, padding_y=25, radius=20)
    continuous_card = continuous_card_data["frame"]
    continuous_card.grid(row=0, column=1, padx=20, pady=20)
    
    continuous_inner = continuous_card_data["inner_frame"]
    
    # Icon
    continuous_icon_label = create_label(continuous_inner, "👥", width=5, height=2, 
                                       bg_color=CARD_BG_COLOR, font_size=42)
    continuous_icon_label.pack(pady=10)
    
    # Title
    continuous_title = create_label(continuous_inner, "Continuous Mode", width=20, height=1, 
                                  bg_color=CARD_BG_COLOR, font_size=16)
    continuous_title.pack(pady=10)
    
    # Description
    continuous_desc = create_label(continuous_inner, "Mark attendance continuously\nfor multiple employees", 
                                 width=25, height=2, bg_color=CARD_BG_COLOR, 
                                 font_size=11, bold=False)
    continuous_desc.pack(pady=15)
    
    # Function to show confirmation before starting
    def confirm_continuous_mode():
        if messagebox.askyesno("Confirm", "Ready to start Continuous Attendance Mode?\n\nThis will open your camera and continuously monitor for faces."):
            # Destroy the attendance window before opening the continuous attendance window
            attendance_window.destroy()
            mark_continuous_attendance()
    
    # Button
    continuous_btn = create_round_button(continuous_inner, "Start Continuous Mode", confirm_continuous_mode, 
                                       width=15, height=1, font_size=12)
    continuous_btn.pack(pady=20)
    
    # Add a close button at the bottom
    close_btn_frame = tk.Frame(attendance_window, bg=BG_COLOR)
    close_btn_frame.pack(side=tk.BOTTOM, pady=20)
    
    close_btn = create_round_button(close_btn_frame, "Close", attendance_window.destroy, 
                                 width=10, height=1, bg_color=ACCENT_COLOR, font_size=12)
    close_btn.pack()
    
    # Update window size to match main window
    attendance_window.update_idletasks()
    attendance_window.geometry(f"{main_width}x{main_height}")
    center_window(attendance_window, main_width, main_height)

# Function to mark attendance for a single employee
def mark_single_attendance():
    try:
        # Check if the model exists
        if not os.path.exists("TrainingImageLabel/trainer.yml"):
            messagebox.showerror("Error", "Model file not found. Please train the model first.")
            print("ERROR: TrainingImageLabel/trainer.yml not found")
            return
            
        # Create a window to display the camera feed
        single_window = tk.Toplevel(window)
        single_window.title("Single Attendance")
        single_window.configure(background=BG_COLOR)
        single_window.focus_force()  # Force focus to this window
        single_window.attributes('-topmost', True)  # Keep on top temporarily
        single_window.update()
        single_window.attributes('-topmost', False)  # Allow other windows to go on top after showing
        
        # Create a gradient header
        header = create_gradient_header(single_window, "Single Attendance Mode", font_size=18, height=60)
        
        # Main content frame
        content_frame = tk.Frame(single_window, bg=BG_COLOR)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Status label
        status_frame = tk.Frame(content_frame, bg=BG_COLOR)
        status_frame.pack(fill="x", pady=10)
        
        status_label = create_label(status_frame, "Looking for face...", width=40, height=1, 
                                   font_size=12, bg_color=BG_COLOR)
        status_label.pack()
        
        # Create a fixed-size frame for the camera feed
        camera_holder = tk.Frame(content_frame, bg="black", width=640, height=480)
        camera_holder.pack_propagate(False)  # Prevent resizing
        camera_holder.pack(pady=20)
        
        camera_frame = tk.Label(camera_holder, bg="black")
        camera_frame.pack(fill="both", expand=True)
        
        # Get main window dimensions for sizing
        main_width = window.winfo_width()
        main_height = window.winfo_height()
        
        # Set window size based on content - use auto-sizing instead of fixed values
        single_window.update_idletasks()
        center_window(single_window)  # Let it determine the size automatically
        
        print("Initializing face recognizer...")
        # Initialize the face recognizer
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read("TrainingImageLabel/trainer.yml")
            print("Face recognizer loaded successfully")
        except Exception as e:
            print(f"ERROR: Could not initialize face recognizer: {str(e)}")
            messagebox.showerror("Error", f"Could not initialize face recognizer: {str(e)}")
            single_window.destroy()
            return
        
        # Load the face cascade
        try:
            face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            if face_cascade.empty():
                print("ERROR: haarcascade_frontalface_default.xml file is empty or failed to load")
                messagebox.showerror("Error", "Failed to load face detector. Check haarcascade_frontalface_default.xml file.")
                single_window.destroy()
                return
            print("Face cascade loaded successfully")
        except Exception as e:
            print(f"ERROR: Could not load face cascade: {str(e)}")
            messagebox.showerror("Error", f"Could not load face cascade: {str(e)}")
            single_window.destroy()
            return
        
        # Load the employee details
        try:
            df = pd.read_csv("EmployeeDetails.csv")
            print(f"Loaded {len(df)} employee records")
        except Exception as e:
            print(f"ERROR: Could not load EmployeeDetails.csv: {str(e)}")
            messagebox.showerror("Error", f"Could not load employee details: {str(e)}")
            single_window.destroy()
            return
        
        # Start the camera
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("ERROR: Could not open camera")
                messagebox.showerror("Error", "Could not open camera. Please check your camera connection.")
                single_window.destroy()
                return
            print("Camera started successfully")
            
            # Immediately get a frame to display
            ret, initial_frame = cap.read()
            if ret:
                # Display the initial frame right away
                cv2image = cv2.cvtColor(initial_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                img = img.resize((640, 480), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                camera_frame.imgtk = imgtk
                camera_frame.configure(image=imgtk)
                single_window.update()
            
        except Exception as e:
            print(f"ERROR: Could not start camera: {str(e)}")
            messagebox.showerror("Error", f"Could not start camera: {str(e)}")
            single_window.destroy()
            return
        
        # Set a flag to track if attendance has been marked
        attendance_marked = False
        
        # Define close_window function before it's used
        def close_window():
            try:
                cap.release()
                single_window.destroy()
                print("Camera released and window closed")
            except Exception as e:
                print(f"ERROR in close_window: {str(e)}")
        
        def update_camera():
            nonlocal attendance_marked
            
            if attendance_marked:
                return
                
            try:
                ret, frame = cap.read()
                if not ret:
                    status_label.config(text="Error accessing camera")
                    print("ERROR: Cannot read frame from camera")
                    return
                
                # Make a copy of the frame to draw on
                display_frame = frame.copy()
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 0:
                    print(f"Detected {len(faces)} faces")
                
                for (x, y, w, h) in faces:
                    # Draw rectangle around the face
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    try:
                        # Recognize the face
                        id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                        print(f"Face recognized with ID: {id}, confidence: {confidence}")
                        
                        # Lower confidence is better in LBPH (0 is a perfect match)
                        if confidence < 70:  # Adjust threshold as needed
                            # Add text with the person's name
                            try:
                                employee_name = df.loc[df['ID'] == id, 'Name'].iloc[0]
                                cv2.putText(display_frame, employee_name, (x, y-10), 
                                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                
                                # Mark attendance
                                ts = time.time()
                                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                
                                # Create attendance directory if it doesn't exist
                                if not os.path.exists("Attendance"):
                                    os.makedirs("Attendance")
                                    
                                # Create attendance file for today if it doesn't exist
                                attendance_file = f"Attendance/{date}.csv"
                                
                                if not os.path.exists(attendance_file):
                                    with open(attendance_file, 'w', newline='') as f:
                                        writer = csv.writer(f)
                                        writer.writerow(["ID", "Name", "Time"])
                                
                                # Check if attendance has already been marked for this employee today
                                attendance_marked_already = False
                                
                                if os.path.exists(attendance_file):
                                    attendance_df = pd.read_csv(attendance_file)
                                    if id in attendance_df['ID'].values:
                                        attendance_marked_already = True
                                
                                if not attendance_marked_already:
                                    with open(attendance_file, 'a', newline='') as f:
                                        writer = csv.writer(f)
                                        writer.writerow([id, employee_name, timestamp])
                                    
                                    status_label.config(text=f"Attendance marked for {employee_name} (ID: {id})")
                                    attendance_marked = True
                                    print(f"Attendance marked for {employee_name}")
                                    
                                    # Show success message
                                    success_frame = tk.Frame(content_frame, bg="#e6f7e9", padx=20, pady=20)  # Light green
                                    success_frame.pack(fill="x", pady=20, padx=50)
                                    
                                    success_msg = tk.Label(
                                        success_frame, 
                                        text=f"Attendance Successfully Marked!\n\nID: {id}\nName: {employee_name}\nTime: {timestamp}", 
                                        bg="#e6f7e9", 
                                        fg="#0d6832",  # Dark green
                                        font=('Segoe UI', 14),
                                        padx=20,
                                        pady=20
                                    )
                                    success_msg.pack()
                                    
                                    # Add close button
                                    close_btn_frame = tk.Frame(content_frame, bg=BG_COLOR)
                                    close_btn_frame.pack(pady=20)
                                    
                                    close_btn = create_round_button(close_btn_frame, "Close", close_window, 
                                                                 width=10, height=1, font_size=12)
                                    close_btn.pack()
                                    
                                    # Update window size to fit new content
                                    single_window.update_idletasks()
                                    new_height = single_window.winfo_reqheight()
                                    single_window.geometry(f"{main_width}x{new_height}")
                                    center_window(single_window, main_width, new_height)
                                    
                                    # Stop updating after 3 seconds
                                    single_window.after(3000, close_window)
                                    return
                                else:
                                    status_label.config(text=f"Attendance already marked for {employee_name}")
                                    attendance_marked = True
                                    print(f"Attendance already marked for {employee_name}")
                                    
                                    # Show already marked message
                                    already_frame = tk.Frame(content_frame, bg="#fff3e6", padx=20, pady=20)  # Light orange
                                    already_frame.pack(fill="x", pady=20, padx=50)
                                    
                                    already_msg = tk.Label(
                                        already_frame, 
                                        text=f"Attendance Already Marked!\n\nID: {id}\nName: {employee_name}", 
                                        bg="#fff3e6", 
                                        fg="#cc7000",  # Dark orange
                                        font=('Segoe UI', 14),
                                        padx=20,
                                        pady=20
                                    )
                                    already_msg.pack()
                                    
                                    # Add close button
                                    close_btn_frame = tk.Frame(content_frame, bg=BG_COLOR)
                                    close_btn_frame.pack(pady=20)
                                    
                                    close_btn = create_round_button(close_btn_frame, "Close", close_window, 
                                                                 width=10, height=1, font_size=12)
                                    close_btn.pack()
                                    
                                    # Update window size to fit new content
                                    single_window.update_idletasks()
                                    new_height = single_window.winfo_reqheight()
                                    single_window.geometry(f"{main_width}x{new_height}")
                                    center_window(single_window, main_width, new_height)
                                    
                                    # Stop updating after 3 seconds
                                    single_window.after(3000, close_window)
                                    return
                            except Exception as e:
                                print(f"ERROR: Could not process employee data: {str(e)}")
                                cv2.putText(display_frame, "Unknown", (x, y-10), 
                                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        else:
                            # Face detected but confidence too low
                            cv2.putText(display_frame, "Unknown", (x, y-10), 
                                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    except Exception as e:
                        print(f"ERROR: Face recognition failed: {str(e)}")
                        cv2.putText(display_frame, "Error", (x, y-10), 
                                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # Convert to ImageTk format to display
                cv2image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                img = img.resize((640, 480), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update the camera frame
                camera_frame.imgtk = imgtk
                camera_frame.configure(image=imgtk)
                
                # Call this function again after 5 milliseconds for smoother video
                if not attendance_marked:
                    camera_frame.after(5, update_camera)
            except Exception as e:
                print(f"ERROR in update_camera: {str(e)}")
                status_label.config(text=f"Error: {str(e)}")
                # Try to continue even after an error
                if not attendance_marked:
                    camera_frame.after(100, update_camera)  # Longer delay if there was an error
        
        # Add a close button
        button_frame = tk.Frame(single_window, bg=BG_COLOR)
        button_frame.pack(side=tk.BOTTOM, pady=20)
        
        close_button = create_round_button(button_frame, "Cancel", close_window, 
                                         bg_color=ACCENT_COLOR, font_size=12)
        close_button.pack()
        
        # Start updating the camera feed immediately
        update_camera()
        
        # Set focus to the window
        single_window.focus_set()
        
        # Protocol when window is closed
        single_window.protocol("WM_DELETE_WINDOW", close_window)
        
    except Exception as e:
        print(f"ERROR: Exception in mark_single_attendance: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to mark attendance continuously for multiple employees
def mark_continuous_attendance():
    try:
        # Check if the model exists
        if not os.path.exists("TrainingImageLabel/trainer.yml"):
            messagebox.showerror("Error", "Model file not found. Please train the model first.")
            print("ERROR: TrainingImageLabel/trainer.yml not found")
            return
            
        # Create a window to display the camera feed and attendance list
        continuous_window = tk.Toplevel(window)
        continuous_window.title("Continuous Attendance")
        continuous_window.configure(background=BG_COLOR)
        continuous_window.focus_force()  # Force focus to this window
        continuous_window.attributes('-topmost', True)  # Keep on top temporarily
        continuous_window.update()
        continuous_window.attributes('-topmost', False)  # Allow other windows to go on top after showing
        
        # Create a gradient header
        header = create_gradient_header(continuous_window, "Continuous Attendance Mode", font_size=18, height=60)
        
        # Main content frame with horizontal split
        content_frame = tk.Frame(continuous_window, bg=BG_COLOR)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left frame for camera feed with fixed size
        left_frame = tk.Frame(content_frame, bg=BG_COLOR, width=700, height=550)
        left_frame.pack_propagate(False)  # Prevent resizing
        left_frame.pack(side=tk.LEFT, fill="both", padx=10)
        
        # Status label
        status_frame = tk.Frame(left_frame, bg=BG_COLOR)
        status_frame.pack(fill="x", pady=10)
        
        status_label = create_label(status_frame, "Monitoring for faces...", width=40, height=1, 
                                   font_size=12, bg_color=BG_COLOR)
        status_label.pack()
        
        # Create a frame for the camera feed with fixed size
        camera_holder = tk.Frame(left_frame, bg="black", width=640, height=480)
        camera_holder.pack_propagate(False)  # Prevent resizing
        camera_holder.pack(pady=10)
        
        camera_frame = tk.Label(camera_holder, bg="black")
        camera_frame.pack(fill="both", expand=True)
        
        # Right frame for attendance list with fixed size
        right_frame_data = create_rounded_card(content_frame, width=400, height=550, padding_x=20, padding_y=20, radius=15)
        right_frame = right_frame_data["frame"]
        right_frame.pack(side=tk.RIGHT, fill="both", padx=10)
        
        attendance_inner = right_frame_data["inner_frame"]
        
        # Attendance list title
        attendance_title = create_label(attendance_inner, "Today's Attendance", width=25, height=1, 
                                      font_size=16, bg_color=CARD_BG_COLOR)
        attendance_title.pack(pady=10)
        
        # Date display
        today_date = datetime.datetime.now().strftime('%Y-%m-%d')
        date_label = create_label(attendance_inner, f"Date: {today_date}", width=25, height=1, 
                                 font_size=12, bg_color=CARD_BG_COLOR)
        date_label.pack(pady=5)
        
        # Counter for attendance
        count_frame = tk.Frame(attendance_inner, bg=CARD_BG_COLOR)
        count_frame.pack(fill="x", pady=5)
        
        count_label = tk.Label(
            count_frame,
            text="Total: 0",
            font=('Segoe UI', 11, 'bold'),
            bg=CARD_BG_COLOR,
            fg=PRIMARY_COLOR
        )
        count_label.pack(side=tk.RIGHT)
        
        # Create a frame for the attendance list with scrollbar
        list_frame = tk.Frame(attendance_inner, bg=CARD_BG_COLOR)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # Scrollable frame for attendance list
        canvas = tk.Canvas(list_frame, bg=CARD_BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=CARD_BG_COLOR)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Set the window size based on content
        continuous_window.update_idletasks()
        width = max(1100, continuous_window.winfo_reqwidth())  # Ensure minimum width
        height = max(650, continuous_window.winfo_reqheight())  # Ensure minimum height
        center_window(continuous_window, width, height)
        
        # Function to add attendance record to the UI
        # Defining this function BEFORE we use it
        def add_attendance_record(id, name, timestamp):
            # Create a frame for each attendance record
            record_frame = tk.Frame(scrollable_frame, bg=CARD_BG_COLOR, padx=10, pady=5)
            record_frame.pack(fill="x", pady=2)
            
            # Add a colored indicator
            indicator = tk.Frame(record_frame, bg=PRIMARY_COLOR, width=4, height=40)
            indicator.pack(side=tk.LEFT, padx=(0, 10))
            
            # Add employee details
            details_frame = tk.Frame(record_frame, bg=CARD_BG_COLOR)
            details_frame.pack(side=tk.LEFT, fill="x", expand=True)
            
            name_label = tk.Label(
                details_frame, 
                text=name, 
                font=('Segoe UI', 12, 'bold'),
                bg=CARD_BG_COLOR,
                fg=TEXT_COLOR,
                anchor='w'
            )
            name_label.pack(fill="x")
            
            id_label = tk.Label(
                details_frame, 
                text=f"ID: {id}", 
                font=('Segoe UI', 10),
                bg=CARD_BG_COLOR,
                fg=TEXT_COLOR,
                anchor='w'
            )
            id_label.pack(fill="x")
            
            # Add timestamp on the right
            time_label = tk.Label(
                record_frame, 
                text=timestamp, 
                font=('Segoe UI', 9),
                bg=CARD_BG_COLOR,
                fg="#666666"
            )
            time_label.pack(side=tk.RIGHT)
            
            # Make sure the canvas scrolls to show the new record
            canvas.update_idletasks()
            canvas.yview_moveto(1.0)  # Scroll to the bottom
            
            # Update attendance count
            count_label.config(text=f"Total: {len(scrollable_frame.winfo_children())}")
        
        print("Initializing face recognizer...")
        # Initialize the face recognizer
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read("TrainingImageLabel/trainer.yml")
            print("Face recognizer loaded successfully")
        except Exception as e:
            print(f"ERROR: Could not initialize face recognizer: {str(e)}")
            messagebox.showerror("Error", f"Could not initialize face recognizer: {str(e)}")
            continuous_window.destroy()
            return
        
        # Load the face cascade
        try:
            face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            if face_cascade.empty():
                print("ERROR: haarcascade_frontalface_default.xml file is empty or failed to load")
                messagebox.showerror("Error", "Failed to load face detector. Check haarcascade_frontalface_default.xml file.")
                continuous_window.destroy()
                return
            print("Face cascade loaded successfully")
        except Exception as e:
            print(f"ERROR: Could not load face cascade: {str(e)}")
            messagebox.showerror("Error", f"Could not load face cascade: {str(e)}")
            continuous_window.destroy()
            return
        
        # Load the employee details
        try:
            df = pd.read_csv("EmployeeDetails.csv")
            print(f"Loaded {len(df)} employee records")
        except Exception as e:
            print(f"ERROR: Could not load EmployeeDetails.csv: {str(e)}")
            messagebox.showerror("Error", f"Could not load employee details: {str(e)}")
            continuous_window.destroy()
            return
        
        # Start the camera
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("ERROR: Could not open camera")
                messagebox.showerror("Error", "Could not open camera. Please check your camera connection.")
                continuous_window.destroy()
                return
            print("Camera started successfully")
        except Exception as e:
            print(f"ERROR: Could not start camera: {str(e)}")
            messagebox.showerror("Error", f"Could not start camera: {str(e)}")
            continuous_window.destroy()
            return
        
        # Dictionary to track marked attendance to avoid duplicates
        marked_attendance = {}
        
        # Attendance file path
        attendance_file = f"Attendance/{today_date}.csv"
        
        # Create attendance file for today if it doesn't exist
        if not os.path.exists("Attendance"):
            os.makedirs("Attendance")
            
        if not os.path.exists(attendance_file):
            with open(attendance_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Time"])
        else:
            # Load existing attendance records
            if os.path.exists(attendance_file):
                attendance_df = pd.read_csv(attendance_file)
                for _, row in attendance_df.iterrows():
                    marked_attendance[row['ID']] = row['Time']
                    
                # Display existing attendance records
                for _, row in attendance_df.iterrows():
                    add_attendance_record(row['ID'], row['Name'], row['Time'])
                    
        def update_camera():
            try:
                ret, frame = cap.read()
                if not ret:
                    status_label.config(text="Error accessing camera")
                    print("ERROR: Cannot read frame from camera")
                    return
                
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 0:
                    print(f"Detected {len(faces)} faces")
                
                for (x, y, w, h) in faces:
                    # Draw rectangle around the face
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    try:
                        # Recognize the face
                        id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                        print(f"Face recognized with ID: {id}, confidence: {confidence}")
                        
                        # Lower confidence is better in LBPH (0 is a perfect match)
                        if confidence < 70:  # Adjust threshold as needed
                            # Get employee name from the ID
                            try:
                                employee_name = df.loc[df['ID'] == id, 'Name'].iloc[0]
                                print(f"Matched with employee: {employee_name}")
                                
                                # Display employee name
                                cv2.putText(frame, employee_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                
                                # Check if attendance has already been marked for this employee
                                if id not in marked_attendance:
                                    # Mark attendance
                                    ts = time.time()
                                    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                    
                                    # Add to marked_attendance
                                    marked_attendance[id] = timestamp
                                    
                                    # Save to CSV
                                    with open(attendance_file, 'a', newline='') as f:
                                        writer = csv.writer(f)
                                        writer.writerow([id, employee_name, timestamp])
                                    
                                    # Add to UI
                                    add_attendance_record(id, employee_name, timestamp)
                                    
                                    # Update status
                                    status_label.config(text=f"Attendance marked for {employee_name} (ID: {id})")
                                    print(f"Attendance marked for {employee_name}")
                                else:
                                    # Already marked, just display employee name
                                    cv2.putText(frame, "Marked", (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            except Exception as e:
                                print(f"ERROR: Could not process employee data: {str(e)}")
                                # No matching employee found
                                cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        else:
                            # Face detected but confidence too low
                            cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    except Exception as e:
                        print(f"ERROR: Face recognition failed: {str(e)}")
                        cv2.putText(frame, "Error", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # Convert to ImageTk format
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                img = img.resize((640, 480), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update the camera frame
                camera_frame.imgtk = imgtk
                camera_frame.configure(image=imgtk)
                
                # Call this function again after 10 milliseconds
                camera_frame.after(10, update_camera)
            except Exception as e:
                print(f"ERROR in update_camera: {str(e)}")
                status_label.config(text=f"Error: {str(e)}")
        
        def close_window():
            try:
                cap.release()
                continuous_window.destroy()
                print("Camera released and window closed")
            except Exception as e:
                print(f"ERROR in close_window: {str(e)}")
        
        # Add buttons at the bottom
        button_frame = tk.Frame(continuous_window, bg=BG_COLOR)
        button_frame.pack(side=tk.BOTTOM, pady=15)
        
        # Add a "Export to Excel" button
        export_btn = create_round_button(button_frame, "Export to Excel", 
                                       lambda: export_to_excel(attendance_file), 
                                       bg_color=PRIMARY_COLOR, font_size=12)
        export_btn.pack(side=tk.LEFT, padx=10)
        
        # Add a close button
        close_button = create_round_button(button_frame, "Close", close_window, 
                                         bg_color=ACCENT_COLOR, font_size=12)
        close_button.pack(side=tk.LEFT, padx=10)
        
        # Start updating the camera feed
        continuous_window.after(10, update_camera)
        
        # Set focus to the window
        continuous_window.focus_set()
        
        # Protocol when window is closed
        continuous_window.protocol("WM_DELETE_WINDOW", close_window)
        
    except Exception as e:
        print(f"ERROR: Exception in mark_continuous_attendance: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to export attendance data to Excel
def export_to_excel(attendance_file):
    try:
        # Check if the file exists
        if not os.path.exists(attendance_file):
            messagebox.showerror("Error", "Attendance file not found.")
            return
            
        # Try to read the CSV file
        df = pd.read_csv(attendance_file)
        
        # If there's no data, show an error
        if len(df) == 0:
            messagebox.showinfo("Info", "No attendance records to export.")
            return
        
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(attendance_file))[0]
        
        # Create Excel file name
        excel_file = f"Attendance/Excel/{base_name}.xlsx"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(excel_file), exist_ok=True)
        
        # Export to Excel
        df.to_excel(excel_file, index=False)
        
        # Show success message
        messagebox.showinfo("Success", f"Attendance data exported to {excel_file}")
        
        # Open the folder containing the file
        os.startfile(os.path.dirname(excel_file))
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data: {str(e)}")

# Create gradient header for main window
header = create_gradient_header(window, "Face Recognition Attendance System", font_size=22, height=100)

# Main content area
content_frame = tk.Frame(window, bg=BG_COLOR)
content_frame.pack(fill="both", expand=True, pady=50)

# Create card container with better spacing
card_container = tk.Frame(content_frame, bg=BG_COLOR)
card_container.pack()

# ------------------- Register Employee Card -------------------
register_card_data = create_rounded_card(card_container, width=340, height=380, padding_x=25, padding_y=25, radius=20)
register_card = register_card_data["frame"]
register_card.grid(row=0, column=0, padx=30, pady=20)

register_inner = register_card_data["inner_frame"]

# Icon
register_icon_label = create_label(register_inner, "👤", width=5, height=2, 
                                 bg_color=CARD_BG_COLOR, font_size=48)
register_icon_label.pack(pady=10)

# Title
register_title = create_label(register_inner, "Register Employee", width=20, height=1, 
                            bg_color=CARD_BG_COLOR, font_size=16)
register_title.pack(pady=10)

# Description
register_desc = create_label(register_inner, "Add new employees to\nthe recognition system", 
                           width=25, height=2, bg_color=CARD_BG_COLOR, 
                           font_size=11, bold=False)
register_desc.pack(pady=15)

# Register button
register_btn = create_round_button(register_inner, "Register Now", register_employee, 
                           width=15, height=1, font_size=12)
register_btn.pack(pady=20)

# ------------------- Start Attendance Card -------------------
attendance_card_data = create_rounded_card(card_container, width=340, height=380, padding_x=25, padding_y=25, radius=20)
attendance_card = attendance_card_data["frame"]
attendance_card.grid(row=0, column=1, padx=30, pady=20)

attendance_inner = attendance_card_data["inner_frame"]

# Icon
attendance_icon_label = create_label(attendance_inner, "📋", width=5, height=2, 
                                   bg_color=CARD_BG_COLOR, font_size=48)
attendance_icon_label.pack(pady=10)

# Title
attendance_title = create_label(attendance_inner, "Start Attendance", width=20, height=1, 
                              bg_color=CARD_BG_COLOR, font_size=16)
attendance_title.pack(pady=10)

# Description
attendance_desc = create_label(attendance_inner, "Begin automatic attendance\nusing face recognition", 
                             width=25, height=2, bg_color=CARD_BG_COLOR, 
                             font_size=11, bold=False)
attendance_desc.pack(pady=15)

# Start button
attendance_btn = create_round_button(attendance_inner, "Start Now", start_attendance, 
                             width=15, height=1, font_size=12)
attendance_btn.pack(pady=20)

# Footer with status information and rounded corners
footer_height = 40
footer_canvas = tk.Canvas(window, height=footer_height, bg=BG_COLOR, highlightthickness=0)
footer_canvas.pack(fill=tk.X, side=tk.BOTTOM)

# Create gradient for footer
width = window.winfo_screenwidth()
for i in range(footer_height):
    # Calculate color based on position
    r1, g1, b1 = int(GRADIENT_TOP[1:3], 16), int(GRADIENT_TOP[3:5], 16), int(GRADIENT_TOP[5:7], 16)
    r2, g2, b2 = int(GRADIENT_BOTTOM[1:3], 16), int(GRADIENT_BOTTOM[3:5], 16), int(GRADIENT_BOTTOM[5:7], 16)
    
    ratio = i / footer_height
    r = int(r1 * (1 - ratio) + r2 * ratio)
    g = int(g1 * (1 - ratio) + g2 * ratio)
    b = int(b1 * (1 - ratio) + b2 * ratio)
    
    color = f'#{r:02x}{g:02x}{b:02x}'
    footer_canvas.create_line(0, i, width, i, fill=color)

# Add status text to footer
footer_canvas.create_text(
    width - 150, footer_height // 2,
    text="Face Recognition Attendance System | v1.0",
    fill="white",
    font=('Segoe UI', 9)
)

# Add status indicator
footer_canvas.create_oval(20, footer_height // 2 - 5, 30, footer_height // 2 + 5, fill="#4cc9f0", outline="")
footer_canvas.create_text(
    80, footer_height // 2,
    text="System Ready",
    fill="white",
    font=('Segoe UI', 9)
)

# Create required directories
if not os.path.exists("TrainingImage"):
    os.makedirs("TrainingImage")
    
if not os.path.exists("TrainingImageLabel"):
    os.makedirs("TrainingImageLabel")
    
if not os.path.exists("Attendance"):
    os.makedirs("Attendance")

# Create employee details CSV if it doesn't exist
if not os.path.exists("EmployeeDetails.csv"):
    with open("EmployeeDetails.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name"])

# Start the main loop
window.mainloop() 