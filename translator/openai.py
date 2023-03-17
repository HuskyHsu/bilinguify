from collections import namedtuple
from configparser import ConfigParser
import asyncio
import time
import math

import aiohttp


class OpenAi:
    url: str = "https://api.openai.com/v1"

    def __init__(self, config_path: str):
        config = ConfigParser()
        config.read(config_path)

        api_keys = config.get("openai", "api_key").split(",")
        api_key_queue = asyncio.Queue()

        for key in api_keys:
            api_key_queue.put_nowait(key)

        self.language = config.get(
            "translation", "language", fallback="Traditional Chinese"
        )

        self.api_key_queue = api_key_queue
        self.data_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()

        self.config = config

    def _get_header(self, api_key):
        return {"Authorization": f"Bearer {api_key}"}

    def _get_chat_completions_config(self, config):
        payload_items = dict(config.items("openai.payload"))
        number_items = (
            dict(config.items("openai.payload.number"))
            if "openai.payload.number" in config
            else {}
        )
        number_items_converted = {k: float(v) for k, v in number_items.items()}

        return {**payload_items, **number_items_converted}

    async def _call_chat_completions_api(self, api_key, message):
        api_path = "/chat/completions"
        system_prompt = f"""
            I want you to act as a professional English translator.
            Please translate the following sentence into {self.language} while keeping its original meaning in English as much as possible.
            Make the translation readable and intelligible.
            Be elegant and natural in your translation.
            Do not translate any personal names.
            Do not add any additional text to the translation.
            Please only return the translated content and do not include the original text.
        """.replace(
            "  ", ""
        ).strip()
        base_config = self._get_chat_completions_config(self.config)

        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.post(
                f"{self.url}{api_path}",
                headers=self._get_header(api_key),
                json={
                    **base_config,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {"role": "user", "content": message},
                    ],
                },
            ) as resp:
                result = await resp.json()
                if "error" in result:
                    return -1, result["error"]["message"]
                return (
                    result["created"],
                    result["choices"][0]["message"]["content"].strip(),
                )

    async def _fetch_data(self):
        Result = namedtuple("Result", "id, result")
        while True:
            api_key = await self.api_key_queue.get()
            data = await self.data_queue.get()

            try:
                created, result = await self._call_chat_completions_api(
                    api_key, data.message
                )
                await self.result_queue.put(Result(data.id, result))

                now = time.time()
                if now < created + 3:
                    sleep_time = math.ceil(created + 3 - now)
                    await asyncio.sleep(sleep_time)

                await self.api_key_queue.put(api_key)

                print(f"{data.message}\n>>> {result}\n")
            except Exception as e:
                print("error", e)
            finally:
                self.data_queue.task_done()

    async def a_translate(self, messages):
        Message = namedtuple("Message", "id, message")
        for i, data in enumerate(messages):
            await self.data_queue.put(Message(i, data))

        tasks = []
        qsize = self.api_key_queue.qsize()
        for _ in range(qsize):
            tasks.append(asyncio.ensure_future(self._fetch_data()))

        await self.data_queue.join()

        for task in tasks:
            task.cancel()

        size = self.result_queue.qsize()
        results = []
        for i in range(size):
            result = await self.result_queue.get()
            results.append(result)

        print("\n ===translate over===")
        return [result.result for result in sorted(results, key=lambda x: x.id)]

    def translate(self, messages):
        return asyncio.run(self.a_translate(messages))
