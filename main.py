from translator import ChatGPT


if __name__ == "__main__":
    api_caller = ChatGPT("config.ini")
    # print(api_caller)
    text = api_caller.call_api("Hello, how are you?")

    print(text)
