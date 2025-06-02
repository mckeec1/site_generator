import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, split_nodes_delimiter
from textnode import TextNode, TextType

class TestHTMLNode(unittest.TestCase):
    def single_prop_test(self):
        node = HTMLNode(tag="div", props={"class":"header"})
        expected = ' class="header"'
        result = node.props_to_html()

        self.assertEqual(result, expected, f"Expected '{expected}', but got '{result}'")

    def test_html_node_multiple_properties(self):
        node = HTMLNode(tag="div", props={
            "id": "main",
            "class": "container",
            "style": "color: red"
        })
        expected = ' id="main" class="container" style="color: red"'
        result = node.props_to_html()

        self.assertEqual(result, expected, f"Expected '{expected}', but got '{result}'")

    def test_html_node_empty(self):
        node = HTMLNode()  # No arguments
        expected_props = ""  # Empty string because there are no attributes
        result = node.props_to_html()

        # Props check
        self.assertEqual(result, expected_props, f"Expected '{expected_props}', but got '{result}'")

        # General attributes check
        self.assertIsNone(node.tag, "Expected 'tag' to be None")
        self.assertIsNone(node.value, "Expected 'value' to be None")
        self.assertIsNone(node.children, "Expected 'children' to be None")
        self.assertIsNone(node.props, "Expected 'props' to be None")

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_b(self):
        node = LeafNode("b", "Hello, world!")
        self.assertEqual(node.to_html(), "<b>Hello, world!</b>")

    def test_leaf_to_html_h2(self):
        node = LeafNode("h2", "Hello, world!")
        self.assertEqual(node.to_html(), "<h2>Hello, world!</h2>")

    def test_leaf_to_html_link(self):
        node = LeafNode("a", "Im a link!", {"href": "https://google.com"})
        self.assertEqual(node.to_html(), '<a href="https://google.com">Im a link!</a>')


    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_parent_node_no_children_valid_tag(self):
        parent_node = ParentNode("p", "")
        self.assertEqual(parent_node.to_html(),"<p></p>")

    def test_parent_node_nest(self):
        other_parent = ParentNode("span", [LeafNode(None,"parent")])
        parent_node = ParentNode("span", [other_parent])

        self.assertEqual(parent_node.to_html(),"<span><span>parent</span></span>")

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with an [link](https://google.com) and another [second link](https://boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://google.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second link", TextType.LINK, "https://boot.dev"
                ),
            ],
            new_nodes,
        )


    def test_text_to_textnodes(self):
        nodes = text_to_textnodes(
            "This is **text** with an _italic_ word and a `code block` and an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://boot.dev)"
        )
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        ) 


if __name__ == "__main__":
    unittest.main()
