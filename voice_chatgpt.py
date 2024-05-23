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
openai.api_key = os.getenv("secret_key")


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
    status_label.config(text="Recording...")
    for _ in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Finished recording.")
    status_label.config(text="Finished recording.")

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
root.geometry('600x400')  # Set a fixed size for the window

# Custom colors and fonts
bg_color = '#282c34'
text_color = '#abb2bf'
button_color = '#61afef'
font_style = ("Helvetica", 12)
response_font = ("Helvetica", 10, "italic")

root.configure(bg=bg_color)

frame = tk.Frame(root, bg=bg_color)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

record_button = tk.Button(frame, text="Record Audio", command=start_process, bg=button_color, fg=text_color,
                          font=font_style)
record_button.pack(pady=20)

response_textbox = tk.Text(frame, wrap=tk.WORD, height=15, width=75, bg="#1e2127", fg=text_color, font=response_font,
                           borderwidth=2, relief="flat")
response_textbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame, command=response_textbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
response_textbox.config(yscrollcommand=scrollbar.set)

status_label = tk.Label(frame, text="Ready", bg=bg_color, fg=text_color, font=font_style)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
