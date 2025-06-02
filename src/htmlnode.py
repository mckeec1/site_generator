import re
from textnode import TextNode, TextType, markdown_to_blocks, TextNodeDelimiter

class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("Must implement this method")

    def props_to_html(self):
        if not self.props:
            return ""

        attr_string = ' ' + ' '.join(f'{key}="{value}"' for key, value in self.props.items())
        return attr_string

    def __repr__(self):
        return f"{self.tag} {self.value} {self.children} {self.props}"

class LeafNode(HTMLNode):
    def __init__(self, tag, value, attributes=None):
        super().__init__()
        self.value = value
        self.tag = tag
        self.attributes = attributes
        self.props = attributes

    def to_html(self):
        if self.value == "":
            raise ValueError("All leaf nodes must have a value.")

        if self.tag is None:
            return self.value

        attr_str = ""
        if self.attributes:
            attr_pairs = []
            for key, value in self.attributes.items():
                attr_pairs.append(f'{key}="{value}"')
            if attr_pairs:
                attr_str = " " + " ".join(attr_pairs)

        new_tag = f"<{self.tag}{attr_str}>{self.value}</{self.tag}>"
        return new_tag

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__()
        self.tag = tag
        self.children = children
        self.props = props

    def to_html(self):
        if not self.tag:
            raise ValueError("Tag is missing")

        if self.children is None:
            raise ValueError("Children value is missing")

        new_tag = ""
        html_list = []
        for child in self.children:
            html_list.append(child.to_html())

        new_tag = ''.join(html_list)

        return f"<{self.tag}>{new_tag}</{self.tag}>"

def text_node_to_html_node(text_node):

    html_dict = {
        TextType.TEXT: lambda node: LeafNode(None, text_node.text),
        TextType.BOLD: lambda node: LeafNode("b", text_node.text),
        TextType.ITALIC: lambda node: LeafNode("i", text_node.text),
        TextType.CODE: lambda node: LeafNode("code", text_node.text),
        TextType.LINK: lambda node: LeafNode("a", text_node.text, {"href": text_node.url}),
        TextType.IMAGE: lambda node: LeafNode("img", "", {"src": text_node.url, "alt": text_node.text}),
        }

    if text_node.text_type not in html_dict:
        raise ValueError(f"Unsupported TextType: {text_node.text_type}") 

    new_node = html_dict[text_node.text_type](text_node)
    return new_node


def extract_markdown_images(text):
    image = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return image

def extract_markdown_links(text):
    link = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return link

def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: TextNodeDelimiter, text_type: TextType
) -> list[TextNode]:
    new_nodes = []

    for node in old_nodes:
        if not node.text_type == TextType.TEXT:
            # don't parse non-text any further
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)

        # this is an even split aka missing an ending
        if len(parts) % 2 == 0:
            raise Exception("Invalid Markdown Syntax")

        for index, part in enumerate(parts):
            # this is empty, nothing to add
            #if part == "":
             #   continue
            if index % 2 == 0:
                # when we split, the even numbers are just texts
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes


def split_nodes_image(old_nodes):
     new_nodes = []

     for node in old_nodes:
         if node.text_type != TextType.TEXT:
             new_nodes.append(node)
             continue
        
         image = extract_markdown_images(node.text)

         if not image:
             new_nodes.append(node)
             continue

         current_text = node.text
         for alt_text, url in image:
             img_markdown = f"![{alt_text}]({url})"
             sections = current_text.split(img_markdown, 1)

             if sections[0]:
                 new_nodes.append(TextNode(sections[0], TextType.TEXT))

             new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))

             if len(sections) > 1:
                 current_text = sections[1]
             else:
                 current_text = ""

         if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))

     return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
         if node.text_type != TextType.TEXT:
             new_nodes.append(node)
             continue
        
         current_text = node.text

         while True:
            match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", current_text)
            if not match:
                if current_text:  # only add if non-empty
                    new_nodes.append(TextNode(current_text, TextType.TEXT))
                break

            before_text = current_text[:match.start()]
            after_text = current_text[match.end():]
            alt_text = match.group(1)
            url = match.group(2)

            if before_text:
                new_nodes.append(TextNode(before_text, TextType.TEXT))
            new_nodes.append(TextNode(alt_text, TextType.LINK, url))

            current_text = after_text

    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes



