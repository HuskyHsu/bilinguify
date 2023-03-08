from translator import ChatGPT


if __name__ == "__main__":
    translator = ChatGPT("config.ini")
    text = translator.translate("Hello, how are you?")

    print(text)
