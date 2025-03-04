import speech_recognition as sr
import pywhatkit as pw
import datetime as dt
import webbrowser
import requests
import cv2
import os
import time
import openai
import platform
import psutil
import winsound
import threading
import subprocess
import pyautogui
import playsound3 as playsoundf
import nltk
import pyttsx3 as pt
from translate import Translator
from textblob import TextBlob
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import wikipedia
import calendar
import tempfile

# Initialize recognizer and text-to-speech engine
listener = sr.Recognizer()
engine = pt.init()

# Set voice properties
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Use a different voice if needed

# NewsAPI Configuration
NEWS_API_KEY = "cacc40f2bde84cfea9d5750c715a2115"  # Replace with your NewsAPI key
NEWS_API_URL = "https://newsapi.org/v2/top-headlines?country=us&apiKey=" + NEWS_API_KEY

OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# Global flag to control task execution
is_running = True


def talk(text):
    """Converts text to speech"""
    engine.say(text)
    engine.runAndWait()


def take_command():
    """Listens to the user's command and returns it as text"""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source, timeout=5)
            command = listener.recognize_google(voice, language="en-US")
            command = command.lower()
            if 'chitti' in command:
                command = command.replace('chitti', '').strip()
            return command
    except sr.UnknownValueError:
        talk("Sorry, I could not understand.")
    except sr.RequestError:
        talk("Could not request results. Check your internet connection.")
    except Exception as e:
        print(f"Error: {e}")
        talk("An error occurred")
    return ""


def translate_text(text, target_language="es"):
    """
    Translates the given text to the target language using the `translate` library.
    Default target language is Spanish ('es').
    """
    try:
        translator = Translator(to_lang=target_language)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"Translation error: {e}")
        return None


def open_application(app_name):
    """Opens an application based on the given name"""
    try:
        # Map application names to their executable paths
        app_paths = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "word document": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
            "paint": "mspaint.exe",
            "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            # Add more applications and their paths as needed
        }

        if app_name in app_paths:
            subprocess.Popen(app_paths[app_name])
            talk(f"Opening {app_name}")
            print(f"Opening {app_name}")
        else:
            talk(f"Sorry, I don't know how to open {app_name}.")
            print(f"Application {app_name} not found in the list.")
    except Exception as e:
        talk(f"Sorry, I couldn't open {app_name}.")
        print(f"Error: {e}")


def close_application(app_name):
    """
    Closes an application by its name.

    Args:
        app_name (str): The name of the application to close (e.g., "chrome", "notepad").
    """
    try:
        # Map application names to their process names
        app_paths = {
            "notepad": "notepad.exe",
            "calculator": "calculator.exe",
            "chrome": "chrome.exe",
            "word document": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "paint": "mspaint.exe",
            "vlc": "vlc.exe",
            # Add more applications and their paths as needed
        }

        if app_name in app_paths:
            process_name = app_paths[app_name]

            # Platform-specific logic to close the application
            if platform.system() == "Windows":
                # Windows: Use taskkill to terminate the process
                executable_name = app_mapping.get(app_name.lower(), app_name)
                os.system(f'taskkill /IM "{executable_name}.exe" /F')
            elif platform.system() == "Linux" or platform.system() == "Darwin":  # Darwin is macOS
                # Linux/macOS: Use pkill to terminate the process
                os.system(f"pkill {process_name}")
            else:
                talk("Sorry, this feature is not supported on your operating system.")
                return

            talk(f"Closed {app_name}.")
            print(f"Closed {app_name}.")
        else:
            talk(f"Sorry, I don't know how to close {app_name}.")
            print(f"Application {app_name} not found in the list.")
    except Exception as e:
        talk(f"Sorry, I couldn't close {app_name}.")
        print(f"Error: {e}")




# Run this in a background thread for continuous listening

def get_directions(destination):
    """Opens Google Maps with directions to the given destination"""
    base_url = "https://www.google.com/maps/dir/?api=1&destination="
    destination = destination.replace(" ", "+")
    maps_url = base_url + destination
    webbrowser.open(maps_url)
    talk(f"Getting directions to {destination}")
    print(f"Opening Google Maps for directions to {destination}")


def search_wikipedia(query):
    """Searches Wikipedia for the given query."""
    try:
        info = wikipedia.summary(query, sentences=3)  # Get a short summary
        talk(info)
        print(f"Wikipedia search: {info}")
    except wikipedia.exceptions.DisambiguationError as e:
        talk("There are multiple matches. Please be more specific.")
        print(f"Wikipedia disambiguation error: {e}")
    except wikipedia.exceptions.PageError:
        talk("Sorry, I couldn't find any information on that.")
    except Exception as e:
        print(f"Error in search_wikipedia(): {e}")
        talk("Sorry, I couldn't fetch the information.")


def calculate(command):
    """Performs basic mathematical calculations"""
    try:
        # Replace words with mathematical symbols
        command = command.replace('plus', '+').replace('minus', '-').replace('times', '*').replace('divided by', '/')

        # Extract the mathematical expression
        expression = ''.join([char for char in command if char in '0123456789+-*/. ']).strip()

        if not expression:
            talk("I couldn't find a valid mathematical expression.")
            return

        # Evaluate the expression
        result = eval(expression)
        talk(f"The result is {result}")
        print(f"Calculation: {expression} = {result}")

    except Exception as e:
        talk("Sorry, I couldn't perform the calculation.")
        print(f"Error: {e}")


def get_meaning(word):
    """Fetches and speaks the meaning of a word using Free Dictionary API"""
    try:
        # Fetch word meaning from Free Dictionary API
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            meanings = data[0]['meanings']
            response_text = f"The meaning of {word} is: "
            for meaning in meanings:
                part_of_speech = meaning['partOfSpeech']
                definition = meaning['definitions'][0]['definition']
                response_text += f"{part_of_speech}: {definition}. "
            talk(response_text)
            print(response_text)
        else:
            talk(f"Sorry, I couldn't find the meaning of {word}.")
    except Exception as e:
        talk("Sorry, I couldn't fetch the meaning.")
        print(f"Error: {e}")


def get_news():
    """Fetches and reads the latest news headlines"""
    global is_running
    try:
        response = requests.get(NEWS_API_URL)
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data['articles']
            talk("Here are the top news headlines.")
            for i, article in enumerate(articles[:5]):  # Read top 5 headlines
                if not is_running:
                    break  # Stop if interrupted
                title = article['title']
                talk(f"News {i + 1}: {title}")
                print(f"News {i + 1}: {title}")
        else:
            talk("Sorry, I couldn't fetch the news.")
    except Exception as e:
        talk("Sorry, I couldn't fetch the news.")
        print(f"Error: {e}")


def get_date():
    """Fetches and speaks today's date"""
    today = dt.datetime.now()
    date_str = today.strftime("%A, %B %d, %Y")  # Format: Day, Month Day, Year
    talk(f"Today is {date_str}")
    print(f"Today is {date_str}")


def show_calendar():
    """Displays the calendar for the current month"""
    today = dt.datetime.now()
    year = today.year
    month = today.month
    cal = calendar.month(year, month)
    talk("Here is the calendar for this month.")
    print(cal)


def get_system_info():
    info = f"""
    System: {platform.system()}
    Node Name: {platform.node()}
    Release: {platform.release()}
    Version: {platform.version()}
    Processor: {platform.processor()}
    RAM: {round(psutil.virtual_memory().total / (1024 ** 3))} GB
    """
    talk(info)
    print(info)


def shutdown_computer():
    """Shuts down the computer."""
    try:
        talk("Are you sure you want to shutdown the computer?")
        response = take_command()
        if response and "yes" in response:
            talk("Shutting down the computer.")
            os.system("shutdown /s /t 1")  # For Windows
            # os.system("shutdown now")  # For Linux/Mac
        else:
            talk("Shutdown canceled.")
    except Exception as e:
        print(f"Error in shutdown_computer(): {e}")
        talk("Sorry, I couldn't shut down the computer.")



def restart_computer():
    """Restarts the computer."""
    try:
        talk("Restarting the computer.")
        os.system("shutdown /r /t 1")  # For Windows
        # os.system("reboot")  # For Linux/Mac
    except Exception as e:
        print(f"Error in restart_computer(): {e}")
        talk("Sorry, I couldn't restart the computer.")


def lock_computer():
    """Locks the computer."""
    try:
        talk("Locking the computer.")
        os.system("rundll32.exe user32.dll,LockWorkStation")  # For Windows
        # os.system("pmset displaysleepnow")  # For Mac
    except Exception as e:
        print(f"Error in lock_computer(): {e}")
        talk("Sorry, I couldn't lock the computer.")


def move_mouse(x, y):
    pyautogui.moveTo(x, y, duration=0.5)


def click():
    pyautogui.click()


def type_text(text):
    pyautogui.write(text, interval=0.1)

def take_screenshot():
    """Takes a screenshot and saves it to the current directory."""
    try:
        screenshot = pyautogui.screenshot()
        screenshot_name = f"screenshot_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot.save(screenshot_name)
        talk("Screenshot taken and saved.")
        print(f"Screenshot saved as {screenshot_name}")
    except Exception as e:
        talk("Sorry, I couldn't take a screenshot.")
        print(f"Error: {e}")

def ask_chatgpt(question):
    """Sends a query to ChatGPT and returns the response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the latest available model
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": question}
            ]
        )
        answer = response["choices"][0]["message"]["content"]
        return answer
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't process that request."


def take_photo():
    """Takes a photo using the webcam and saves it to the current directory."""
    try:
        # Initialize the webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            talk("Sorry, I couldn't access the webcam.")
            return

        # Capture a frame
        ret, frame = cap.read()
        if ret:
            photo_name = f"photo_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cv2.imwrite(photo_name, frame)
            talk("Photo taken and saved.")
            print(f"Photo saved as {photo_name}")
        else:
            talk("Sorry, I couldn't capture a photo.")

        # Release the webcam
        cap.release()
    except Exception as e:
        talk("Sorry, I couldn't take a photo.")
        print(f"Error: {e}")


def set_alarm(alarm_time):
    """Sets an alarm for the specified time."""

    def alarm_thread():
        while True:
            current_time = time.strftime("%H:%M")
            if current_time == alarm_time:
                talk("Time to wake up!")
                print("Alarm ringing!")
                for _ in range(5):  # Ring alarm 5 times
                    winsound.Beep(1000, 1000)
                break
            time.sleep(30)  # Check every 30 seconds

    threading.Thread(target=alarm_thread, daemon=True).start()
    talk(f"Alarm set for {alarm_time}.")
    print(f"Alarm set for {alarm_time}.")

def listen_for_stop():
    """Listen for the stop command."""
    global is_running
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for stop command...")
        while is_running:
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")
                if "stop" in command or "cancel" in command:
                    is_running = False
                    print("Stop command detected.")
                    talk("Stopping the current task.")
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError:
                print("Speech recognition service failed.")



def introduce_chitti():
    intro_text = ("Namasthey! I am Chitti . loaded version 1 point o , your personal AI Voice assistant . "
                  " I can help you with various tasks like fetching news , performing basic "
                  "calculations , playing songs and videos on Youtube , giving directions to your destination , "
                  "opening applications , can perform beginner user command operations and much more.")
    print(intro_text)
    talk(intro_text)


def intro_chitti():
    intr_text = ("I can help you with various tasks like fetching news , performing basic "
                 "calculations , playing songs and videos on Youtube , giving directions to your destination , "
                 "opening applications , can perform beginner user command operations and much more.")
    print(intr_text)
    talk(intr_text)


def greet():
    """Greets the user"""
    talk("Hello! I'm Chitti. How can I help you today?")


def run_chitti():
    """Processes user commands"""
    global is_running
    greet()
    while True:
        command = take_command()
        if not command:
            continue

        print(f"User said: {command}")

        if 'play' in command:
            song = command.replace('play', '').strip()
            talk(f"Playing {song}")
            print(f"Playing {song}")
            is_running = True
            threading.Thread(target=listen_for_stop).start()  # Start listening for stop
            pw.playonyt(song)

        elif 'time' in command:
            time = dt.datetime.now().strftime('%I:%M %p')
            print(f"Current time: {time}")
            talk(f"Right now, the time is {time}")

        elif 'directions to' in command or 'navigate to' in command:
            destination = command.replace('directions to', '').replace('navigate to', '').strip()
            if destination:
                get_directions(destination)
            else:
                talk("I didn't catch the destination. Please try again.")

        elif 'search for' in command:
            query = command.replace('search for', '').strip()
            if query:
                talk(f"Searching for {query}")
                talk(pw.search(query))

        elif 'calculate' in command or 'what is' in command:
            if 'meaning' not in command:  # Avoid conflict with word meanings
                calculate(command)

        elif 'meaning of' in command or 'define' in command:
            word = command.replace('meaning of', '').replace('define', '').strip()
            if word:
                get_meaning(word)
            else:
                talk("I didn't catch the word. Please try again.")

        elif 'open' in command:
            app_name = command.replace('open', '').strip()
            if app_name:
                open_application(app_name)
            else:
                talk("I didn't catch the application name. Please try again.")
        elif 'close' in command:
            app_name = command.replace('close', '').strip()
            if app_name:
                close_application(app_name)
            else:
                talk("I didn't catch the application name. Please try again.")

        elif 'news' in command or 'headlines' in command:
            is_running = True
            threading.Thread(target=listen_for_stop).start()  # Start listening for stop
            get_news()

        elif 'date' in command or 'today' in command:
            get_date()

        elif 'calendar' in command:
            show_calendar()

        elif 'who' in command:
            person = command.replace('who', '')
            info = wikipedia.summary(person, 5)
            print(info)
            talk(info)

        elif 'shutdown computer' in command:

            shutdown_computer()

        elif 'restart computer' in command:
            restart_computer()

        elif 'lock computer' in command:
            lock_computer()

        elif "move the mouse" in command:
            talk("Give me X and Y coordinates.")
            x = int(take_command())
            y = int(take_command())
            move_mouse(x, y)

        elif "click" in command:
            click()

        elif "type" in command:
            talk("What should I type?")
            text = take_command()
            type_text(text)

        elif "system info" in command:
            get_system_info()

        elif "introduce yourself" in command:
            introduce_chitti()

        elif "what can you do" in command:
            intro_chitti()

        elif 'translate' in command:
            talk("What do you want to translate?")
            text_to_translate = take_command()
            if text_to_translate:
                talk("To which language? Please say the language code, like 'es' for Spanish or 'fr' for French.")
                target_lang =input("> ") or take_command()
                if target_lang:
                    translated_text = translate_text(text_to_translate, target_lang)
                    if translated_text:
                        talk(f"The translation is: {translated_text}")
                        print(f"Translated text: {translated_text}")
                    else:
                        talk("Sorry, I couldn't translate that.")
                else:
                    talk("I didn't catch the target language. Please try again.")
            else:
                talk("I didn't catch the text to translate. Please try again.")

        elif 'take screenshot' in command or 'capture screen' in command:
            take_screenshot()

        elif 'take photo' in command or 'capture photo' in command:
            take_photo()
        elif "set alarm for" in command:
            alarm_time = command.replace("set alarm for", "").strip()
            set_alarm(alarm_time)
        elif 'chat' in command or 'ask' in command or 'talk to me' in command:
            talk("What would you like to ask?")
            user_query = take_command()
            if user_query:
                response = ask_chatgpt(user_query)
                talk(response)
                print("ChatGPT:", response)
            else:
                talk("I didn't catch that. Please ask again.")


        elif 'exit' in command or 'stop' in command:
            talk("Goodbye!")
            print("Exiting.....")
            break
        else:
            talk('Please say the command again.')

# Run the assistant in the background
def start_assistant():
    """Starts the assistant in a separate thread."""
    assistant_thread = threading.Thread(target=run_chitti, daemon=True)
    assistant_thread.start()
    return assistant_thread

# Run the assistant
if __name__ == "__main__":
    try:
        run_chitti()
    except Exception as e:
        # Catch any unhandled exceptions in the main thread
        print(f"Fatal error: {e}")
        traceback.print_exc()
        talk("A critical error occurred. Restarting the assistant.")
        run_chitti()  # Restart the assistant