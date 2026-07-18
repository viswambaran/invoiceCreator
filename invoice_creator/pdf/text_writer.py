from typing import Any

from typing import Any

import fitz


def get_pdf_font_name(
    font: dict[str, Any]
    font: dict[str, Any]
) -> str:

    return "helv"


def get_colour(
    font: dict[str, Any]
) -> tuple[float, float, float]:

    colour = font[
        "colour"
    ]

    return (
        colour["r"] / 255,
        colour["g"] / 255,
        colour["b"] / 255
    )


def fit_font_size(
    text: str,
    font_name: str,
    preferred_size: float,
    available_width: float,
    minimum_size: float = 6.0
) -> float:
    """
    Reduce the font only when a value cannot fit in its box.
    """

    font_size = preferred_size

    while font_size > minimum_size:

        text_width = fitz.get_text_length(
            text,
            fontname=font_name,
            fontsize=font_size
        )

        if text_width <= available_width:

            return font_size

        font_size = round(
            font_size - 0.25,
            2
        )

    return minimum_size


def write_value(
    page,
    value,
    metadata: dict[str, Any],
    align: str | None = None,
    row_offset_y: float = 0,
    padding: float = 0
) -> None:
    """
    Insert text into a blank template.

    No masking, redaction, or white rectangle is drawn.
    """

    required_keys = {
        "write_position",
        "box",
        "font"
    }

    missing = (
        required_keys
        - metadata.keys()
    )

    if missing:

        raise KeyError(
            "Incomplete PDF metadata. Missing: "
            + ", ".join(
                sorted(missing)
            )
        )


    text = (
        ""
        if value is None
        else str(value)
    )

    font = metadata[
        "font"
    ]

    font_name = get_pdf_font_name(
        font
    )

    box = metadata[
        "box"
    ]

    left_x = float(
        box["x0"]
    )

    right_x = float(
        box["x1"]
    )

    available_width = max(
        right_x
        - left_x
        - (padding * 2),
        1
    )

    preferred_size = float(
        font["size"]
    )

    font_size = fit_font_size(
        text=text,
        font_name=font_name,
        preferred_size=preferred_size,
        available_width=available_width
    )

    text_width = fitz.get_text_length(
        text,
        fontname=font_name,
        fontsize=font_size
    )

    resolved_alignment = (
        align
        or metadata.get(
            "align",
            "left"
        )
    )

    if resolved_alignment == "right":

        write_x = (
            right_x
            - padding
            - text_width
        )

    elif resolved_alignment == "center":

        write_x = (
            left_x
            + (
                available_width
                - text_width
            ) / 2
            + padding
        )

    else:

        write_x = (
            float(
                metadata
                ["write_position"]
                ["x"]
            )
            + padding
        )


    baseline_y = (
        float(
            metadata
            ["write_position"]
            ["y"]
        )
        + row_offset_y
    )


    page.insert_text(
        (
            write_x,
            baseline_y
        ),
        text,
        fontname=font_name,
        fontsize=font_size,
        color=get_colour(
            font
        ),
        overlay=True
    )