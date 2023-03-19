import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


class EpubReader:
    def __init__(self, filepath):
        self.book = epub.read_epub(filepath)

    def _get_soup(self, content):
        return BeautifulSoup(content, "html.parser")

    def read(self):
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = self._get_soup(item.get_content())

                ls = soup.body.strings
                for l in ls:
                    l = l.strip()
                    if len(l) == 0:
                        continue
                    print(f"\n{l}")

                yield soup
