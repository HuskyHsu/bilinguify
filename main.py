from translator import OpenAI

if __name__ == "__main__":
    openai = OpenAI("config.ini")

    input_data = [
        "Chat models take a series of messages as input, and return a model-generated message as output.",
        "Make the translation readable and intelligible.",
        "Be elegant and natural in your translation.",
        "Do not translate any personal names.",
        "Do not add any additional text to the translation.",
    ]

    results = openai.translate(input_data)

    for i, result in enumerate(results):
        print(f"{i + 1}. {result}")
