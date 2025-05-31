from sign_language_translator import SignLanguageTranslator

# Inside TranslationApp class
def sign_language_mode(self):
    cap = cv2.VideoCapture(0)
    sl_translator = SignLanguageTranslator("sign_language_model.h5")  # Update with your model path
    
    self.output_label.delete(1.0, tk.END)
    self.output_label.insert(tk.END, "Press 'q' to quit Sign Language Mode\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        sign_prediction = sl_translator.predict_sign(frame)
        cv2.putText(frame, f"Predicted Sign: {sign_prediction}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        cv2.imshow('Sign Language Detection', frame)

        # Display the detected sign in the output label
        self.output_label.insert(tk.END, sign_prediction + " ")
        self.root.update_idletasks()  # Update the GUI

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()