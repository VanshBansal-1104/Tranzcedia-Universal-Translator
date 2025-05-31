import cv2
import numpy as np
from tensorflow.keras.models import load_model
import tkinter as tk

class SignLanguageTranslator:
    def __init__(self):
        self.model = load_model("sign_language_model.h5")  # Load your trained model
        self.classes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']  # Adjust as needed

    def detect_sign_language(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            roi = frame[100:300, 100:300]  # Define the region of interest
            cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 2)
            resized = cv2.resize(roi, (28, 28))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            img_array = gray.reshape(1, 28, 28, 1) / 255.0  # Normalize

            prediction = self.model.predict(img_array)
            class_index = np.argmax(prediction)
            predicted_letter = self.classes[class_index]
            cv2.putText(frame, f"Predicted: {predicted_letter}", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Sign Language Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()