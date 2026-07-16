import fitz


def write_text(
    page,
    value,
    position,
    font,
    clear_area=None
):


    if clear_area:


        rect = fitz.Rect(

            clear_area["x0"],

            clear_area["y0"],

            clear_area["x1"],

            clear_area["y1"]

        )


        page.add_redact_annot(
            rect
        )


        page.apply_redactions()



    page.insert_text(

        (
            position["x"],
            position["y"]
        ),

        str(value),

        fontname="helv",

        fontsize=font["size"],

        color=(

            font["colour"]["r"] / 255,

            font["colour"]["g"] / 255,

            font["colour"]["b"] / 255

        )

    )