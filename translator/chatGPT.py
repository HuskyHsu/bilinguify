from configparser import ConfigParser

import requests
from pydantic import BaseModel


class ChatGPT(BaseModel):
    url: str = "https://api.openai.com/v1/chat/completions"
    headers: dict = {}
    base_payload: dict = {}
    language: str

    @classmethod
    def from_config(cls):
        config = ConfigParser()
        config.read("config.ini")

        headers = {"Authorization": f"Bearer {config.get('openai', 'api_key')}"}
        payload = cls._process_payload_config(config)
        language = config.get("translation", "language", fallback="Traditional Chinese")

        return cls(headers=headers, base_payload=payload, language=language)

    @classmethod
    def _process_payload_config(cls, config):
        payload_items = config.items("openai.payload")
        number_items = (
            config.items("openai.payload.number")
            if "openai.payload.number" in config
            else []
        )
        number_items_converted = [
            [config[0], float(config[1])] for config in number_items
        ]

        return dict(payload_items + number_items_converted)

    def call_api(self, message):
        data = {
            **self.base_payload,
            "messages": [
                {
                    "role": "system",
                    "content": "I want you to act as an English translator. Please translate the following sentence into Traditional Chinese while keeping its original meaning in English as much as possible and return only translated content not include the origin text.",
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        response.raise_for_status()  # Raises an exception if the response status code is not ok (200)
        result = response.json()

        # print(result)
        return result["choices"][0]["message"]["content"].strip()
