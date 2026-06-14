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
python printshawp.py -p input.pdf
python printshawp.py -p -s 3 input.pdf output.pdf
```

If no output path is given, the output is written to `<input>-booklet.pdf`.

### Options

| Flag | Description |
|------|-------------|
| `-p`, `--page-numbers` | Overlay page numbers on each non-blank page — lower-left for left-side pages, lower-right for right-side pages |
| `-s N`, `--start-page N` | Label source page N as "1"; pages before N receive no number (overrides auto-detection) |
| `-n`, `--no-cover` | Number all pages from 1, including the first page (for inserts with no cover) |

By default, `--page-numbers` auto-detects the first page with text content and starts numbering
there — cover photos and blank inside-cover pages are skipped automatically. The detected start
page is printed so you can catch misdetection and override with `-s`.

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
