import pyaudio
import wave
import speech_recognition as sr
import logging


class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def record_audio(self, filename="input.wav", duration=5):
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 44100
        p = pyaudio.PyAudio()
        frames = []
        stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)

        logging.info("Recording started.")
        for _ in range(0, int(fs / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        logging.info("Finished recording.")

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b''.join(frames))

    def recognize_speech(self, filename="input.wav"):
        with sr.AudioFile(filename) as source:
            audio_data = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google(audio_data)
            logging.info("Speech recognized: " + text)
            return text
        except sr.UnknownValueError:
            logging.error("Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            logging.error("Could not request results; {0}".format(e))
            return ""
