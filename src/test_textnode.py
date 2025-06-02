import unittest

from textnode import TextNode, TextType, TextNodeDelimiter, markdown_to_blocks
from htmlnode import text_node_to_html_node, split_nodes_delimiter

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_different_text(self):
        node = TextNode("First text", TextType.BOLD)
        node2 = TextNode("Second text", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_different_type(self):
        node = TextNode("Same text", TextType.BOLD)
        node2 = TextNode("Same text", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_different_url(self):
        node = TextNode("Link text", TextType.LINK, "https://example.com")
        node2 = TextNode("Link text", TextType.LINK, "https://different.com")
        self.assertNotEqual(node, node2)

    def test_default_url(self):
        node = TextNode("Text", TextType.BOLD)
        self.assertEqual(node.url, None)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_text_bold(self):
        node = TextNode("<b>This is text</b>", TextType.BOLD)
        bold_node = text_node_to_html_node(node)
        self.assertEqual(bold_node.tag, "b")
        self.assertEqual(bold_node.value, "<b>This is text</b>")

    def test_code(self):
        node = TextNode("[code]This is code[/code]", TextType.CODE)
        code_node = text_node_to_html_node(node)
        self.assertEqual(code_node.tag, "code")
        self.assertEqual(code_node.value, "[code]This is code[/code]")

    def test_link(self):
        node = TextNode("Google", TextType.LINK, "https://google.com")
        link_node = text_node_to_html_node(node)
        self.assertEqual(link_node.tag, "a")
        self.assertEqual(link_node.value, "Google")
        self.assertEqual(link_node.props["href"], "https://google.com")

    def test_basic_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "code block")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, " word")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)
    
    def test_delimiter_at_beginning(self):
        node = TextNode("`code` and more text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 3)  # Empty TextNode at beginning, CODE node, TEXT node
        self.assertEqual(new_nodes[0].text, "")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "code")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, " and more text")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)

    def test_delimiter_at_end(self):
        node = TextNode("text and then `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 3)  # TEXT node, CODE node, empty TextNode at end
        self.assertEqual(new_nodes[0].text, "text and then ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "code")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, "")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)

    def test_markdown_to_blocks(self):
        md = """
    This is **bolded** paragraph

    This is another paragraph with _italic_ text and `code` here
    This is the same paragraph on a new line

    - This is a list
    - with items
    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )


if __name__ == "__main__":
    unittest.main()
