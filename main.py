from translator import ChatGPT


if __name__ == "__main__":
    translator = ChatGPT("config.ini")

    text = translator.translate(
        "Chat models take a series of messages as input, and return a model-generated message as output."
    )
    print(text)
