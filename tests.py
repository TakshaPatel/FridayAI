"import os
import subprocess
import shlex
import time

def os_system_speak(text):
    print("os.system speak starting...")
    os.system(f'say -r 157 "{text}"')
    print("os.system speak done.")

def subprocess_run_speak(text):
    print("subprocess.run speak starting...")
    subprocess.run(["say", "-r", "157", text])
    print("subprocess.run speak done.")

def subprocess_run_quoted_speak(text):
    print("subprocess.run quoted speak starting...")
    safe_text = shlex.quote(text)
    subprocess.run(f"say -r 157 {safe_text}", shell=True, check=True)
    print("subprocess.run quoted speak done.")

test_text = 'Hello! Testing "quotes", punctuation, and a slow speech rate. a'

print("\nRunning os_system_speak...")
os_system_speak(test_text)
time.sleep(2)

print("\nRunning subprocess_run_speak...")
subprocess_run_speak(test_text)
time.sleep(2)

print("\nRunning subprocess_run_quoted_speak...")
subprocess_run_quoted_speak(test_text)


def beep():
    subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])

# When buzzword detected:
beep()
print("Buzzword detected! Recording next 7 seconds...")



import pyttsx3
engine = pyttsx3.init()
engine.say("Hello world, can you hear me?")
engine.runAndWait()
