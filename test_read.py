from reader import epub


if __name__ == "__main__":
    epub_reader = epub.EpubReader("input_book/Alice's Adventures in Wonderland.epub")

    i = 0
    for paragraph in epub_reader.read():
        print("\n========\n")
        print(paragraph)
        i += 1
        # if i > 100:
        #     break

    print(i)
