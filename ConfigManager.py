import logging
import os
from dotenv import load_dotenv


class ConfigManager:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("secret_key")
        self.configure_logging()

    def configure_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            filename='app.log',
            filemode='a',
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_api_key(self):
        if self.api_key is None:
            logging.error("API key is not loaded. Check your .env file.")
        return self.api_key
