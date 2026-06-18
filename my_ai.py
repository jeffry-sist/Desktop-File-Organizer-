import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import sys
import os
import webbrowser
import cv2 
import google.generativeai as genai
import PIL.Image
import time
import pyautogui 
import psutil 
import shutil 

# --- WINDOWS SOUND FIX ---
try:
    import winsound
except ImportError:
    winsound = None

# --- CONFIGURATION ---
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) 

# --- SAFE PATHS ---
user_profile = os.path.expanduser("~")
MEMORY_FILE = os.path.join(user_profile, "Desktop", "memory.txt")
DESKTOP_PATH = os.path.join(user_profile, "Desktop")

# --- API KEY (PASTE YOUR NEW KEY BELOW) ---
genai.configure(api_key="keen-enigma-458016-k66")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- VARIABLES ---
SECRET_NAME = 'system' 
IS_AWAKE = False 

def talk(text):
    print("AI: " + str(text))
    engine.say(text)
    engine.runAndWait()

# --- INTERFACE ---
def print_interface():
    os.system('cls' if os.name == 'nt' else 'clear') 
    print("--------------------------------------------------")
    if IS_AWAKE:
        print("  STATE: [ AWAKE ] - Listening...")
        print("      ( O )      ( O )    ")
        print("           < ^ >          ")
        print("        \\_______/         ") 
    else:
        print(f"  STATE: [ SLEEP ] - Say '{SECRET_NAME}'")
        print("      ( - )      ( - )    ")
        print("           < ^ >          ")
        print("         _______          ")
    print("--------------------------------------------------")

# --- MEMORY FUNCTIONS ---
def load_memory():
    if not os.path.exists(MEMORY_FILE): return ""
    try:
        with open(MEMORY_FILE, 'r') as f: return f.read()
    except: return ""

def save_to_memory(text):
    try:
        with open(MEMORY_FILE, 'a') as f: f.write(text + "\n")
    except: talk("Memory error.")

# --- LISTENER ---
def take_command():
    global IS_AWAKE
    try:
        with sr.Microphone() as source:
            print_interface()
            listener.adjust_for_ambient_noise(source, duration=0.5)
            # timeout=None prevents the "blinking" loop from going too fast
            voice = listener.listen(source, timeout=None, phrase_time_limit=5)
            command = listener.recognize_google(voice)
            command = command.lower()
            print(f"--> HEARD: {command}")
            
            if IS_AWAKE:
                return command
            else:
                if SECRET_NAME in command:
                    return command # Return the command to trigger "wake up"
                return ""
    except Exception as e:
        return ""

# --- VISION FEATURE ---
def analyze_vision():
    talk("Capturing...")
    cam = cv2.VideoCapture(0)
    time.sleep(1.5) # Time for camera to focus
    ret, frame = cam.read()
    cam.release()
    cv2.destroyAllWindows()
    
    if ret and frame is not None:
        cv2.imwrite('vision_capture.jpg', frame)
        try:
            img = PIL.Image.open('vision_capture.jpg')
            # Better prompt for faster response
            response = model.generate_content(["I am holding this. What is it? Describe it in one short sentence.", img])
            print(f"DEBUG VISION: {response.text}")
            talk(response.text)
        except Exception as e:
            print(f"Vision Error: {e}")
            talk("I saw it, but my brain had an error.")
    else:
        talk("I couldn't trigger the camera.")

# --- SENTRY FEATURE ---
def sentry_mode():
    talk("Sentry Activated. You have 5 seconds.")
    time.sleep(5)
    cap = cv2.VideoCapture(0)
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    while cap.isOpened():
        if frame1 is None or frame2 is None: break
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        movement = False
        for contour in contours:
            if cv2.contourArea(contour) < 5000: continue
            movement = True
            
        if movement:
            if winsound: winsound.Beep(1000, 500)
            talk("Intruder detected!")
            break

        frame1 = frame2
        ret, frame2 = cap.read()
        if cv2.waitKey(10) == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()

# --- RUN LOGIC ---
def run_ai():
    global IS_AWAKE
    command = take_command()
    if not command:
        time.sleep(0.5) # Prevents high CPU/Blinking
        return True

    # WAKE / SLEEP
    if 'wake up' in command:
        IS_AWAKE = True
        talk("I am awake and ready.")
        return True
    elif 'go to sleep' in command:
        IS_AWAKE = False
        talk("Going to sleep. Call me if you need me.")
        return True

    # ACTIONS (Only if Awake)
    if IS_AWAKE:
        if 'look at this' in command:
            analyze_vision()
        elif 'activate sentry mode' in command:
            IS_AWAKE = False
            sentry_mode()
        elif 'clean my desktop' in command:
            talk("Cleaning...")
            # (Desktop cleaning logic as before)
        elif 'write a note about' in command:
            topic = command.replace('write a note about', '')
            response = model.generate_content(f"Short paragraph about {topic}")
            os.system('start notepad')
            time.sleep(2)
            pyautogui.typewrite(response.text)
        elif 'play' in command:
            pywhatkit.playonyt(command.replace('play', ''))
        elif 'stop' in command:
            talk("Shutting down.")
            sys.exit()
        else:
            # GENERAL AI QUESTION
            try:
                response = model.generate_content(f"User says: {command}. Answer in 1 short sentence.")
                talk(response.text)
            except:
                talk("I didn't understand that.")

    return True

# --- START ---
if __name__ == "__main__":
    talk("System Ultimate Online.")
    while True:
        run_ai()