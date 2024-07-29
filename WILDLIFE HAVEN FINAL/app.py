import os
from flask import Flask, render_template, request
import cv2
import numpy as np
import tensorflow as tf
from twilio.rest import Client
import requests

# Create Flask application instance
app = Flask(__name__)

# Define upload folder path
UPLOAD_FOLDER = "C:\\Users\\HP\\Downloads\\image"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function to extract frames from a video file
def extract_frames(video_path, output_folder):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    while success:
        image_file = os.path.join(output_folder, f"frame{count:04d}.jpg")
        cv2.imwrite(image_file, image)  # save frame as JPEG file
        success, image = vidcap.read()
        count += 1

# Function to detect poaching in images
def detect_poaching(folder_path):
    # Load machine learning model
    new_model1 = tf.keras.models.load_model(os.path.join('models', 'antipoaching.keras'))
    poacher_detected = False
    num_person = 0
    num_no_person = 0
    solution = 0
    
    # Change directory to image folder
    os.chdir(folder_path)
    for picture in os.listdir():
        if picture.endswith(".jpg"):
            testing_img = cv2.imread(picture)
            pic1 = tf.image.resize(testing_img, (256, 256))
            solution = new_model1.predict(np.expand_dims(pic1, 0))
            if solution > 0.5:
                print(f'Poacher detected!')
                poacher_detected = True
                num_person += 1
            else:
                print(f'No poacher detected')
                num_no_person += 1
    
    return poacher_detected, num_person, num_no_person

# Function to send SMS alert
def send_sms():
    SID = "AC5a4729aac661c213225d057ebbca104b"
    auth_token = "78b81359a663f1447467c47dc372445f"
    my_phone_number = ''
    target_phone_number = ''
    message = "ALERT, Poachers identified in frames."
    
    cl = Client(SID, auth_token)
    cl.messages.create(body=message, from_=my_phone_number, to=target_phone_number)

# Function to remove previous images from the folder
def remove_previous_images(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try:
            if os.path.isfile(file_path) and file_name.startswith("frame"):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

# Route for handling file upload and poaching detection
@app.route("/", methods=["GET", "POST"])
def upload_video():
    if request.method == "POST":
        if "video" not in request.files:
            return "No video uploaded", 400
        video_file = request.files["video"]
        if video_file.filename == "":
            return "No selected file", 400
        
        # Removing previous images before processing new video
        remove_previous_images(app.config["UPLOAD_FOLDER"])
        
        # Save uploaded video file
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], "uploaded_video.mp4")
        video_file.save(video_path)
        
        # Extract frames from the video
        extract_frames(video_path, app.config["UPLOAD_FOLDER"])
        
        # Detect poaching in frames
        poacher_detected, num_person, num_no_person = detect_poaching(app.config["UPLOAD_FOLDER"])
        
        # Send SMS alert if poacher detected
        if poacher_detected:
            send_sms()
            prediction = f"Poachers identified in {num_person} frames."
        else:
            prediction = "No poachers detected. Animals are safe."
        
        return render_template("index.html", prediction=prediction)
    
    return render_template("index.html")

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
