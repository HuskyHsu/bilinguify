import json

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def html_to_dict(element):
    if element.name is None:
        return None

    if element.text.strip() == "":
        return None

    result = {
        "tag": element.name,
        "full_text": element.text.strip(),
    }
    if element.has_attr("class") and element["class"]:
        result["class"] = element["class"]

    if element.contents != None and len(element.contents) > 0:
        result["children"] = [
            html_to_dict(child) for child in element.contents if child != "\n"
        ]
        result["children"] = [
            child for child in result["children"] if child is not None
        ]
        if len(result["children"]) == 0:
            del result["children"]

    return result


class EpubReader:
    def __init__(self, filepath):
        self.book = epub.read_epub(filepath)

    def _get_soup(self, content):
        return BeautifulSoup(content.decode("utf-8"), "html.parser")

    def read(self):
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = self._get_soup(item.get_content())

                print(soup.body)

                result = html_to_dict(soup.body)

                print(json.dumps(result))

                yield soup
