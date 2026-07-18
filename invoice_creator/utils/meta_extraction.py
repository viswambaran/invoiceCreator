import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz


TEMPLATE_PATH = Path(
    "templates/Invoice Template.pdf"
)

OUTPUT_PATH = Path(
    "templates/template_metadata.json"
)


def decode_font_flags(
    flags: int
) -> dict[str, bool]:

    return {
        "bold": bool(flags & 16),
        "italic": bool(flags & 2),
        "serif": bool(flags & 4),
        "monospace": bool(flags & 8),
    }


def rgb_colour(
    value: int
) -> dict[str, int]:

    return {
        "r": (value >> 16) & 255,
        "g": (value >> 8) & 255,
        "b": value & 255,
    }


def round_rect(
    rect
) -> dict[str, float]:

    return {
        "x0": round(float(rect.x0), 2),
        "y0": round(float(rect.y0), 2),
        "x1": round(float(rect.x1), 2),
        "y1": round(float(rect.y1), 2),
    }


def extract_text_fields(
    page,
    page_number: int
) -> list[dict[str, Any]]:

    fields: list[dict[str, Any]] = []

    blocks = page.get_text(
        "dict"
    )["blocks"]

    for block in blocks:

        if "lines" not in block:
            continue

        for line in block["lines"]:

            for span in line["spans"]:

                fields.append(
                    {
                        "page":
                            page_number,

                        "text":
                            span["text"],

                        "rect":
                            {
                                "x0": round(
                                    span["bbox"][0],
                                    2
                                ),

                                "y0": round(
                                    span["bbox"][1],
                                    2
                                ),

                                "x1": round(
                                    span["bbox"][2],
                                    2
                                ),

                                "y1": round(
                                    span["bbox"][3],
                                    2
                                ),
                            },

                        "font":
                            {
                                "name":
                                    span["font"],

                                "size":
                                    round(
                                        span["size"],
                                        2
                                    ),

                                "colour":
                                    rgb_colour(
                                        span["color"]
                                    ),

                                "style":
                                    decode_font_flags(
                                        span["flags"]
                                    ),
                            },
                    }
                )

    return fields


def extract_drawings(
    page,
    page_number: int
) -> list[dict[str, Any]]:

    extracted: list[dict[str, Any]] = []

    for drawing in page.get_drawings():

        for item in drawing["items"]:

            item_type = item[0]

            if item_type == "re":

                rect = item[1]

                extracted.append(
                    {
                        "page":
                            page_number,

                        "type":
                            "rectangle",

                        "rect":
                            round_rect(
                                rect
                            ),

                        "width":
                            round(
                                float(
                                    drawing.get(
                                        "width",
                                        0
                                    )
                                ),
                                3
                            ),
                    }
                )

            elif item_type == "l":

                start = item[1]
                end = item[2]

                extracted.append(
                    {
                        "page":
                            page_number,

                        "type":
                            "line",

                        "start":
                            {
                                "x": round(
                                    float(start.x),
                                    2
                                ),

                                "y": round(
                                    float(start.y),
                                    2
                                ),
                            },

                        "end":
                            {
                                "x": round(
                                    float(end.x),
                                    2
                                ),

                                "y": round(
                                    float(end.y),
                                    2
                                ),
                            },

                        "width":
                            round(
                                float(
                                    drawing.get(
                                        "width",
                                        0
                                    )
                                ),
                                3
                            ),
                    }
                )

    return extracted


def extract_metadata(
    pdf_path: Path
) -> dict[str, Any]:

    document = fitz.open(
        pdf_path
    )

    try:

        metadata: dict[str, Any] = {
            "template_name":
                pdf_path.stem,

            "created":
                datetime.now().isoformat(),

            "pages":
                len(document),

            "page_sizes":
                [],

            "fields":
                [],

            "drawings":
                [],
        }

        for page_index, page in enumerate(
            document,
            start=1
        ):

            metadata["page_sizes"].append(
                {
                    "page":
                        page_index,

                    "width":
                        round(
                            float(page.rect.width),
                            2
                        ),

                    "height":
                        round(
                            float(page.rect.height),
                            2
                        ),
                }
            )

            metadata["fields"].extend(
                extract_text_fields(
                    page,
                    page_index
                )
            )

            metadata["drawings"].extend(
                extract_drawings(
                    page,
                    page_index
                )
            )

        return metadata

    finally:

        document.close()


def save_metadata(
    data: dict[str, Any],
    output_path: Path
) -> None:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


if __name__ == "__main__":

    if not TEMPLATE_PATH.exists():

        raise FileNotFoundError(
            f"Missing template: "
            f"{TEMPLATE_PATH}"
        )

    print(
        "Extracting template metadata..."
    )

    metadata = extract_metadata(
        TEMPLATE_PATH
    )

    save_metadata(
        metadata,
        OUTPUT_PATH
    )

    print(
        "Complete"
    )

    print(
        f"Pages: "
        f"{metadata['pages']}"
    )

    print(
        f"Text spans found: "
        f"{len(metadata['fields'])}"
    )

    print(
        f"Drawing items found: "
        f"{len(metadata['drawings'])}"
    )

    print(
        f"Saved: "
        f"{OUTPUT_PATH}"
    )