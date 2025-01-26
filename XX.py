import speech_recognition as sr
import os
import random
import datetime
import pyjokes
import webbrowser
import playsound
import google.generativeai as genai
import re  # For cleaning unwanted formatting
import edge_tts  # Install using 'pip install edge-tts'
import asyncio  # Required for Edge TTS

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

# Transaction Data
TRANSACTIONS = [
    {"date_transacted": "2025-01-09", "amount": -4570.48, "description": "LIC Insurance Premium", "currency": "USD"},
    {"date_transacted": "2025-01-06", "amount": -4820.43, "description": "Mutual Fund SIP", "currency": "USD"},
    {"date_transacted": "2024-12-24", "amount": -4886.4, "description": "Google Play Purchase", "currency": "USD"},
    # Add more transactions if needed
]

FINANCE_PROMPT = """
You are a highly knowledgeable financial assistant specializing in loans, credit, and personal finance. 
Your sole responsibility is to provide accurate, concise, and helpful answers to questions strictly related to financial topics.
"""


def format_transactions(transactions):
    """Format transactions into a human-readable string."""
    formatted = ""
    for t in transactions:
        formatted += f"- Date: {t['date_transacted']} | Amount: {t['amount']} {t['currency']} | Description: {t['description']}\n"
    return formatted.strip()


def get_gemini_response(user_input, transactions=None):
    """Get a response from the Gemini model."""
    try:
        if transactions:
            formatted_transactions = format_transactions(transactions)
            combined_input = f"{FINANCE_PROMPT}\nTransactions:\n{formatted_transactions}\nUser Query: {user_input}"
        else:
            combined_input = f"{FINANCE_PROMPT}\nUser Query: {user_input}"

        response = chat_session.send_message(combined_input)
        cleaned_response = re.sub(r"\*", "", response.text).strip()
        return cleaned_response
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return "Sorry, I couldn't process that request."


async def talk(audio):
    """Speak the text aloud using Edge TTS."""
    print(f"Speaking: {audio}")
    communicate = edge_tts.Communicate()
    try:
        await communicate.tts(audio, voice="en-US-AriaNeural", rate="+5%")
    except Exception as e:
        print(f"Error with Edge TTS: {e}")


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
        asyncio.run(talk("I could not understand that. Can you repeat?"))
    except sr.RequestError as ex:
        print("Request Error from Google Speech Recognition", ex)
        asyncio.run(talk("There was an issue with the speech recognition service. Please try again."))
    except Exception as e:
        print(f"Error in rec_audio: {e}")
        asyncio.run(talk("An error occurred while listening."))
    return data.lower()


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
                    asyncio.run(talk(f"Today is {now.strftime('%A, %B %d, %Y')}"))

                elif "time" in text:
                    now = datetime.datetime.now()
                    meridiem = "p.m." if now.hour >= 12 else "a.m."
                    hour = now.hour - 12 if now.hour > 12 else now.hour
                    minute = f"{now.minute:02d}"
                    asyncio.run(talk(f"It is {hour}:{minute} {meridiem}."))

                elif "joke" in text:
                    asyncio.run(talk(pyjokes.get_joke()))

                elif "transaction" in text or "my" in text:
                    asyncio.run(talk("Let me check your transactions for you."))
                    response = get_gemini_response(text, TRANSACTIONS)
                    asyncio.run(talk(response))

                elif "exit" in text or "quit" in text:
                    asyncio.run(talk("Goodbye!"))
                    break

                else:
                    response = get_gemini_response(text)
                    asyncio.run(talk(response))

        except Exception as e:
            asyncio.run(talk("I don't know that."))
            print(f"Error: {e}")


# Run the assistant
asyncio.run(talk("Hello, how can I assist you today?"))
assistant_loop()
