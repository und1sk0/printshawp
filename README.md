# printshawp

Imposes a PDF as a single-signature saddle-stitch booklet, ready for duplex printing.

## What it does

Takes any PDF and rearranges its pages into booklet printing order: two source pages
side by side per sheet, outermost sheet first, with the correct 180° rotation on
back-facing sides for long-edge duplex binding. Optionally overlays page numbers.

## Requirements

- Python 3.10+
- [pikepdf](https://pikepdf.readthedocs.io/)

```
pip install -r requirements.txt
```

## Usage

```
python printshawp.py input.pdf [output.pdf]
python printshawp.py --page-numbers input.pdf output.pdf
```

If no output path is given, the output is written to `<input>-booklet.pdf`.

### Options

| Flag | Description |
|------|-------------|
| `--page-numbers` | Overlay page numbers on each non-blank page — lower-left for left-side pages, lower-right for right-side pages |

## Printing

1. Print the output PDF duplex with **long-edge binding** selected
2. Stack the printed sheets in order (sheet 1 — the one with the cover — on top)
3. Fold the stack together along the center spine
4. Saddle-stitch or staple through the spine

## How it works

For N source pages (padded to the nearest multiple of 4), each physical sheet
carries four page slots. The outermost sheet gets pages 1 and N on its front,
pages 2 and N−1 on its back; the next sheet gets 3/N−2 and 4/N−3; and so on
toward the centerfold.

Back-of-sheet pages are rotated 180° in the output PDF. A standard duplex
printer's long-edge flip inverts them again, so the content prints right-side up
on the physical paper. After folding, every page reads correctly.
