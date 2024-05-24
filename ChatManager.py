import openai
import pyttsx3
import logging

class ChatManager:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_response(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                api_key=self.api_key
            )
            answer = response.choices[0].message['content'].strip()
            logging.info("Received response from ChatGPT: " + answer)
            return answer
        except Exception as e:
            logging.error("Error in ChatGPT response: {0}".format(e))
            return "There was an error processing the request."

    def text_to_speech(self, text):
        engine = pyttsx3.init()
        try:
            engine.say(text)
            engine.runAndWait()
            logging.info("Converted text to speech successfully.")
        except Exception as e:
            logging.error("Failed to convert text to speech: {0}".format(e))
