import re

from enum import Enum
from htmlnode import HTMLNode, ParentNode, LeafNode, text_node_to_html_node, text_to_textnodes
from textnode import markdown_to_blocks

class BlockType (Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    IMAGE = "image"

def markdown_to_html_node(markdown):
    children = []
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block.strip() == "":
            continue
        block_type = block_to_block_type(block)
        node = block_to_html_node(block, block_type)
        children.append(node)

    return ParentNode(tag="div", children=children)

def block_to_block_type(block):

    if re.match(r'^#{1,6} ', block):
        return BlockType.HEADING

    # Code block pattern: starts with ``` and ends with ```
    if re.match(r'^```.*```$', block, re.DOTALL):
        return BlockType.CODE
    
    # For quote blocks, we need to check if EVERY line starts with >
    lines = block.split('\n')
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE
    
    # For unordered lists, check if EVERY line starts with -
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST
    
    # For ordered lists, more complex: check if lines start with incrementing numbers
    if is_ordered_list(lines):  # You'd need to implement this helper function
        return BlockType.ORDERED_LIST

    line = lines[0].strip()  # only for a single-line block
    if len(lines) == 1 and re.match(r"^!\[.*\]\(.*\)$", line):
        # It's an image block!
        return BlockType.IMAGE
    
    # Default case
    return BlockType.PARAGRAPH

def block_to_html_node(text: str, type: BlockType) -> HTMLNode:
    if type == BlockType.QUOTE:
        return _quote_block_to_html_node(text)
    elif type == BlockType.UNORDERED_LIST:
        return _ul_block_to_html_node(text)
    elif type == BlockType.ORDERED_LIST:
        return _ol_block_to_html_node(text)
    elif type == BlockType.CODE:
        return _code_block_to_html_node(text)
    elif type == BlockType.HEADING:
        return _heading_block_to_html_node(text)
    elif type == BlockType.PARAGRAPH:
        return _paragraph_block_to_html_node(text)
    elif type == BlockType.IMAGE:
        return _image_block_to_html_node(text)
    else:
        raise Exception(f"Unknown BlockType {type}") 

def is_ordered_list(lines):
    for i, line in enumerate(lines, 1):
                if not re.match(f'^{i}\\. ', line):
                    return False
    return True

def text_to_html_node(text: str) -> list[LeafNode]:
    # take text and make it into leaf nodes (children of parent)
    # text nodes are our intermediate representation
    text_nodes = text_to_textnodes(text)

    # this is the actual html represetnation
    children = [text_node_to_html_node(node) for node in text_nodes]

    return children


def _paragraph_block_to_html_node(markdown: str) -> HTMLNode:
    print(f"_paragraph_block_to_html_node received: '{markdown}'")
    # markdown text ready to be made into html text
    text = ""
    for line in markdown.split("\n"):
        text = " ".join(markdown.split("\n"))

    # text needs to be parsed into html nodes (aka leaf nodes)
    children = text_to_html_node(text.strip())
    return ParentNode(tag="p", children=children)


def _check_if_heading(text: str) -> bool:
    # first char should be a #, then after all # should be a space
    if text.startswith("#") and text.strip("#")[0] == " ":
        parts = text.split()
        heading_num = len(parts[0])
        return 1 <= heading_num < 7

    return False


def _heading_block_to_html_node(markdown: str) -> HTMLNode:
    # markdown text ready to be made into html text
    heading_parts = markdown.split()
    heading, heading_text = heading_parts[0], " ".join(heading_parts[1:])
    heading_num = len(heading)
    # text needs to be parsed into html nodes (aka leaf nodes)
    children = text_to_html_node(heading_text)
    return ParentNode(tag=f"h{heading_num}", children=children)


def _check_if_code_block(text: str) -> bool:
    # first and last line should start with 3 back ticks
    return text[:3] == "```" and text[-3:] == "```"


def _code_block_to_html_node(markdown: str) -> HTMLNode:
    # markdown text ready to be made into html text
    list_elements = []
    text = markdown.strip("```")
    children = text_to_html_node(text)
    list_elements.append(ParentNode("code", children))

    return ParentNode(tag="pre", children=list_elements)


def _check_if_quote_block(text: str) -> bool:
    parts = text.split("\n")
    for part in parts:
        if part[0] != ">":
            return False
    return True


def _quote_block_to_html_node(markdown: str) -> HTMLNode:
    # markdown text ready to be made into html text
    text = ""
    for line in markdown.split("\n"):
        text += line.strip().strip(">")

    # text needs to be parsed into html nodes (aka leaf nodes)
    children = text_to_html_node(text.strip())
    return ParentNode(tag="blockquote", children=children)


def _check_if_unordered_list_block(text: str) -> bool:
    parts = text.split("\n")
    for part in parts:
        if part[0] not in ["*", "-"] or part[1] != " ":
            return False
    return True


def _ul_block_to_html_node(markdown: str) -> HTMLNode:
    # markdown text ready to be made into html text
    list_elements = []
    for line in markdown.split("\n"):
        # we know it's a ul, so assume it's the correct format
        children = text_to_html_node(line[2:])
        list_elements.append(ParentNode("li", children))

    return ParentNode(tag="ul", children=list_elements)


def _check_if_ordered_list_block(text: str) -> bool:
    parts = text.split("\n")
    for i, part in enumerate(parts, 1):
        if not part[0].isnumeric() or part[1] != "." or part[0] != str(i):
            return False
    return True


def _ol_block_to_html_node(markdown: str) -> HTMLNode:
    # markdown text ready to be made into html text
    list_elements = []
    for line in markdown.split("\n"):
        # we know it's a ol, so assume it's the correct format
        children = text_to_html_node(line[3:])
        list_elements.append(ParentNode("li", children))

    return ParentNode(tag="ol", children=list_elements)

def _image_block_to_html_node(markdown: str) -> HTMLNode:
    match = re.match(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", markdown)
    if match:
        alt = match.group(1)
        src = match.group(2)
    # Then create your LeafNode here
    else:
        raise Exception("Invalid markdown image syntax")

    return LeafNode(tag="img", value=None, attributes={"src": src, "alt": alt})
