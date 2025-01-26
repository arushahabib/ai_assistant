import pyttsx3
import speech_recognition as sr
import os
import random
import datetime
import pyjokes
import webbrowser
import playsound
import google.generativeai as genai
import re  # For cleaning unwanted formatting

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

# Transaction Data
TRANSACTIONS = [
    {"date_transacted": "2025-01-09", "amount": -4570.48, "description": "LIC Insurance Premium", "currency": "USD"},
    {"date_transacted": "2025-01-06", "amount": -4820.43, "description": "Mutual Fund SIP", "currency": "USD"},
    {"date_transacted": "2024-12-24", "amount": -4886.4, "description": "Google Play Purchase", "currency": "USD"},
    {"date_transacted": "2024-12-18", "amount": -1798.22, "description": "Uber Ride", "currency": "USD"},
    {"date_transacted": "2024-12-26", "amount": -1194.49, "description": "Uber Ride", "currency": "USD"},
    {"date_transacted": "2024-12-27", "amount": -3144.86, "description": "Amazon Purchase", "currency": "USD"},
    {"date_transacted": "2024-12-19", "amount": -1957.1, "description": "PhonePe Transfer", "currency": "USD"},
    {"date_transacted": "2025-01-07", "amount": -2527.15, "description": "Discover credit card payment",
     "currency": "USD"},
    {"date_transacted": "2024-12-27", "amount": -4148.83, "description": "ATM Withdrawal", "currency": "USD"},
    {"date_transacted": "2024-12-20", "amount": -3629.7, "description": "Amazon Purchase", "currency": "USD"},
    {"date_transacted": "2025-01-13", "amount": -2100.43, "description": "Fuel Payment - HPCL", "currency": "USD"},
    {"date_transacted": "2025-01-01", "amount": 75000, "description": "Salary Credit", "currency": "USD"},
    {"date_transacted": "2024-12-19", "amount": -2488.91, "description": "Amazon Purchase", "currency": "USD"},
]

# Financial Assistant Prompt
FINANCE_PROMPT = """
You are a highly knowledgeable financial assistant specializing in loans, credit, and personal finance. 
Your sole responsibility is to provide accurate, concise, and helpful answers to questions strictly related to financial topics.

These topics include:
1. Types of loans (personal, home, auto, student, business, etc.).
2. Loan eligibility, interest rates, and repayment terms.
3. Credit scores and their impact on loan applications.
4. Budgeting, saving, and financial planning.
5. Banking products and services (e.g., savings accounts, credit cards).
6. Investment options and strategies.

If a user asks a question outside the scope of loans and finances, politely redirect them by saying:
"I'm here to assist only with loan and financial queries. Please ask me something related to those topics."
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
        # Combine the prompt with the user input and transaction data
        if transactions:
            formatted_transactions = format_transactions(transactions)
            combined_input = f"{FINANCE_PROMPT}\nTransactions:\n{formatted_transactions}\nUser Query: {user_input}"
        else:
            combined_input = f"{FINANCE_PROMPT}\nUser Query: {user_input}"

        # Send message to Gemini
        response = chat_session.send_message(combined_input)

        # Clean the response text to remove all asterisks
        cleaned_response = re.sub(r"\*", "", response.text).strip()  # Remove all '*' characters
        return cleaned_response
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return "Sorry, I couldn't process that request."


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


def assistant_loop():
    """Main loop for the voice assistant."""
    while True:
        try:
            print("Start Listening")
            text = rec_audio()
            print(f"Recognized Text: {text}")

            if text.strip() == "":
                continue

            # Check for "hello"
            if "hello" in text:
                talk("Hello! How can I assist you today?")

            elif "assistant" in text:
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

                elif "transaction" in text or "my" in text:
                    talk("Let me check your transactions for you.")
                    response = get_gemini_response(text, TRANSACTIONS)
                    talk(response)

                elif "exit" in text or "quit" in text:
                    talk("Goodbye!")
                    break

                else:
                    response = get_gemini_response(text)
                    talk(response)

        except Exception as e:
            talk("I don't know that.")
            print(f"Error: {e}")


talk("Hello, how can I assist you today?")
assistant_loop()
