import json

from reader import epub


if __name__ == "__main__":
    epub_reader = epub.EpubReader("input_book/animal_farm.epub")
    chapter_contents = epub_reader.read()

    for i in range(3):
        print("\n========\n")
        chapter_content, level = next(chapter_contents)
        print(json.dumps(chapter_content), level)
