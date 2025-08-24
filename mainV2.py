"""
import speech_recognition as sr
import time
import subprocess
import shlex
import pyttsx3
import google.generativeai as genai
import requests  # for API calls

# Hardcoded API key (DON'T expose this in public repos)
API_KEY = "NopeeNotGonnaGiveItToYou"

engine = pyttsx3.init()
engine.setProperty('rate', 150)
r = sr.Recognizer()
mic = sr.Microphone()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def call_gemini_flash(message):
    # Example endpoint and payload — replace with actual Gemini flash API details
    url = "https://api.gemini.example/v1/flash"  # Replace with real Gemini API URL
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "flash-1.5",
        "input": message
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        # Extract the relevant output from Gemini response, adjust as needed
        return result.get("output", "No response from Gemini")
    except Exception as e:
        print(f"API call failed: {e}")
        return "Sorry, I couldn't reach the AI."

with mic as source:
    r.adjust_for_ambient_noise(source)
    print("Listening for the buzzword 'Friday'...")

while True:
    with mic as source:
        audio = r.listen(source, phrase_time_limit=1)
    try:
        transcript = r.recognize_google(audio).lower()
        print(f"Heard: {transcript}")

        if "friday" in transcript:
            print("Buzzword detected! Recording next 5 seconds after 3 seconds...")
            subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
            time.sleep(3)  # Give a 3-second delay before recording

            with mic as source:
                audio2 = r.record(source, duration=5)
            message = r.recognize_google(audio2)
            print(f"Captured message: {message}")

            # Call Gemini flash API with the captured message
            response_text = call_gemini_flash(message)
            print(f"Gemini response: {response_text}")

            # Speak out the response
            speak(response_text)

        elif "exit now" in transcript:
            subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
            speak("Exiting now")
            exit()
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

"""


#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import time
import subprocess
import pyttsx3
import google.generativeai as genai
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found. Make sure it's in your .env file.")

genai.configure(api_key=API_KEY)

# === Text-to-Speech ===
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    print("os.system speak starting...")
    os.system(f'say -r 157 "{text}"')
    print("os.system speak done.")

# === Load Whisper ===
model = WhisperModel("small", device="cpu", compute_type="int8")  
# On M2, you could try "medium" for more accuracy, still realtime.

# === Gemini integration ===
def get_gemini_answer(prompt):
    try:
        model_g = genai.GenerativeModel(model_name="gemini-2.5-flash")
        response = model_g.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Sorry, error with friday: {e}"

def get_gemini_command(prompt):
    try:
        model_g = genai.GenerativeModel(model_name="gemini-2.5-flash")
        response = model_g.generate_content(
            "You are Friday, an AI assistant supposed to be helpfull, keep your awnswers short and consise" + prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"# Error: {e}"

# === Audio Recorder (sounddevice) ===
def record_audio(seconds=5, samplerate=16000):
    print(f"[Recording {seconds}s of audio]")
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype=np.float32)
    sd.wait()
    return audio.flatten()

def transcribe(audio, samplerate=16000):
    segments, _ = model.transcribe(audio, language="en", beam_size=5)
    text = " ".join([seg.text for seg in segments]).lower().strip()
    return text

# === Main loop ===
print("Listening for 'friday'...")

while True:
    # short listen to catch wake word
    audio = record_audio(2)
    transcript = transcribe(audio)
    if not transcript:
        continue

    print("Heard:", transcript)

    if "friday" in transcript:
        subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
        speak("Yes?")
        time.sleep(0.5)

        # longer capture for full question
        audio2 = record_audio(6)
        message = transcribe(audio2)
        print("Captured message:", message)

        if any(word in message for word in ["run", "execute", "command"]):
            response_text = get_gemini_command(message)
            print("Gemini (command):", response_text)
            try:
                os.system(response_text)
            except Exception as e:
                print(f"Command failed: {e}")
            speak(response_text)
        else:
            response_text = get_gemini_answer(message)
            print("Friday (answer):", response_text)
            speak(response_text)

    elif "exit" in transcript:
        subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
        speak("Exiting now")
        break
