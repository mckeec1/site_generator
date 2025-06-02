import unittest

from blocktype import *

class TestBlockType(unittest.TestCase):

    def test_paragraphs(self):
        markdown = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        result = markdown_to_html_node(markdown).to_html()
        expected_result = "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>"
        self.assertEqual(result, expected_result)
    
    def test_code(self):
        markdown_block = "``` this is a code block ```"

        result = block_to_block_type(markdown_block)

        expected_result = BlockType.CODE

        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()
