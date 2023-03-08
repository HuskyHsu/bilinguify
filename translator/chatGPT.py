from configparser import ConfigParser
from itertools import cycle
from typing import Iterable

import requests
from pydantic import BaseModel


class ChatGPT(BaseModel):
    url: str = "https://api.openai.com/v1/chat/completions"
    language: str
    api_keys: Iterable[str]
    base_payload: dict = {}

    @classmethod
    def _process_payload_config(self, config):
        payload_items = dict(config.items("openai.payload"))
        number_items = (
            dict(config.items("openai.payload.number"))
            if "openai.payload.number" in config
            else {}
        )
        number_items_converted = {k: float(v) for k, v in number_items.items()}

        return {**payload_items, **number_items_converted}

    def __init__(self, config_path: str):
        config = ConfigParser()
        config.read(config_path)
        language = config.get("translation", "language", fallback="Traditional Chinese")
        api_keys = cycle(config.get("openai", "api_key").split(","))
        base_payload = self._process_payload_config(config)

        super().__init__(
            api_keys=api_keys, base_payload=base_payload, language=language
        )

    def _get_header(self):
        return {"Authorization": f"Bearer {next(self.api_keys)}"}

    def call_api(self, message):
        data = {
            **self.base_payload,
            "messages": [
                {
                    "role": "system",
                    "content": f"I want you to act as an English translator. Please translate the following sentence into {self.language} while keeping its original meaning in English as much as possible and return only translated content not include the origin text.",
                },
                {"role": "user", "content": message},
            ],
        }
        response = requests.post(self.url, headers=self._get_header(), json=data)
        response.raise_for_status()
        result = response.json()

        return result["choices"][0]["message"]["content"].strip()
