import tkinter as tk
from tkinter import ttk, filedialog
from googletrans import Translator
from PIL import Image, ImageTk
import pytesseract
import PyPDF2
import speech_recognition as sr
from gtts import gTTS
import os
from sign_language_translator import SignLanguageTranslator

# Braille to English dictionary
braille_to_english = {  
    '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e', '⠋': 'f', '⠛': 'g', '⠓': 'h',
    '⠊': 'i', '⠚': 'j', '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o', '⠏': 'p',
    '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't', '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x',
    '⠽': 'y', '⠵': 'z', '⠲': '.', '⠂': ',', '⠖': '!', '⠦': '?', ' ': ' '
}

# English to Braille dictionary
english_to_braille = {  
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓',
    'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏',
    'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
    'y': '⠽', 'z': '⠵', '.': '⠲', ',': '⠂', '!': '⠖', '?': '⠦', ' ': ' '
}


class SplashScreen:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)
        self.splash.geometry("600x400")
        self.center_window(self.splash, 600, 400)
        self.splash.configure(bg="#1E1E1E")

        logo_image = Image.open("logo-removebg-preview.png").resize((300, 300))
        self.logo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(self.splash, image=self.logo, bg="#1E1E1E")
        logo_label.pack(expand=True)

        tk.Label(self.splash, text="Welcome to Tranzcendia", font=("Arial", 24, "bold"), fg="#F4E04D", bg="#1E1E1E").pack(pady=10)
        self.splash.after(3000, self.close_splash)

    def center_window(self, win, width, height):
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    def close_splash(self):
        self.splash.destroy()
        self.callback()


class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tranzcendia: Universal Translator")
        self.root.geometry("800x600")
        self.root.configure(bg="#F0F0F0")

        style = ttk.Style()
        style.theme_use("default")

        # Custom styles for buttons
        style.configure("Custom.TButton", font=("Arial", 12), background="#4CAF50", foreground="white", borderwidth=1, relief="flat", padding=10)
        style.map("Custom.TButton", background=[("active", "#45a049")])

        style.configure("Custom.TCombobox", font=("Arial", 12), background="white", foreground="black", borderwidth=1, relief="flat", padding=5)

        style.configure("TLabel", font=("Arial", 12), background="#F0F0F0", foreground="black")
        style.configure("TEntry", font=("Arial", 12), background="white", foreground="black")

        self.sign_language_translator = SignLanguageTranslator()

        self.input_text = ttk.Entry(root, width=50)
        self.input_text.insert(0, "Enter text here or select a file to translate")
        self.input_text.grid(row=0, column=0, padx=20, pady=10, columnspan=2, sticky="ew")

        self.mic_icon = ImageTk.PhotoImage(Image.open("7123011_google_mic_icon.png").resize((30, 30)))
        self.mic_button = ttk.Button(root, image=self.mic_icon, command=self.speech_to_text, style="Custom.TButton")
        self.mic_button.grid(row=0, column=2, padx=10)

        ttk.Label(root, text="Input Language:").grid(row=1, column=0, sticky="w")
        self.language_input = ttk.Combobox(root, values=["English", "Spanish", "French", "German", "Italian", "Hindi","Urdu"], style="Custom.TCombobox")
        self.language_input.set("English")
        self.language_input.grid(row=1, column=1, sticky="ew")

        ttk.Label(root, text="Output Language:").grid(row=2, column=0, sticky="w")
        self.language_output = ttk.Combobox(root, values=["English", "Spanish", "French", "German", "Italian", "Hindi","Urdu"], style="Custom.TCombobox")
        self.language_output.set("English")
        self.language_output.grid(row=2, column=1, sticky="ew")

        self.select_pdf_button = ttk.Button(root, text="Select PDF", command=self.select_pdf_file, style="Custom.TButton")
        self.select_pdf_button.grid(row=3, column=0, pady=10)

        self.select_image_button = ttk.Button(root, text="Select Image", command=self.select_image_file, style="Custom.TButton")
        self.select_image_button.grid(row=3, column=1)

        self.translate_button = ttk.Button(root, text="Translate Text", command=self.translate_typed_text, style="Custom.TButton")
        self.translate_button.grid(row=4, column=0, pady=10)

        self.braille_button = ttk.Button(root, text="English to Braille", command=self.english_to_braille_translate_text, style="Custom.TButton")
        self.braille_button.grid(row=4, column=1, pady=10)

        self.braille_pdf_button = ttk.Button(root, text="Braille PDF to English", command=self.select_braille_pdf_file, style="Custom.TButton")
        self.braille_pdf_button.grid(row=5, column=0, pady=10)

        self.braille_image_button = ttk.Button(root, text="Braille Image to English", command=self.select_braille_image_file, style="Custom.TButton")
        self.braille_image_button.grid(row=5, column=1, pady=10)

        self.sign_language_button = ttk.Button(root, text="Sign Language Mode", command=self.sign_language_mode, style="Custom.TButton")
        self.sign_language_button.grid(row=9, column=1, columnspan=2, pady=10)

        self.play_audio_button = ttk.Button(root, text="Play Audio", command=lambda: self.play_audio(self.output_label.get("1.0", tk.END).strip()), style="Custom.TButton")
        self.play_audio_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.output_label = tk.Text(root, height=10, width=70, wrap=tk.WORD, bg="white", fg="black", font=("Arial", 12))
        self.output_label.grid(row=6, column=0, columnspan=3, padx=20, pady=10)
        self.output_label.insert(tk.END, "Translated text will appear here")

    def braille_translate_text(self):
        text = self.input_text.get().lower()
        braille_text = ''.join(braille_alphabet.get(char, char) for char in text)
        self.output_label.delete(1.0, tk.END)
        self.output_label.insert(tk.END, braille_text if braille_text else "Please enter text for Braille translation")

    def sign_language_mode(self):
        self.output_label.delete(1.0, tk.END)
        self.output_label.insert(tk.END, "Sign Language Mode activated!")
        self.start_sign_language_translation()

    def english_to_braille_translate_text(self):
        text = self.input_text.get().lower()
        braille_text = ''.join(english_to_braille.get(char, char) for char in text)
        self.output_label.delete(1.0, tk.END)
        self.output_label.insert(tk.END, braille_text)

    def braille_text_to_english(self):
        text = self.input_text.get().strip()
        english_text = ''.join(braille_to_english.get(char, char) for char in text)
        self.output_label.delete(1.0, tk.END)
        self.output_label.insert(tk.END, english_text)

    def translate_typed_text(self):
        text = self.input_text.get()
        input_lang = self.language_codes.get(self.language_input.get(), 'en')
        output_lang = self.language_codes.get(self.language_output.get(), 'en')
        translator = Translator()
        translated = translator.translate(text, src=input_lang, dest=output_lang)
        self.output_label.delete(1.0, tk.END)
        self.output_label.insert(tk.END, translated.text)

    language_codes = {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Hindi": "hi",
        "Urdu":"ur"
    }

    def play_audio(self, text):
        try:
            lang = self.language_codes.get(self.language_output.get(), "en")
            tts = gTTS(text=text, lang=lang)
            audio_file = "translated_audio.mp3"
            tts.save(audio_file)
            os.system(f"afplay {audio_file}")
        except Exception as e:
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, f"Error playing audio: {str(e)}")
            print(f"Error details: {str(e)}")

    def select_pdf_file(self):
        pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf_file:
            self.translate_pdf(pdf_file)

    def translate_pdf(self, pdf_file):
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = "".join(page.extract_text() for page in pdf_reader.pages)
            translated_text = self.translate_text(text, self.language_output.get())
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, translated_text)
            self.play_audio(translated_text)
        except Exception as e:
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, f"Error translating PDF: {str(e)}")

    def select_image_file(self):
        image_file = filedialog.askopenfilename(filetypes=[("Image files", "*.png"), ("Image files", "*.jpg"), ("Image files", "*.jpeg")])
        if image_file:
            self.translate_image(image_file)

    def translate_image(self, image_file):
        try:
            text = pytesseract.image_to_string(Image.open(image_file))
            translated_text = self.translate_text(text, self.language_output.get())
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, translated_text)
            self.play_audio(translated_text)
        except Exception as e:
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, f"Error translating image: {str(e)}")

    def speech_to_text(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        try:
            with mic as source:
                self.output_label.delete(1.0, tk.END)
                self.output_label.insert(tk.END, "Listening... Speak Now!")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                self.input_text.delete(0, tk.END)
                self.input_text.insert(0, text)
                self.output_label.delete(1.0, tk.END)
                self.output_label.insert(tk.END, f"Recognized Text: {text}")
        except sr.UnknownValueError:
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, "Could not understand the audio")
        except sr.RequestError:
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, "Could not request results from Google Speech Recognition")

    def translate_text(self, text, target_lang):
        translator = Translator()
        try:
            result = translator.translate(text, dest=self.language_codes.get(target_lang, "en"))
            return result.text
        except Exception as e:
            return f"Error in translation: {str(e)}"

    def text_to_braille(self):
        text = self.input_text.get().lower()
        braille_text = ''.join(self.english_to_braille.get(char, char) for char in text)
        self.output_label.delete(1.0, tk.END)
        self.output_label.insert(tk.END, braille_text)

    def braille_to_english_func(self):
        text = self.input_text.get()
        english_text = ''.join(self.braille_to_english.get(char, char) for char in text)
        self.output_label.delete(1.0, tk.END)
        self.output_label.insert(tk.END, english_text)

    def braille_pdf_to_english(self, pdf_file):
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                braille_text = "".join(page.extract_text() for page in pdf_reader.pages)
            english_text = ''.join(self.braille_to_english.get(char, char) for char in braille_text)
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, english_text)
        except Exception as e:
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, f"Error reading PDF: {str(e)}")

    def select_braille_pdf_file(self):
        pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf_file:
            self.braille_pdf_to_english(pdf_file)

    def braille_image_to_english(self, image_file):
        try:
            braille_text = pytesseract.image_to_string(Image.open(image_file))
            english_text = ''.join(self.braille_to_english.get(char, char) for char in braille_text)
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, english_text)
        except Exception as e:
            self.output_label.delete(1.0, tk.END)
            self.output_label.insert(tk.END, f"Error reading image: {str(e)}")

    def select_braille_image_file(self):
        image_file = filedialog.askopenfilename(filetypes=[("Image files", "*.png"), ("Image files", "*.jpg")])
        if image_file:
            self.braille_image_to_english(image_file)

    def start_sign_language_translation(self):
        self.sign_language_translator.detect_sign_language()


def main():
    root = tk.Tk()
    root.withdraw()

    def show_main_app():
        root.deiconify()
        TranslationApp(root)

    SplashScreen(root, show_main_app)
    root.mainloop()


if __name__ == "__main__":
    main()
    
    
    
    
# import tkinter as tk
# from tkinter import ttk, filedialog
# from googletrans import Translator
# from PIL import Image, ImageTk
# import pytesseract
# import PyPDF2
# import speech_recognition as sr
# from gtts import gTTS
# import os
# from sign_language_translator import SignLanguageTranslator

# # Braille to English dictionary
# braille_to_english = {  
#     '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e', '⠋': 'f', '⠛': 'g', '⠓': 'h',
#     '⠊': 'i', '⠚': 'j', '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o', '⠏': 'p',
#     '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't', '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x',
#     '⠽': 'y', '⠵': 'z', '⠲': '.', '⠂': ',', '⠖': '!', '⠦': '?', ' ': ' '
# }

# # English to Braille dictionary
# english_to_braille = {  
#     'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓',
#     'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏',
#     'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
#     'y': '⠽', 'z': '⠵', '.': '⠲', ',': '⠂', '!': '⠖', '?': '⠦', ' ': ' '
# }


# class SplashScreen:
#     def __init__(self, root, callback):
#         self.root = root
#         self.callback = callback
#         self.splash = tk.Toplevel(root)
#         self.splash.overrideredirect(True)
#         self.splash.geometry("600x400")
#         self.center_window(self.splash, 600, 400)
#         self.splash.configure(bg="#1E1E1E")

#         logo_image = Image.open("logo-removebg-preview.png").resize((300, 300))
#         self.logo = ImageTk.PhotoImage(logo_image)
#         logo_label = tk.Label(self.splash, image=self.logo, bg="#1E1E1E")
#         logo_label.pack(expand=True)

#         tk.Label(self.splash, text="Welcome to Tranzcendia", font=("Arial", 24, "bold"), fg="#F4E04D", bg="#1E1E1E").pack(pady=10)
#         self.splash.after(3000, self.close_splash)

#     def center_window(self, win, width, height):
#         screen_width = win.winfo_screenwidth()
#         screen_height = win.winfo_screenheight()
#         x = (screen_width - width) // 2
#         y = (screen_height - height) // 2
#         win.geometry(f"{width}x{height}+{x}+{y}")

#     def close_splash(self):
#         self.splash.destroy()
#         self.callback()


# class TranslationApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tranzcendia: Universal Translator")
#         self.root.geometry("800x600")
#         self.root.configure(bg="#F0F0F0")

#         style = ttk.Style()
#         style.theme_use("default")

#         # Custom styles for buttons
#         style.configure("Custom.TButton", font=("Arial", 12), background="#4CAF50", foreground="white", borderwidth=1, relief="flat", padding=10)
#         style.map("Custom.TButton", background=[("active", "#45a049")])

#         style.configure("Custom.TCombobox", font=("Arial", 12), background="white", foreground="black", borderwidth=1, relief="flat", padding=5)

#         style.configure("TLabel", font=("Arial", 12), background="#F0F0F0", foreground="black")
#         style.configure("TEntry", font=("Arial", 12), background="white", foreground="black")

#         self.sign_language_translator = SignLanguageTranslator()

#         self.input_text = ttk.Entry(root, width=50)
#         self.input_text.insert(0, "Enter text here or select a file to translate")
#         self.input_text.grid(row=0, column=0, padx=20, pady=10, columnspan=2, sticky="ew")

#         self.mic_icon = ImageTk.PhotoImage(Image.open("7123011_google_mic_icon.png").resize((30, 30)))
#         self.mic_button = ttk.Button(root, image=self.mic_icon, command=self.speech_to_text, style="Custom.TButton")
#         self.mic_button.grid(row=0, column=2, padx=10)

#         ttk.Label(root, text="Input Language:").grid(row=1, column=0, sticky="w")
#         self.language_input = ttk.Combobox(root, values=["English", "Spanish", "French", "German", "Italian", "Hindi","Urdu"], style="Custom.TCombobox")
#         self.language_input.set("English")
#         self.language_input.grid(row=1, column=1, sticky="ew")

#         ttk.Label(root, text="Output Language:").grid(row=2, column=0, sticky="w")
#         self.language_output = ttk.Combobox(root, values=["English", "Spanish", "French", "German", "Italian", "Hindi","Urdu"], style="Custom.TCombobox")
#         self.language_output.set("English")
#         self.language_output.grid(row=2, column=1, sticky="ew")

#         self.select_pdf_button = ttk.Button(root, text="Select PDF", command=self.select_pdf_file, style="Custom.TButton")
#         self.select_pdf_button.grid(row=3, column=0, pady=10)

#         self.select_image_button = ttk.Button(root, text="Select Image", command=self.select_image_file, style="Custom.TButton")
#         self.select_image_button.grid(row=3, column=1)

#         self.translate_button = ttk.Button(root, text="Translate Text", command=self.translate_typed_text, style="Custom.TButton")
#         self.translate_button.grid(row=4, column=0, pady=10)

#         self.braille_button = ttk.Button(root, text="English to Braille", command=self.english_to_braille_translate_text, style="Custom.TButton")
#         self.braille_button.grid(row=4, column=1, pady=10)

#         self.braille_pdf_button = ttk.Button(root, text="Braille PDF to English", command=self.select_braille_pdf_file, style="Custom.TButton")
#         self.braille_pdf_button.grid(row=5, column=0, pady=10)

#         self.braille_image_button = ttk.Button(root, text="Braille Image to English", command=self.select_braille_image_file, style="Custom.TButton")
#         self.braille_image_button.grid(row=5, column=1, pady=10)

#         self.sign_language_button = ttk.Button(root, text="Sign Language Mode", command=self.sign_language_mode, style="Custom.TButton")
#         self.sign_language_button.grid(row=9, column=1, columnspan=2, pady=10)

#         self.play_audio_button = ttk.Button(root, text="Play Audio", command=lambda: self.play_audio(self.output_label.get("1.0", tk.END).strip()), style="Custom.TButton")
#         self.play_audio_button.grid(row=7, column=0, columnspan=2, pady=10)

#         self.output_label = tk.Text(root, height=10, width=70, wrap=tk.WORD, bg="white", fg="black", font=("Arial", 12))
#         self.output_label.grid(row=6, column=0, columnspan=3, padx=20, pady=10)
#         self.output_label.insert(tk.END, "Translated text will appear here")

#     def braille_translate_text(self):
#         text = self.input_text.get().lower()
#         braille_text = ''.join(braille_alphabet.get(char, char) for char in text)
#         self.output_label.delete(1.0, tk.END)
#         self.output_label.insert(tk.END, braille_text if braille_text else "Please enter text for Braille translation")

#     def sign_language_mode(self):
#         self.output_label.delete(1.0, tk.END)
#         self.output_label.insert(tk.END, "Sign Language Mode activated!")
#         self.start_sign_language_translation()

#     def english_to_braille_translate_text(self):
#         text = self.input_text.get().lower()
#         braille_text = ''.join(english_to_braille.get(char, char) for char in text)
#         self.output_label.delete(1.0, tk.END)
#         self.output_label.insert(tk.END, braille_text)

#     def braille_text_to_english(self):
#         text = self.input_text.get().strip()
#         english_text = ''.join(braille_to_english.get(char, char) for char in text)
#         self.output_label.delete(1.0, tk.END)
#         self.output_label.insert(tk.END, english_text)

#     def translate_typed_text(self):
#         text = self.input_text.get()
#         input_lang = self.language_codes.get(self.language_input.get(), 'en')
#         output_lang = self.language_codes.get(self.language_output.get(), 'en')
#         translator = Translator()
#         translated = translator.translate(text, src=input_lang, dest=output_lang)
#         self.output_label.delete(1.0, tk.END)
#         self.output_label.insert(tk.END, translated.text)

#     language_codes = {
#         "English": "en",
#         "Spanish": "es",
#         "French": "fr",
#         "German": "de",
#         "Italian": "it",
#         "Hindi": "hi",
#         "Urdu":"ur"
#     }

#     def play_audio(self, text):
#         try:
#             lang = self.language_codes.get(self.language_output.get(), "en")
#             tts = gTTS(text=text, lang=lang)
#             audio_file = "translated_audio.mp3"
#             tts.save(audio_file)
#             os.system(f"afplay {audio_file}")
#         except Exception as e:
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, f"Error playing audio: {str(e)}")
#             print(f"Error details: {str(e)}")

#     def select_pdf_file(self):
#         pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
#         if pdf_file:
#             self.translate_pdf(pdf_file)

#     def translate_pdf(self, pdf_file):
#         try:
#             with open(pdf_file, 'rb') as file:
#                 pdf_reader = PyPDF2.PdfReader(file)
#                 text = "".join(page.extract_text() for page in pdf_reader.pages)
#             translated_text = self.translate_text(text, self.language_output.get())
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, translated_text)
#             self.play_audio(translated_text)
#         except Exception as e:
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, f"Error translating PDF: {str(e)}")

#     def select_image_file(self):
#         image_file = filedialog.askopenfilename(filetypes=[("Image files", "*.png"), ("Image files", "*.jpg"), ("Image files", "*.jpeg")])
#         if image_file:
#             self.translate_image(image_file)

#     def translate_image(self, image_file):
#         try:
#             text = pytesseract.image_to_string(Image.open(image_file))
#             translated_text = self.translate_text(text, self.language_output.get())
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, translated_text)
#             self.play_audio(translated_text)
#         except Exception as e:
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, f"Error translating image: {str(e)}")

#     def speech_to_text(self):
#         recognizer = sr.Recognizer()
#         mic = sr.Microphone()
#         try:
#             with mic as source:
#                 self.output_label.delete(1.0, tk.END)
#                 self.output_label.insert(tk.END, "Listening... Speak Now!")
#                 recognizer.adjust_for_ambient_noise(source)
#                 audio = recognizer.listen(source)
#                 text = recognizer.recognize_google(audio)
#                 self.input_text.delete(0, tk.END)
#                 self.input_text.insert(0, text)
#                 self.output_label.delete(1.0, tk.END)
#                 self.output_label.insert(tk.END, f"Recognized Text: {text}")
#         except sr.UnknownValueError:
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, "Could not understand the audio")
#         except sr.RequestError:
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, "Could not request results from Google Speech Recognition")

#     def translate_text(self, text, target_lang):
#         translator = Translator()
#         try:
#             result = translator.translate(text, dest=self.language_codes.get(target_lang, "en"))
#             return result.text
#         except Exception as e:
#             return f"Error in translation: {str(e)}"

#     def text_to_braille(self):
#         text = self.input_text.get().lower()
#         braille_text = ''.join(self.english_to_braille.get(char, char) for char in text)
#         self.output_label.delete(1.0, tk.END)
#         self.output_label.insert(tk.END, braille_text)

#     def braille_to_english_func(self):
#         text = self.input_text.get()
#         english_text = ''.join(self.braille_to_english.get(char, char) for char in text)
#         self.output_label.delete(1.0, tk.END)
#         self.output_label.insert(tk.END, english_text)

#     def braille_pdf_to_english(self, pdf_file):
#         try:
#             with open(pdf_file, 'rb') as file:
#                 pdf_reader = PyPDF2.PdfReader(file)
#                 braille_text = "".join(page.extract_text() for page in pdf_reader.pages)
#             english_text = ''.join(self.braille_to_english.get(char, char) for char in braille_text)
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, english_text)
#         except Exception as e:
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, f"Error reading PDF: {str(e)}")

#     def select_braille_pdf_file(self):
#         pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
#         if pdf_file:
#             self.braille_pdf_to_english(pdf_file)

#     def braille_image_to_english(self, image_file):
#         try:
#             braille_text = pytesseract.image_to_string(Image.open(image_file))
#             english_text = ''.join(self.braille_to_english.get(char, char) for char in braille_text)
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, english_text)
#         except Exception as e:
#             self.output_label.delete(1.0, tk.END)
#             self.output_label.insert(tk.END, f"Error reading image: {str(e)}")

#     def select_braille_image_file(self):
#         image_file = filedialog.askopenfilename(filetypes=[("Image files", "*.png"), ("Image files", "*.jpg")])
#         if image_file:
#             self.braille_image_to_english(image_file)

#     def start_sign_language_translation(self):
#         self.sign_language_translator.detect_sign_language()


# def main():
#     root = tk.Tk()
#     root.withdraw()

#     def show_main_app():
#         root.deiconify()
#         TranslationApp(root)

#     SplashScreen(root, show_main_app)
#     root.mainloop()


# if __name__ == "__main__":
#     main()