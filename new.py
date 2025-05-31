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
import platform
import threading
from playsound import playsound 

# Braille mappings
braille_to_english = {  
    '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e', '⠋': 'f', '⠛': 'g', '⠓': 'h',
    '⠊': 'i', '⠚': 'j', '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o', '⠏': 'p',
    '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't', '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x',
    '⠽': 'y', '⠵': 'z', '⠲': '.', '⠂': ',', '⠖': '!', '⠦': '?', ' ': ' '
}

english_to_braille = {  
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓',
    'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏',
    'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
    'y': '⠽', 'z': '⠵', '.': '⠲', ',': '⠂', '!': '⠖', '?': '⠦', ' ': ' '
}

# Color schemes
DARK_THEME = {
    "background": "#2D2D2D",
    "primary": "#4CAF50",
    "secondary": "#607D8B",
    "text": "#FFFFFF",
    "highlight": "#FFC107",
    "entry_bg": "#424242"
}

LIGHT_THEME = {
    "background": "#F5F5F5",
    "primary": "#2196F3",
    "secondary": "#607D8B",
    "text": "#212121",
    "highlight": "#FF9800",
    "entry_bg": "#FFFFFF"
}

class SplashScreen:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)
        self.splash.geometry("600x400")
        self.center_window()
        self.splash.configure(bg=DARK_THEME["background"])

        # Logo and text
        logo_image = Image.open("logo-removebg-preview.png").resize((250, 250))
        self.logo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(self.splash, image=self.logo, bg=DARK_THEME["background"])
        logo_label.pack(pady=20)
        
        tk.Label(self.splash, text="Tranzcendia", font=("Segoe UI", 28, "bold"), 
                fg=DARK_THEME["highlight"], bg=DARK_THEME["background"]).pack()
        tk.Label(self.splash, text="Universal Translation Suite", font=("Segoe UI", 14),
                fg=DARK_THEME["text"], bg=DARK_THEME["background"]).pack(pady=10)

        self.splash.after(3000, self.close_splash)

    def center_window(self):
        self.splash.update_idletasks()
        width = self.splash.winfo_width()
        height = self.splash.winfo_height()
        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)
        self.splash.geometry(f'+{x}+{y}')

    def close_splash(self):
        self.splash.destroy()
        self.callback()

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tranzcendia: A Universal Translator")
        self.root.geometry("1000x750")
        self.current_theme = LIGHT_THEME
        self.setup_styles()
        self.sign_language_translator = SignLanguageTranslator()
        self.root.configure(bg=self.current_theme["background"]) 

        # Language code mapping
        self.language_codes = {
            "English": "en", "Hindi": "hi", "Bengali": "bn", "Gujarati": "gu",
            "Kannada": "kn", "Malayalam": "ml", "Marathi": "mr", "Punjabi": "pa",
            "Tamil": "ta", "Telugu": "te", "Urdu": "ur", "Odia": "or",
            "Assamese": "as", "Nepali": "ne",
            "French": "fr", "Spanish": "es", "German": "de", "Chinese (Simplified)": "zh-CN",
            "Chinese (Traditional)": "zh-TW", "Japanese": "ja", "Korean": "ko",
            "Russian": "ru", "Italian": "it", "Portuguese": "pt", "Arabic": "ar",
            "Turkish": "tr", "Dutch": "nl", "Thai": "th", "Vietnamese": "vi"
        }

        # Main container
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        # Theme toggle
        self.theme_icon = tk.StringVar(value="🌞")
        self.theme_btn = ttk.Button(header_frame, textvariable=self.theme_icon, 
                                  command=self.toggle_theme, style="Accent.TButton")
        self.theme_btn.pack(side=tk.RIGHT, padx=5)

        # Input field with placeholder
        self.placeholder_text = "Enter text or select a file..."
        self.input_entry = ttk.Entry(
            header_frame, font=("Segoe UI", 14), foreground="gray"
        )
        self.input_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=7, padx=(5, 10))
        self.input_entry.insert(0, self.placeholder_text)
        
        # Bind focus events
        self.input_entry.bind("<FocusIn>", self.on_entry_click)
        self.input_entry.bind("<FocusOut>", self.on_focus_out)
        
        # Add placeholder state
        self.input_entry.placeholder_active = True
        
        self.mic_icon = ImageTk.PhotoImage(Image.open("7123011_google_mic_icon.png").resize((24, 24)))
        ttk.Button(header_frame, image=self.mic_icon, command=self.speech_to_text, 
                 style="Accent.TButton").pack(side=tk.LEFT, padx=5)

        # Language selection
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(lang_frame, text="Input:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.language_input = ttk.Combobox(lang_frame, values=list(self.language_codes.keys()),
                                         width=18, state="readonly")
        self.language_input.current(0)
        self.language_input.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(lang_frame, text="Output:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.language_output = ttk.Combobox(lang_frame, values=list(self.language_codes.keys()),
                                          width=18, state="readonly")
        self.language_output.current(0)
        self.language_output.pack(side=tk.LEFT, padx=10)

        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)
        
        buttons = [
            ("📄 PDF", self.select_pdf_file),
            ("🖼️ Image", self.select_image_file),
            ("🔤 Braille PDF", self.select_braille_pdf_file),
            ("🖼️ Braille Image", self.select_braille_image_file)
        ]
        for text, cmd in buttons:
            ttk.Button(btn_frame, text=text, command=cmd, style="Accent.TButton").pack(side=tk.LEFT, padx=5)

        # Translation buttons
        trans_btn_frame = ttk.Frame(main_frame)
        trans_btn_frame.pack(fill=tk.X, pady=10)
        
        trans_buttons = [
            ("🌐 Translate Text", self.translate_typed_text),
            ("⠿ English to Braille", self.english_to_braille_translate_text),
            ("🎤 Play Audio", self.play_audio_output),
            ("👐 Sign Language", self.sign_language_mode)
        ]
        for text, cmd in trans_buttons:
            ttk.Button(trans_btn_frame, text=text, command=cmd, style="Primary.TButton").pack(side=tk.LEFT, padx=5)

        # Output area
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, font=("Segoe UI", 12),
                                 bg=self.current_theme["entry_bg"], fg=self.current_theme["text"])
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Start listening for "Hey Translator"
        self.listen_for_wake_word()

    def on_entry_click(self, event):
        """Function that gets called whenever entry is clicked"""
        if self.input_entry.placeholder_active:
            self.input_entry.placeholder_active = False
            self.input_entry.delete(0, tk.END)
            self.input_entry.configure(foreground='black')

    def on_focus_out(self, event):
        """Function that gets called whenever focus is lost"""
        if self.input_entry.get() == '':
            self.input_entry.placeholder_active = True
            self.input_entry.insert(0, self.placeholder_text)
            self.input_entry.configure(foreground='gray')

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure base styles
        style.configure(".", background=self.current_theme["background"], 
                      foreground=self.current_theme["text"])
        style.configure("TEntry", fieldbackground=self.current_theme["entry_bg"],
                      foreground=self.current_theme["text"])
        style.configure("TCombobox", fieldbackground=self.current_theme["entry_bg"],
                      foreground=self.current_theme["text"])
        
        # Button styles
        style.configure("Primary.TButton", 
                      background=self.current_theme["primary"],
                      foreground=self.current_theme["text"],
                      font=("Segoe UI", 10, "bold"),
                      padding=8,
                      borderwidth=0)
        style.map("Primary.TButton",
                background=[("active", self.current_theme["primary"]), ("disabled", "#BDBDBD")])
        
        style.configure("Accent.TButton", 
                      background=self.current_theme["secondary"],
                      foreground=self.current_theme["text"],
                      font=("Segoe UI", 10),
                      padding=6,
                      borderwidth=0)
        style.map("Accent.TButton",
                background=[("active", self.current_theme["secondary"]), ("disabled", "#BDBDBD")])

    def toggle_theme(self):
        if self.current_theme == DARK_THEME:
            self.current_theme = LIGHT_THEME
            self.theme_icon.set("🌙")
        else:
            self.current_theme = DARK_THEME
            self.theme_icon.set("🌞")
        
        self.root.configure(bg=self.current_theme["background"])
        self.output_text.configure(bg=self.current_theme["entry_bg"], fg=self.current_theme["text"])
        self.setup_styles()

    def translate_typed_text(self):
        input_text = self.input_entry.get().strip()
        if input_text == self.placeholder_text or not input_text:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Please enter text to translate.")
            return

        source_lang = self.language_codes[self.language_input.get()]
        target_lang = self.language_codes[self.language_output.get()]
    
        try:
            translator = Translator()
            translated_text = translator.translate(input_text, src=source_lang, dest=target_lang).text
            self.output_text.delete(1.0, tk.END)  # Clear the previous output
            self.output_text.insert(tk.END, translated_text)  # Display the translated text
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Translation Error: {e}")

    def english_to_braille_translate_text(self):
        if self.input_entry.placeholder_active:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Please enter text to translate.")
            return
            
        text = self.input_entry.get().lower()
        braille_text = ''.join(english_to_braille.get(char, char) for char in text)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, braille_text)

    def braille_to_english(self, text):
        return ''.join(braille_to_english.get(char, char) for char in text)

    def play_audio_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if not text:
            self.show_error("No text to play")
            return

        try:
            lang_code = self.language_codes[self.language_output.get()]
            tts = gTTS(text=text, lang=lang_code)
            tts.save("output.mp3")

            # Detect OS and play audio accordingly
            if platform.system() == "Windows":
                os.system("start output.mp3")
            elif platform.system() == "Darwin":  # macOS
                os.system("afplay output.mp3")
            else:  # Linux
                os.system("mpg321 output.mp3")

        except Exception as e:
            self.show_error(f"Audio Error: {str(e)}")

    def speech_to_text(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "Processing...")
                self.root.update()
                
                recognizer.energy_threshold = 300
                recognizer.pause_threshold = 1.2
                recognizer.dynamic_energy_threshold = True

                text = recognizer.recognize_google(audio)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, text)
                
                # Clear placeholder if active
                if self.input_entry.placeholder_active:
                    self.input_entry.placeholder_active = False
                    self.input_entry.configure(foreground='black')
                
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, text)
            except sr.UnknownValueError:
                self.show_error("Could not understand audio")
            except sr.RequestError as e:
                self.show_error(f"Speech Service Error: {e}")

    def process_pdf(self, file_path, is_braille=False):
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = "".join(page.extract_text() for page in reader.pages)
            
            if is_braille:
                return self.braille_to_english(text)
            return text
        except Exception as e:
            self.show_error(f"PDF Error: {str(e)}")
        return ""

    def process_image(self, file_path, is_braille=False):
        try:
            text = pytesseract.image_to_string(Image.open(file_path))
            return self.braille_to_english(text) if is_braille else text
        except Exception as e:
            self.show_error(f"Image Error: {str(e)}")
            return ""

    def select_pdf_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            extracted_text = self.process_pdf(file_path)
            if extracted_text:
                if self.input_entry.placeholder_active:
                    self.input_entry.placeholder_active = False
                    self.input_entry.configure(foreground='black')
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, extracted_text)
                
                src_lang = self.language_codes[self.language_input.get()]
                dest_lang = self.language_codes[self.language_output.get()]
                
                try:
                    translator = Translator()
                    translated_text = translator.translate(extracted_text, src=src_lang, dest=dest_lang).text
                    self.output_text.delete(1.0, tk.END)
                    self.output_text.insert(tk.END, translated_text)
                except Exception as e:
                    self.show_error(f"Translation Error: {str(e)}")
            else:
                self.show_error("No text extracted from the PDF.")

    def select_image_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            text = self.process_image(file_path)
            if text:
                if self.input_entry.placeholder_active:
                    self.input_entry.placeholder_active = False
                    self.input_entry.configure(foreground='black')
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, text)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, text)

    def select_braille_pdf_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            text = self.process_pdf(file_path, is_braille=True)
            if text:
                if self.input_entry.placeholder_active:
                    self.input_entry.placeholder_active = False
                    self.input_entry.configure(foreground='black')
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, text)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, text)

    def select_braille_image_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            text = self.process_image(file_path, is_braille=True)
            if text:
                if self.input_entry.placeholder_active:
                    self.input_entry.placeholder_active = False
                    self.input_entry.configure(foreground='black')
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, text)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, text)

    def sign_language_mode(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Initializing sign language detection...")
        self.sign_language_translator.detect_sign_language()

    def show_error(self, message):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"⚠️ Error: {message}")

    def listen_for_wake_word(self):
        threading.Thread(target=self.wake_word_listener, daemon=True).start()

    def wake_word_listener(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.show_error("Listening for 'Hey Translator'...")
            while True:
                try:
                    audio = recognizer.listen(source)
                    text = recognizer.recognize_google(audio).lower()
                    if "hey translator" in text:
                        try:
                            playsound("how_may_I_help_you.mp3")
                        except Exception as e:
                            print(f"Error playing sound: {e}")
                        
                        self.show_error("How can I assist you?")
                        self.process_command(recognizer, source)
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    self.show_error(f"Speech Service Error: {e}")

    def process_command(self, recognizer, source):
        self.show_error("Listening for command...")
        try:
            # Adjust the recognizer sensitivity to ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)
            self.show_error("Calibrated to ambient noise. Listening for command...")

            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            self.show_error(f"Command: {command}")

            if "translate" in command:
                self.show_error("Say the text to translate.")
                audio = recognizer.listen(source)
                text_to_translate = recognizer.recognize_google(audio)
                if self.input_entry.placeholder_active:
                    self.input_entry.placeholder_active = False
                    self.input_entry.configure(foreground='black')
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, text_to_translate)
                self.translate_typed_text()

            elif "open pdf" in command:
                self.show_error("Please select the PDF file to translate.")
                self.select_pdf_file()

            elif "open image" in command:
                self.show_error("Please select the image file to translate.")
                self.select_image_file()

            elif "exit" in command or "quit" in command:
                self.show_error("Goodbye!")
                self.root.quit()

            else:
                self.show_error("Sorry, I didn't understand that command.")

        except sr.UnknownValueError:
            self.show_error("Could not understand the command.")
        except sr.RequestError as e:
            self.show_error(f"Speech Recognition Error: {e}")


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