import sys
import os
import shutil

from pathlib import Path
from textnode import TextNode
from blocktype import markdown_to_html_node
from htmlnode import HTMLNode


def extract_title(markdown):
    
    line_split = markdown.split("\n")
    title = line_split[0]

    if not title.startswith("#"):
        raise Exception("Bad Markdown")

    item = title.lstrip("#").strip()

    return item

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    from_path_open = open(from_path, "r")
    template_path_open = open(template_path, "r")


    markdown = from_path_open.read()
    template = template_path_open.read()

    html = markdown_to_html_node(markdown)

    title = extract_title(markdown)

    template = (
        template.replace("{{ Title }}", title)
        .replace("{{ Content }}", html.to_html())
        .replace('href="/', f'href="{basepath}')
        .replace('src="/', f'src="{basepath}')
    )

    dest_path = Path(dest_path)

    if not dest_path.parent.exists():
          dest_path.parent.mkdir(parents=True, exist_ok=True)

    dest_path.write_text(template)

def copy_directory_recursive(src, dst) -> None:
    if not os.path.exists(dst):
        os.mkdir(dst)

    for f in os.listdir(src):
        new_f = os.path.join(dst, f)
        old_path = os.path.join(src, f)

        if os.path.isdir(old_path):
            copy_directory_recursive(old_path, new_f)
        else:
            print(f"Copying {f} to {new_f}")
            shutil.copy(old_path, new_f)

def generate_pages_recursive(from_path, template_path, dest_path, basepath):

    from_path = Path(from_path)
    template_path = Path(template_path)
    dest_path = Path(dest_path)

    if not dest_path.parent.exists():
        dest_path.parent.mkdir(parents=True, exist_ok=True)

    for f in from_path.iterdir():
        new_f = dest_path / f.name
        if f.is_dir():
            generate_pages_recursive(f, template_path, new_f, basepath)
        else:
            if f.suffix.lower() == ".md":
                generate_page(f, template_path, new_f.with_suffix(".html"), basepath)
            else:
                print(f"Ignoring {f}")

def main():
    if len(sys.argv) == 2:
        basepath = sys.argv[1]
    else:
        basepath = "/"

    project_root = os.path.dirname(__file__)

    dest_path = "public/index.html"
    static_dest_dir = "public"
    static_dir = "static"

    if os.path.exists(dest_path):
        shutil.rmtree(static_dest_dir)

    copy_directory_recursive(static_dir, static_dest_dir)

    from_path = "content"
    template_path = "template.html"

    generate_pages_recursive(from_path, template_path, static_dest_dir, basepath)
#    generate_page(from_path, template_path, dest_path)

main()
