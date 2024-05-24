import tkinter as tk
from AudioManager import AudioManager
from ChatManager import ChatManager
from ConfigManager import ConfigManager
import threading


class VoiceChatApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Voice Chat with ChatGPT")
        self.master.geometry('800x600')  # Bigger window for better layout
        self.master.configure(bg='#36393F')  # Discord dark background color

        self.config_manager = ConfigManager()
        self.audio_manager = AudioManager()
        self.chat_manager = ChatManager(self.config_manager.get_api_key())

        self.setup_ui()

    def setup_ui(self):
        # Frame for buttons and status
        top_frame = tk.Frame(self.master, bg='#2F3136', pady=10, padx=10)  # Slightly lighter than the background
        top_frame.grid(row=0, sticky='ew', padx=10)
        top_frame.grid_columnconfigure(0, weight=1)

        # Record button
        self.record_button = tk.Button(top_frame, text="Record & Chat", command=self.start_process,
                                       font=('Calibri', 14, 'bold'), bg='#7289DA', fg='white', relief='ridge')
        self.record_button.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Status label
        self.status_label = tk.Label(top_frame, text="Ready to record", bg='#2F3136', fg='white', font=('Calibri', 12))
        self.status_label.grid(row=1, column=0, sticky='ew', padx=10, pady=5)

        # Frame for text display
        text_frame = tk.Frame(self.master, bg='#2F3136', padx=10, pady=10)
        text_frame.grid(row=1, sticky='nsew', padx=10, pady=5)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        # Text widget for displaying conversation
        self.conversation_text = tk.Text(text_frame, wrap='word', bg='#40444B', fg='#CCCCCC',
                                         font=('Calibri', 12), borderwidth=2, relief="groove")
        self.conversation_text.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Scrollbar for the text widget
        scrollbar = tk.Scrollbar(text_frame, command=self.conversation_text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.conversation_text.config(yscrollcommand=scrollbar.set)

    def start_process(self):
        self.status_label.config(text="Processing...")
        thread = threading.Thread(target=self.process_audio)
        thread.start()

    def process_audio(self):
        filename = "input.wav"
        self.audio_manager.record_audio(filename)
        text = self.audio_manager.recognize_speech(filename)
        if text:
            response = self.chat_manager.get_response(text)
            self.display_conversation("You: " + text)
            self.display_conversation("ChatGPT: " + response)
            self.chat_manager.text_to_speech(response)
        self.status_label.config(text="Ready to record")

    def display_conversation(self, message):
        self.conversation_text.insert(tk.END, message + "\n\n")
        self.conversation_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceChatApp(root)
    root.mainloop()
