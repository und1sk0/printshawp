#!/usr/bin/env python3
"""
printshawp - impose a PDF as a single-signature duplex booklet

Usage:
    python printshawp.py [--page-numbers] input.pdf [output.pdf]

The output is designed to be printed duplex with long-edge binding,
then sheets stacked and folded together to form a saddle-stitch booklet.
"""

import argparse
import sys
from pathlib import Path

import pikepdf
from pikepdf import Array, Dictionary, Name, Page, Pdf


def pad_to_4(n: int) -> int:
    return ((n + 3) // 4) * 4


def imposition_order(n_pages: int) -> list[tuple[int, int, int, int]]:
    """
    For each sheet (outermost first), return (front_left, front_right, back_left, back_right)
    as 1-indexed page numbers. 0 means a blank slot.
    """
    assert n_pages % 4 == 0
    sheets = []
    for k in range(1, n_pages // 4 + 1):
        fl = n_pages - 2 * (k - 1)
        fr = 2 * k - 1
        bl = 2 * k
        br = n_pages - 2 * k + 1
        sheets.append((fl, fr, bl, br))
    return sheets


def get_page_size(page: Page) -> tuple[float, float]:
    mb = page.mediabox
    return float(mb[2]) - float(mb[0]), float(mb[3]) - float(mb[1])


_MARGIN = 18.0    # points from page edge (~0.25")
_FONT_SIZE = 9
_DIGIT_W = 4.5   # approximate Helvetica digit width at 9pt


def make_imposed_page(
    out: Pdf,
    src: Pdf,
    left_num: int,
    right_num: int,
    n_src: int,
    page_w: float,
    page_h: float,
    rotate_back: bool = False,
    page_numbers: bool = False,
) -> None:
    xobjects = Dictionary()
    content_parts = []

    for xname, page_num, tx in (("PgL", left_num, 0.0), ("PgR", right_num, page_w)):
        if page_num < 1 or page_num > n_src:
            continue
        xobj = out.copy_foreign(src.pages[page_num - 1].as_form_xobject())
        xobjects[f"/{xname}"] = xobj
        if tx == 0:
            content_parts.append(f"q /{xname} Do Q")
        else:
            content_parts.append(f"q 1 0 0 1 {tx:.4f} 0 cm /{xname} Do Q")

    if page_numbers:
        # Left slot: number at lower-left of the left half
        if 1 <= left_num <= n_src:
            content_parts.append(
                f"BT /PgNumFont {_FONT_SIZE} Tf "
                f"{_MARGIN:.1f} {_MARGIN:.1f} Td ({left_num}) Tj ET"
            )
        # Right slot: number at lower-right of the right half
        if 1 <= right_num <= n_src:
            x = page_w * 2 - _MARGIN - len(str(right_num)) * _DIGIT_W
            content_parts.append(
                f"BT /PgNumFont {_FONT_SIZE} Tf "
                f"{x:.1f} {_MARGIN:.1f} Td ({right_num}) Tj ET"
            )

    content = "\n".join(content_parts).encode()

    helvetica = Dictionary(
        Type=Name.Font,
        Subtype=Name("/Type1"),
        BaseFont=Name("/Helvetica"),
    )
    resources = Dictionary(
        XObject=xobjects,
        Font=Dictionary(PgNumFont=helvetica) if page_numbers else Dictionary(),
    )

    page_dict = Dictionary(
        Type=Name.Page,
        MediaBox=Array([0, 0, page_w * 2, page_h]),
        Resources=resources,
        Contents=out.make_stream(content),
    )

    page = Page(out.make_indirect(page_dict))
    if rotate_back:
        page.rotate(180, relative=True)
    out.pages.append(page)


def create_booklet(input_path: Path, output_path: Path, page_numbers: bool = False) -> None:
    with Pdf.open(input_path) as src:
        n_src = len(src.pages)
        n_padded = pad_to_4(n_src)
        n_sheets = n_padded // 4

        pw, ph = get_page_size(Page(src.pages[0]))

        out = Pdf.new()
        for fl, fr, bl, br in imposition_order(n_padded):
            make_imposed_page(out, src, fl, fr, n_src, pw, ph, rotate_back=False, page_numbers=page_numbers)
            make_imposed_page(out, src, bl, br, n_src, pw, ph, rotate_back=True, page_numbers=page_numbers)

        out.save(output_path)

    print(f"Input:  {input_path} ({n_src} pages)")
    print(f"Output: {output_path}")
    print(f"        {n_sheets} sheets, {n_padded} slots ({n_padded - n_src} blank padding)")
    print(f"Print:  duplex, long-edge binding — then stack and fold")


def main():
    p = argparse.ArgumentParser(
        description="Impose a PDF as a single-signature saddle-stitch booklet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Print the output duplex with long-edge binding.\n"
            "Stack sheets in order, fold together, and staple the spine."
        ),
    )
    p.add_argument("input", help="Source PDF")
    p.add_argument("output", nargs="?", help="Output PDF (default: <input>-booklet.pdf)")
    p.add_argument(
        "--page-numbers",
        action="store_true",
        help="Overlay page numbers on each non-blank page",
    )
    args = p.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_name(input_path.stem + "-booklet.pdf")

    create_booklet(input_path, output_path, page_numbers=args.page_numbers)


if __name__ == "__main__":
    main()
