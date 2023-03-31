import re
from configparser import ConfigParser

from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup


class EpubReader:
    def __init__(self, config_path):
        config = ConfigParser()
        config.read(config_path)

        file_path = config.get("book", "file_path")
        self.book = epub.read_epub(file_path)

    def _get_soup(self, content):
        return BeautifulSoup(content.decode("utf-8"), "html.parser")

    def _html_to_dict(self, element):
        tag = element.name
        text = re.sub(rf"<\/?{tag}[^>]*>|^\s+|\s+$", "", str(element)).strip()

        if not tag or not text:
            return None

        result = {
            "tag": tag,
            "full_text": text,
        }
        if element.has_attr("class") and element["class"]:
            result["class"] = element["class"]

        children = [
            self._html_to_dict(child) for child in element.contents if child != "\n"
        ]
        children = [child for child in children if child is not None]
        if children:
            result["children"] = children

        return result

    def _get_paragraphs_level(self, results, level=0):
        def get_level(result):
            if result["tag"] == "p":
                return level

            if "children" not in result:
                return 0

            return self._get_paragraphs_level(result["children"], level + 1)

        return max(get_level(result) for result in results)

    def get_paragraphs(self, results, level):
        for result in results:
            if level == 0:
                yield result["full_text"]

            if "children" not in result:
                continue

            yield from self.get_paragraphs(result["children"], level - 1)

    def read(self, limit_part=None):
        part = 0
        for item in self.book.get_items():
            if limit_part and part >= limit_part:
                break

            if item.get_type() == ITEM_DOCUMENT:
                soup = self._get_soup(item.get_content())

                results = [
                    children
                    for children in [
                        self._html_to_dict(content) for content in soup.body.contents
                    ]
                    if children is not None
                ]
                if not results:
                    continue

                level = self._get_paragraphs_level(results)

                for paragraph in self.get_paragraphs(results, level):
                    yield paragraph

            part += 1
