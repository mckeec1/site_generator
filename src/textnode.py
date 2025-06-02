from enum import Enum

class TextType(Enum):
    TEXT = "Normal text"
    BOLD = "**Bold text**"
    ITALIC = "_Italic text_"
    CODE = "`Code text`"
    LINK = "[anchor text](url)"
    IMAGE = "![alt text](url)"

class TextNodeDelimiter(Enum):
    BOLD = "**"
    ITALIC = "_"
    CODE = "`"

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if isinstance(other, TextNode):
            return (self.text == other.text and self.text_type == other.text_type and self.url == other.url)
        return False

    def __repr__(self):
        text_type = self.text_type
        return f"TextNode({self.text}, {text_type}, {self.url})"

def markdown_to_blocks(markdown):
    new_blocks = []

    split_markdown = markdown.split("\n\n")
    for item in split_markdown:
        line = item.split("\n")
        stripped_lines = []
        for l in line:
            stripped = l.strip()
            if stripped != "":
                stripped_lines.append(stripped)
            
        result = "\n".join(stripped_lines)
        if result != "":
            new_blocks.append(result)

    return new_blocks
