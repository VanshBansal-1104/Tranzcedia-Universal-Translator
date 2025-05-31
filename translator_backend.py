import os
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract

# Braille mappings for basic English letters and numbers
braille_mappings = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
    '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑',
    '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊', '0': '⠚',
    ' ': ' '
}

def text_to_braille(text):
    return ''.join(braille_mappings.get(char, '?') for char in text.lower())

def speech_to_text(language="en-US"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please speak now...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio, language=language)
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None

def detect_and_translate(text, target_lang):
    translator = Translator()
    try:
        detected_lang = translator.detect(text).lang
        return translator.translate(text, src=detected_lang, dest=target_lang).text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save("translated_speech.mp3")
        os.system("afplay translated_speech.mp3" if os.name == 'posix' else "start translated_speech.mp3")
    except Exception as e:
        print(f"Audio playback error: {e}")

def translate_pdf(file_path, target_lang, tts_enabled):
    try:
        reader = PdfReader(file_path)
        pdf_text = "".join(page.extract_text() for page in reader.pages)
        translated_text = text_to_braille(pdf_text) if target_lang == 'br' else detect_and_translate(pdf_text, target_lang)
        if tts_enabled:
            speak_text(translated_text, target_lang)
        print(f"Translated PDF Text: {translated_text}")
    except Exception as e:
        print(f"PDF processing error: {e}")

def image_to_text(file_path, target_lang, tts_enabled):
    try:
        img = Image.open(file_path)
        extracted_text = pytesseract.image_to_string(img)
        translated_text = text_to_braille(extracted_text) if target_lang == 'br' else detect_and_translate(extracted_text, target_lang)
        if tts_enabled:
            speak_text(translated_text, target_lang)
        print(f"Translated Image Text: {translated_text}")
    except Exception as e:
        print(f"Image processing error: {e}")