import asyncio
import aiohttp
import random


async def call_api(api_key, data):
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(
            "https://randomuser.me/api/",
            params={"api_key": api_key},
        ) as resp:
            result = await resp.json()
            sleep_time = random.randint(1, 3)
            print(
                f"api_key: {api_key}, data: {data}, result: {result['info']['seed']}, sleep_time: {sleep_time}"
            )

            await asyncio.sleep(sleep_time)
            return result["info"]["seed"]


async def fetch_data(api_key_queue, data_queue, result_queue):
    while True:
        api_key = await api_key_queue.get()
        data = await data_queue.get()
        data_index = data["index"]
        data_value = data["data"]
        try:
            result = await call_api(api_key, data_value)
            await result_queue.put({"index": data_index, "result": result})

            print(f"release api_key: {api_key}")
            await api_key_queue.put(api_key)
        except Exception as e:
            print(e)
        finally:
            data_queue.task_done()


async def main(input_data):
    API_KEYS = ["key1", "key2", "key3"]  # 假設有3組 api key

    api_key_queue = asyncio.Queue()
    data_queue = asyncio.Queue()
    result_queue = asyncio.Queue()

    for api_key in API_KEYS:
        await api_key_queue.put(api_key)

    # 將 input data 放進 queue
    for i, data in enumerate(input_data):
        await data_queue.put({"index": i, "data": data})

    tasks = []
    for _ in range(3):
        tasks.append(
            asyncio.ensure_future(fetch_data(api_key_queue, data_queue, result_queue))
        )

    # 等待所有 input data 都處理完畢
    await data_queue.join()

    # 取消所有 task
    for task in tasks:
        task.cancel()

    size = result_queue.qsize()
    results = []
    for i in range(size):
        result = await result_queue.get()
        results.append(result)

    return sorted(results, key=lambda x: x["index"])


if __name__ == "__main__":
    INPUT_DATA = [f"data{i}" for i in range(10)]  # 假設有多筆 input data

    results = asyncio.run(main(INPUT_DATA))
    print(results)
