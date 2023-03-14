from configparser import ConfigParser
from itertools import cycle
from typing import Iterable
import time

import requests
from pydantic import BaseModel


class ChatGPT(BaseModel):
    url: str = "https://api.openai.com/v1/chat/completions"
    system_prompt: str
    api_keys: Iterable[str]
    base_payload: dict = {}

    rate_limit: float
    last_request: dict = {}

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
        system_prompt = f"""
            I want you to act as a professional English translator.
            Please translate the following sentence into {language} while keeping its original meaning in English as much as possible.
            Make the translation readable and intelligible.
            Be elegant and natural in your translation.
            Do not translate any personal names.
            Do not add any additional text to the translation.
            Please only return the translated content and do not include the original text.
        """.replace(
            "  ", ""
        ).strip()

        api_keys = cycle(config.get("openai", "api_key").split(","))
        rate_limit = 60.0 / int(config.getint("openai", "rate_limit", fallback="20"))

        base_payload = self._process_payload_config(config)

        super().__init__(
            api_keys=api_keys,
            base_payload=base_payload,
            system_prompt=system_prompt,
            rate_limit=rate_limit,
        )

    def _get_header(self):
        token = next(self.api_keys)
        now = time.time()
        if (
            token in self.last_request
            and now - self.last_request[token] < self.rate_limit
        ):
            sleep_time = self.rate_limit - (now - self.last_request[token])
            time.sleep(sleep_time * 1.2)

        return {"Authorization": f"Bearer {token}"}

    def translate(self, message):
        data = {
            **self.base_payload,
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {"role": "user", "content": message},
            ],
        }
        headers = self._get_header()
        response = requests.post(self.url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        self.last_request[headers["Authorization"].split()[1]] = time.time()

        return result["choices"][0]["message"]["content"].strip()
