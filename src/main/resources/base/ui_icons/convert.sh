#!/bin/bash
mkdir -p svg_tmp

for svg in svg/*.svg; do
    name=$(basename "${svg%.svg}")
    tmp="svg_tmp/$name.svg"

    # Farbe auf #7f7f7f setzen (alte fill-Werte entfernen, neue einsetzen)
    sed -E 's/fill:[^;"]+;//g' "$svg" | sed -E 's/<path /<path fill="#7f7f7f" /' > "$tmp"

    # Als PNG exportieren (nach ./)
    inkscape "$tmp" \
      --export-type=png \
      --export-height=64 \
      --export-background-opacity=0 \
      --export-filename="./$name.png"
done

# temporäre SVGs löschen
rm -r svg_tmp