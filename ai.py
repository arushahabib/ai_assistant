import pyttsx3
import speech_recognition as sr
import os
import random
import time
import datetime
import pyjokes
import webbrowser
import wikipedia
import playsound
import requests
import json
import subprocess
import google.generativeai as genai

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Configure Google Generative AI
GEMINI_API_KEY = "AIzaSyD5pZAB-36xAyckGmW4_DM4ayivQ9dUKuk"  # Replace with your actual Gemini API key
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

def talk(audio):
    """Speak the text aloud."""
    print(f"Speaking: {audio}")
    engine.say(audio)
    engine.runAndWait()

def rec_audio():
    """Record and recognize speech from the microphone."""
    recog = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        audio = recog.listen(source)

    data = ""
    try:
        data = recog.recognize_google(audio)
        print("You said: " + data)
    except sr.UnknownValueError:
        print("Assistant could not understand the audio")
        talk("I could not understand that. Can you repeat?")
    except sr.RequestError as ex:
        print("Request Error from Google Speech Recognition", ex)
        talk("There was an issue with the speech recognition service. Please try again.")
    except Exception as e:
        print(f"Error in rec_audio: {e}")
        talk("An error occurred while listening.")
    return data.lower()

def get_gemini_response(user_input):
    """Get a response from the Gemini model."""
    try:
        response = chat_session.send_message(user_input)
        return response.text
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return "Sorry, I couldn't process that request."

def assistant_loop():
    """Main loop for the voice assistant."""
    while True:
        try:
            print("Start Listening")
            text = rec_audio()
            print(f"Recognized Text: {text}")

            if text.strip() == "":
                continue

            if "assistant" in text:


                if "date" in text or "day" in text or "month" in text:
                    now = datetime.datetime.now()
                    talk(f"Today is {now.strftime('%A, %B %d, %Y')}")

                elif "time" in text:
                    now = datetime.datetime.now()
                    meridiem = "p.m." if now.hour >= 12 else "a.m."
                    hour = now.hour - 12 if now.hour > 12 else now.hour
                    minute = f"{now.minute:02d}"
                    talk(f"It is {hour}:{minute} {meridiem}.")

                elif "joke" in text:
                    talk(pyjokes.get_joke())

                elif "search" in text.lower():
                    query = text.lower().split("search")[-1].strip()
                    talk(f"Searching for {query} on Google.")
                    webbrowser.open(f"https://www.google.com/search?q={query}")

                elif "who was" in text or "what is" in text or "who is" in text:
                    talk("Let me find that out for you.")
                    response = get_gemini_response(text)
                    talk(response)

                elif "play music" in text or "play song" in text:
                    talk("Here you go with music")
                    music_dir = r"C:\Path\To\Your\Music"  # Provide the correct music directory path
                    if os.path.exists(music_dir):
                        songs = os.listdir(music_dir)
                        if songs:
                            random_song = random.choice(songs)
                            playsound.playsound(os.path.join(music_dir, random_song))
                        else:
                            talk("The music directory is empty.")
                    else:
                        talk("I couldn't find the music directory.")

                elif "exit" in text or "quit" in text:
                    talk("Goodbye!")
                    break

                else:
                    talk("Let me check that for you.")
                    response = get_gemini_response(text)
                    talk(response)

        except Exception as e:
            talk("I don't know that.")
            print(f"Error: {e}")

# Start the assistant
talk("Hello, how can I assist you today?")
assistant_loop()
