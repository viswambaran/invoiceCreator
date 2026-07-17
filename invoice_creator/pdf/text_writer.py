# # import fitz


# # # def add_redaction(
# # #     page,
# # #     clear_area
# # # ):

# # #     if not clear_area:
# # #         return


# # #     rect = fitz.Rect(

# # #         clear_area["x0"],

# # #         clear_area["y0"],

# # #         clear_area["x1"],

# # #         clear_area["y1"]

# # #     )


# # #     page.add_redact_annot(
# # #         rect
# # #     )



# # # def apply_redactions(page):

# # #     page.apply_redactions()



# # # def write_text(
# # #     page,
# # #     value,
# # #     position,
# # #     font,
# # #     align=None
# # # ):

# # #     page.insert_text(

# # #         (
# # #             position["x"],
# # #             position["y"]
# # #         ),

# # #         str(value),

# # #         fontname="helv",

# # #         fontsize=font["size"],

# # #         color=(

# # #             font["colour"]["r"] / 255,

# # #             font["colour"]["g"] / 255,

# # #             font["colour"]["b"] / 255

# # #         )

# # #     )



# # # def write_text(
# # #     page,
# # #     value,
# # #     position,
# # #     font,
# # #     align=None
# # # ):

# # #     text = str(value)

# # #     fontsize = font["size"]

# # #     colour = (

# # #         font["colour"]["r"] / 255,

# # #         font["colour"]["g"] / 255,

# # #         font["colour"]["b"] / 255

# # #     )


# # #     #
# # #     # Estimate text width
# # #     #

# # #     text_width = fitz.get_text_length(

# # #         text,

# # #         fontname="helv",

# # #         fontsize=fontsize

# # #     )


# # #     #
# # #     # Small white rectangle behind text
# # #     #

# # #     padding = 2

# # #     rect = fitz.Rect(

# # #         position["x"] - padding,

# # #         position["y"] - fontsize,

# # #         position["x"] + text_width + padding,

# # #         position["y"] + 2

# # #     )


# # #     page.draw_rect(

# # #         rect,

# # #         color=(1, 1, 1),

# # #         fill=(1, 1, 1)

# # #     )


# # #     #
# # #     # Write replacement value
# # #     #

# # #     page.insert_text(

# # #         (

# # #             position["x"],

# # #             position["y"]

# # #         ),

# # #         text,

# # #         fontname="helv",

# # #         fontsize=fontsize,

# # #         color=colour

# # #     )

# # import fitz


# # def write_text(
# #     page,
# #     value,
# #     position,
# #     font,
# #     clear_rect=None
# # ):

# #     text = str(value)


# #     #
# #     # Clear old value area
# #     #

# #     if clear_rect:

# #         rect = fitz.Rect(

# #             clear_rect["x0"],
# #             clear_rect["y0"],
# #             clear_rect["x1"],
# #             clear_rect["y1"]

# #         )

# #         page.draw_rect(

# #             rect,

# #             color=(1,1,1),

# #             fill=(1,1,1)

# #         )


# #     #
# #     # Write new value
# #     #

# #     page.insert_text(

# #         (
# #             position["x"],
# #             position["y"]
# #         ),

# #         text,

# #         fontname="helv",

# #         fontsize=font["size"],

# #         color=(

# #             font["colour"]["r"] / 255,

# #             font["colour"]["g"] / 255,

# #             font["colour"]["b"] / 255

# #         )

# #     )


# ## NEW VERSION 

# import fitz


# def get_pdf_font_name(font: dict) -> str:
#     """
#     Map extracted font styling to a built-in PyMuPDF font.
#     """

#     return "helv"


# def write_in_area(
#     page,
#     value,
#     clear_rect,
#     baseline_y,
#     font,
#     align="left",
#     padding=2,
# ):
#     """
#     Cover only the old value area, then write the replacement.

#     clear_rect must describe the value area only. It must not include
#     labels or table borders.
#     """

#     text = "" if value is None else str(value)
#     fontsize = float(font["size"])
#     fontname = get_pdf_font_name(font)

#     colour = (
#         font["colour"]["r"] / 255,
#         font["colour"]["g"] / 255,
#         font["colour"]["b"] / 255,
#     )

#     rect = fitz.Rect(
#         clear_rect["x0"],
#         clear_rect["y0"],
#         clear_rect["x1"],
#         clear_rect["y1"],
#     )

#     # Move slightly inside the supplied boundaries so table lines remain.
#     whiteout_rect = fitz.Rect(
#         rect.x0 + 1,
#         rect.y0 + 1,
#         rect.x1 - 1,
#         rect.y1 - 1,
#     )

#     page.draw_rect(
#         whiteout_rect,
#         color=None,
#         fill=(1, 1, 1),
#         overlay=True,
#     )

#     text_width = fitz.get_text_length(
#         text,
#         fontname=fontname,
#         fontsize=fontsize,
#     )

#     if align == "right":
#         x = rect.x1 - padding - text_width
#     elif align == "center":
#         x = rect.x0 + ((rect.width - text_width) / 2)
#     else:
#         x = rect.x0 + padding

#     page.insert_text(
#         (x, baseline_y),
#         text,
#         fontname=fontname,
#         fontsize=fontsize,
#         color=colour,
#         overlay=True,
#     )


# def write_text(
#     page,
#     value,
#     position,
#     font,
# ):
#     """
#     Write into a genuinely blank template area.
#     """

#     text = "" if value is None else str(value)
#     fontname = get_pdf_font_name(font)

#     page.insert_text(
#         (position["x"], position["y"]),
#         text,
#         fontname=fontname,
#         fontsize=float(font["size"]),
#         color=(
#             font["colour"]["r"] / 255,
#             font["colour"]["g"] / 255,
#             font["colour"]["b"] / 255,
#         ),
#         overlay=True,
#     )

## NEWER VERSION

import fitz


def get_pdf_font_name(
    font: dict
) -> str:
    """
    Use regular Helvetica for replacement values.

    This is visually closer to the template values than the
    extracted bold style.
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
    padding=0
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
        value_rect["y0"]
        + row_offset_y,
        value_rect["x1"],
        value_rect["y1"]
        + row_offset_y
    )

    # Keep the white box slightly inside the supplied value rectangle.
    # This prevents it from covering table borders.
    border_inset = 1.25

    whiteout_rect = fitz.Rect(
        rect.x0 + border_inset,
        rect.y0 + border_inset,
        rect.x1 - border_inset,
        rect.y1 - border_inset
    )

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
        (
            x,
            y
        ),

        text,

        fontname=fontname,

        fontsize=fontsize,

        color=colour,

        overlay=True
    )