#!/usr/bin/env python3

import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

THEME_QRC = "resources_theme.qrc"
TARGET_QRC = "src/main/resources/base/resources_dist.qrc"
OUTPUT_QRC = "src/main/resources/base/resources.qrc"


def parse_qrc(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return root.findall("qresource")


def collect_files(qresources):
    merged = defaultdict(set)
    for qres in qresources:
        prefix = qres.attrib.get("prefix", "")
        for f in qres.findall("file"):
            merged[prefix].add(f.text)
    return merged


def write_merged_qrc(merged, output_path):
    new_root = ET.Element("RCC")
    for prefix, files in merged.items():
        qres = ET.SubElement(new_root, "qresource", {"prefix": prefix})
        for fname in sorted(files):
            ET.SubElement(qres, "file").text = fname
    tree = ET.ElementTree(new_root)
    tree.write(output_path, encoding="unicode", xml_declaration=False)
    print(f"✅ Merged QRC written to: {output_path}")


def fix_image_urls_in_qss(qss_path):
    with open(qss_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Fix URLs like: url(theme_icons  active/downarrow.svg)
    content = re.sub(
        r"url\(theme_icons\s+([^\)]+)\)", r"url(:/theme_icons/theme_icons/\1)", content
    )
    with open(qss_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"🔧 Fixed image URLs in QSS: {qss_path}")


if __name__ == "__main__":
    try:
        theme_qresources = parse_qrc(THEME_QRC)
        target_qresources = parse_qrc(TARGET_QRC)
        all_qresources = theme_qresources + target_qresources
        merged = collect_files(all_qresources)
        write_merged_qrc(merged, OUTPUT_QRC)
        fix_image_urls_in_qss("src/main/resources/base/theme.qss")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
