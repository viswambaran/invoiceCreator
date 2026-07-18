import fitz


def get_pdf_font_name(
    font: dict
) -> str:
    """
    Regular Helvetica matches the original template values
    more closely than the extracted bold style.
    """

    return "helv"


def write_in_area(
    page,
    value,
    value_rect,
    write_position,
    font,
    align="left",
    row_offset_y=0,
    padding=0,
    horizontal_inset=1.25,
    vertical_inset=2.0
) -> None:

    text = (
        ""
        if value is None
        else str(value)
    )

    fontsize = float(
        font["size"]
    )

    fontname = get_pdf_font_name(
        font
    )

    colour = (
        font["colour"]["r"] / 255,
        font["colour"]["g"] / 255,
        font["colour"]["b"] / 255
    )

    rect = fitz.Rect(
        value_rect["x0"],
        value_rect["y0"] + row_offset_y,
        value_rect["x1"],
        value_rect["y1"] + row_offset_y
    )

    whiteout_rect = fitz.Rect(
        rect.x0 + horizontal_inset,
        rect.y0 + vertical_inset,
        rect.x1 - horizontal_inset,
        rect.y1 - vertical_inset
    )

    if (
        whiteout_rect.x1 > whiteout_rect.x0
        and whiteout_rect.y1 > whiteout_rect.y0
    ):
        page.draw_rect(
            whiteout_rect,
            color=None,
            fill=(1, 1, 1),
            overlay=True
        )

    text_width = fitz.get_text_length(
        text,
        fontname=fontname,
        fontsize=fontsize
    )

    if align == "right":
        x = (
            rect.x1
            - padding
            - text_width
        )

    elif align == "center":
        x = (
            rect.x0
            + (
                rect.width
                - text_width
            ) / 2
        )

    else:
        x = (
            write_position["x"]
            + padding
        )

    y = (
        write_position["y"]
        + row_offset_y
    )

    page.insert_text(
        (x, y),
        text,
        fontname=fontname,
        fontsize=fontsize,
        color=colour,
        overlay=True
    )