# sign_language_mode.py

import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from gtts import gTTS
import os

# Class-to-alphabet mapping (excluding 'J' as per your dataset)
class_to_alphabet = {i: chr(65 + i) for i in range(25)}  # 65 is ASCII for 'A'
class_to_alphabet.pop(9)  # Remove 'J'

# Load the trained sign language model
model = load_model('sign_language_model.h5')
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Function to preprocess the webcam frame for prediction
def preprocess_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (28, 28)) / 255.0  # Normalize like training data
    return resized.reshape(1, 28, 28, 1)

# Function to speak the recognized word
def speak_predicted_word(word):
    tts = gTTS(text=word, lang='en')
    tts.save("predicted_word.mp3")
    os.system("mpg321 predicted_word.mp3")  # or use other audio playback methods

# Function to handle real-time sign language recognition
def real_time_sign_language_recognition():
    cap = cv2.VideoCapture(0)  # Start webcam feed
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Preprocess the frame and predict the sign language gesture
        reshaped = preprocess_frame(frame)
        prediction = model.predict(reshaped)
        predicted_class = np.argmax(prediction)
        predicted_alphabet = class_to_alphabet.get(predicted_class, "Unknown")

        # Update the Tkinter label with the predicted word
        label_predicted.config(text=f"Predicted: {predicted_alphabet}")
        
        # Speak the predicted word if the confidence is high enough
        confidence = np.max(prediction)
        if confidence > 0.8:
            speak_predicted_word(predicted_alphabet)

        # Display the webcam feed (optional)
        cv2.imshow('Sign Language Detection', frame)

        # Check for exit condition (if 'q' is pressed)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to switch to sign language mode
def enter_sign_language_mode(label_predicted, button_stop_sign_language):
    # Hide the translation widgets and show sign language widgets
    label_predicted.pack()  # Show the predicted sign language label
    button_stop_sign_language.pack()  # Show the stop button
    start_sign_language_mode()

# Function to stop sign language mode and go back to translation mode
def stop_sign_language_mode(label_main, label_predicted, button_stop_sign_language):
    label_predicted.pack_forget()  # Hide predicted sign language label
    button_stop_sign_language.pack_forget()  # Hide stop button
    label_main.pack()  # Show the main translation label again
    start_audio_translation_mode()

# Function to start the audio translation mode (this can be extended as needed)
def start_audio_translation_mode():
    label_main.config(text="Audio Translation Mode Active")

# Create the main Tkinter window
def create_sign_language_window():
    root = tk.Tk()
    root.title("Tranzcendia - Audio Translator with Sign Language Mode")
    root.geometry("500x500")

    # Main label for the app
    label_main = tk.Label(root, text="Welcome to Tranzcendia!", font=("Helvetica", 16))
    label_main.pack(pady=20)

    # Button to enter Sign Language Mode
    button_sign_language = tk.Button(root, text="Enter Sign Language Mode", font=("Helvetica", 12), 
                                     command=lambda: enter_sign_language_mode(label_predicted, button_stop_sign_language))
    button_sign_language.pack(pady=10)

    # Label to show predicted word from sign language (initially hidden)
    label_predicted = tk.Label(root, text="Predicted: ", font=("Helvetica", 16))
    label_predicted.pack_forget()  # Initially hidden

    # Button to stop Sign Language Mode and go back to translation mode
    button_stop_sign_language = tk.Button(root, text="Stop Sign Language Mode", font=("Helvetica", 12), 
                                          command=lambda: stop_sign_language_mode(label_main, label_predicted, button_stop_sign_language))
    button_stop_sign_language.pack_forget()  # Initially hidden

    # Start in audio translation mode
    start_audio_translation_mode()

    # Run the Tkinter main loop
    root.mainloop()