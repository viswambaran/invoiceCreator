from typing import Any

import fitz


def get_pdf_font_name(
    font: dict[str, Any]
) -> str:
    """
    Regular Helvetica currently matches the original value text
    more closely than applying the extracted bold flag.
    """

    return "helv"


def get_colour(
    font: dict[str, Any]
) -> tuple[float, float, float]:

    colour = font["colour"]

    return (
        colour["r"] / 255,
        colour["g"] / 255,
        colour["b"] / 255,
    )


def get_horizontal_bounds(
    metadata: dict[str, Any],
    row_offset_y: float = 0,
) -> tuple[float, float]:
    """
    Return the usable horizontal boundaries for a field.

    Table fields use cell_rect.
    Fixed fields use value_rect.
    """

    bounds = (
        metadata.get("cell_rect")
        or metadata.get("value_rect")
    )

    if bounds is None:
        raise KeyError(
            "PDF metadata must contain either "
            "'cell_rect' or 'value_rect'."
        )

    return (
        float(bounds["x0"]),
        float(bounds["x1"]),
    )


def write_metadata_value(
    page,
    value,
    metadata: dict[str, Any],
    align: str = "left",
    row_offset_y: float = 0,
    padding: float = 0,
    clear_padding_x: float = 1.25,
    clear_padding_top: float = 1.0,
    clear_padding_bottom: float = 0.75,
) -> None:
    """
    Clear only the glyph-sized region occupied by the replacement
    text, then write the replacement.

    Metadata controls placement and cell boundaries. The whiteout
    rectangle is calculated from the actual rendered text width,
    so it does not span the full cell or touch its borders.
    """

    required_keys = {
        "write_position",
        "font",
    }

    missing_keys = (
        required_keys
        - metadata.keys()
    )

    if missing_keys:
        raise KeyError(
            "Incomplete PDF metadata. Missing: "
            + ", ".join(
                sorted(missing_keys)
            )
        )

    text = (
        ""
        if value is None
        else str(value)
    )

    font = metadata["font"]
    font_size = float(font["size"])
    font_name = get_pdf_font_name(font)

    left_bound, right_bound = get_horizontal_bounds(
        metadata,
        row_offset_y=row_offset_y,
    )

    write_position = metadata["write_position"]

    baseline_y = (
        float(write_position["y"])
        + row_offset_y
    )

    text_width = fitz.get_text_length(
        text,
        fontname=font_name,
        fontsize=font_size,
    )

    if align == "right":
        write_x = (
            right_bound
            - padding
            - text_width
        )

    elif align == "center":
        available_width = (
            right_bound
            - left_bound
        )

        write_x = (
            left_bound
            + (
                available_width
                - text_width
            ) / 2
        )

    else:
        write_x = (
            float(write_position["x"])
            + padding
        )

    #
    # Keep the rendered text inside its metadata-defined cell.
    #

    write_x = max(
        write_x,
        left_bound + 0.5,
    )

    maximum_write_x = (
        right_bound
        - text_width
        - 0.5
    )

    write_x = min(
        write_x,
        maximum_write_x,
    )

    #
    # Clear only the glyph band.
    #
    # This avoids painting across table borders or totals-row lines.
    #

    clear_x0 = max(
        left_bound + 0.35,
        write_x - clear_padding_x,
    )

    clear_x1 = min(
        right_bound - 0.35,
        write_x
        + text_width
        + clear_padding_x,
    )

    clear_y0 = (
        baseline_y
        - font_size
        - clear_padding_top
    )

    clear_y1 = (
        baseline_y
        + clear_padding_bottom
    )

    clear_rect = fitz.Rect(
        clear_x0,
        clear_y0,
        clear_x1,
        clear_y1,
    )

    if (
        clear_rect.x1 > clear_rect.x0
        and clear_rect.y1 > clear_rect.y0
    ):
        page.draw_rect(
            clear_rect,
            color=None,
            fill=(1, 1, 1),
            overlay=True,
        )

    page.insert_text(
        (
            write_x,
            baseline_y,
        ),
        text,
        fontname=font_name,
        fontsize=font_size,
        color=get_colour(font),
        overlay=True,
    )