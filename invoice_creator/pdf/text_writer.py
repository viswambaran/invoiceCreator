from typing import Any

import fitz


def get_pdf_font_name(
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
        colour["b"] / 255,
    )


def fit_font_size(
    text: str,
    font_name: str,
    preferred_size: float,
    available_width: float,
    minimum_size: float = 6.0
) -> float:

    font_size = preferred_size

    while font_size > minimum_size:

        width = fitz.get_text_length(
            text,
            fontname=font_name,
            fontsize=font_size
        )

        if width <= available_width:
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
    padding: float = 6.0
) -> None:

    text = (
        ""
        if value is None
        else str(value)
    )

    required = {
        "cell",
        "write_position",
        "font",
    }

    missing = (
        required
        - metadata.keys()
    )

    if missing:

        raise KeyError(
            "Incomplete PDF metadata. Missing: "
            + ", ".join(
                sorted(missing)
            )
        )

    cell = metadata[
        "cell"
    ]

    left_x = float(
        cell["x0"]
    )

    right_x = float(
        cell["x1"]
    )

    available_width = max(
        right_x
        - left_x
        - (
            padding * 2
        ),
        1
    )

    font = metadata[
        "font"
    ]

    font_name = get_pdf_font_name(
        font
    )

    font_size = fit_font_size(
        text=text,
        font_name=font_name,
        preferred_size=float(
            font["size"]
        ),
        available_width=available_width
    )

    text_width = fitz.get_text_length(
        text,
        fontname=font_name,
        fontsize=font_size
    )

    alignment = (
        align
        or metadata.get(
            "align",
            "left"
        )
    )

    if alignment == "right":

        write_x = (
            right_x
            - padding
            - text_width
        )

    elif alignment == "center":

        write_x = (
            left_x
            + (
                right_x
                - left_x
                - text_width
            )
            / 2
        )

    else:

        write_x = max(
            float(
                metadata
                ["write_position"]
                ["x"]
            ),
            left_x + padding
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