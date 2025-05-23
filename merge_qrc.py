import sys
from pathlib import Path
from xml.etree import ElementTree as ET


def merge_qrc_files(output_file: Path, *input_files: Path):
    ET.register_namespace("", "http://www.qt-project.org/namespace")  # Optional, clean output
    root = ET.Element("RCC")

    for input_file in input_files:
        tree = ET.parse(input_file)
        rcc = tree.getroot()

        for qresource in rcc.findall("qresource"):
            root.append(qresource)

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python merge_qrc.py output.qrc input1.qrc input2.qrc input3.qrc")
        sys.exit(1)

    output = Path(sys.argv[1])
    inputs = [Path(arg) for arg in sys.argv[2:]]

    merge_qrc_files(output, *inputs)
    print(f"✅ Merged QRC written to: {output}")
