from reader import epub

if __name__ == "__main__":
    book = epub.EpubReader("config.ini")

    i = 0
    for paragraph in book.read(6):
        print("\n========\n")
        print(paragraph)
        i += 1
        # if i > 100:
        #     break

    print(i)
