import tkinter as tk
import pyaudio
import wave
import speech_recognition as sr
import openai
import pyttsx3
import threading
import os
from dotenv import load_dotenv


load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("openai.api_key")


# Function to record audio
def record_audio(filename="input.wav", duration=5):
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 44100  # Record at 44100 samples per second
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    frames = []  # Initialize array to store frames

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    print("Recording...")

    for _ in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Finished recording.")

    # Save the recorded data as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))

    # Convert the recorded audio to text
    recognized_text = recognize_speech(filename)

    return recognized_text


# Function to recognize speech from audio
def recognize_speech(filename="input.wav"):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)  # Read the entire audio file

    try:
        print("Recognizing speech...")
        text = recognizer.recognize_google(audio)
        print(f"Recognized Text: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""


# Function to get response from ChatGPT
def get_chatgpt_response(prompt):
    try:
        # Mock response if the API quota is exceeded
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response['choices'][0]['message']['content'].strip()
        print(f"ChatGPT: {answer}")
        return answer
    except openai.error.RateLimitError as e:
        print(f"Rate limit error: {e}")
        return "You have exceeded your API quota. Please check your OpenAI plan and billing details."
    except Exception as e:
        print(f"Error: {e}")
        return "There was an error processing the request."


# Function to convert text to speech
def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


# Function to handle the entire process
def process_audio():
    recognized_text = record_audio()
    if recognized_text:
        chatgpt_response = get_chatgpt_response(recognized_text)
        update_response_textbox(f"User: {recognized_text}\nChatGPT: {chatgpt_response}\n\n")
        text_to_speech(chatgpt_response)


# Function to update the response textbox
def update_response_textbox(text):
    response_textbox.insert(tk.END, text)
    response_textbox.see(tk.END)


# Function to start the process in a new thread
def start_process():
    thread = threading.Thread(target=process_audio)
    thread.start()


# Set up the Tkinter GUI
root = tk.Tk()
root.title("Voice Chat with ChatGPT")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

record_button = tk.Button(frame, text="Record Audio", command=start_process)
record_button.pack()

response_textbox = tk.Text(frame, wrap=tk.WORD, height=20, width=50)
response_textbox.pack(padx=10, pady=10)

root.mainloop()
