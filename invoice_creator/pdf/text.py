import fitz


def write_text(
    page,
    value,
    position,
    font,
    bold=False
):

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