# Face Recognition Attendance System

A modern attendance management system that uses facial recognition technology to automatically mark attendance. Built with Python, OpenCV, and Tkinter.

## Features

- **Employee Registration**: Register new employees with face capture
- **Face Recognition**: Automatically recognize registered employees
- **Multiple Attendance Modes**:
  - Single Mode: Quick attendance for one person
  - Continuous Mode: Ongoing attendance tracking for multiple people
- **Modern UI**: Clean, responsive interface with gradient styling
- **Attendance Reports**: CSV-based attendance records for easy export

## Requirements

- Python 3.6+
- OpenCV (`pip install opencv-python`)
- OpenCV contrib modules (`pip install opencv-contrib-python`)
- Tkinter (included in Python)
- PIL/Pillow (`pip install Pillow`)
- Pandas (`pip install pandas`)
- NumPy (`pip install numpy`)

## Project Structure

- **attendance_system.py**: Main application file
- **EmployeeDetails.csv**: Database of employee information
- **Attendance/**: Folder containing attendance records (CSV files)
- **TrainingImage/**: Folder for storing employee face images
- **TrainingImageLabel/**: Folder containing trained face recognition models
- **haarcascade_frontalface_default.xml** and **haarcascade_frontalface_alt.xml**: Face detection models
- **testing.py** and **training.py**: Helper files for testing and training

## Getting Started

1. Clone the repository
2. Install the required packages:
   ```
   pip install opencv-python opencv-contrib-python Pillow pandas numpy
   ```
3. Run the application:
   ```
   python attendance_system.py
   ```

## How to Use

### Employee Registration
1. Click on "Register Employee"
2. Enter the employee ID and name
3. The system will capture 100 face images for training
4. The model will be automatically trained after capture

### Taking Attendance
1. Click on "Start Attendance"
2. Choose either "Single Mode" or "Continuous Mode"
3. The system will automatically recognize faces and mark attendance
4. Attendance records are saved in the Attendance folder with date as the filename

### Viewing Attendance
- Attendance records are stored as CSV files in the Attendance folder
- CSV format: ID, Name, Time
- You can export the records from the continuous attendance mode

## Customization

The system includes various customization options:
- Modern color scheme with gradient headers
- Rounded buttons and card elements
- Progress indicators for face capture and registration
- Adaptive window sizing for different screen resolutions

## Troubleshooting

- Ensure your camera is properly connected and working
- Good lighting improves face detection accuracy
- Maintain a consistent position during registration for best results
- If face detection fails, try using the alternative haarcascade file 