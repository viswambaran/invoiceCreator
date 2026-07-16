import fitz
import json
from pathlib import Path
from datetime import datetime


TEMPLATE_PATH = Path(
    "templates/Invoice Template.pdf"
)

OUTPUT_PATH = Path(
    "templates/template_metadata.json"
)


def decode_font_flags(flags):

    return {
        "bold": bool(flags & 16),
        "italic": bool(flags & 2),
        "serif": bool(flags & 4),
        "monospace": bool(flags & 8),
    }


def rgb_colour(value):

    return {
        "r": (value >> 16) & 255,
        "g": (value >> 8) & 255,
        "b": value & 255
    }


def extract_metadata(pdf_path):

    doc = fitz.open(pdf_path)

    metadata = {

        "template_name": pdf_path.stem,

        "created": datetime.now().isoformat(),

        "pages": len(doc),

        "fields": []

    }


    for page_number, page in enumerate(doc, start=1):

        blocks = page.get_text(
            "dict"
        )["blocks"]


        for block in blocks:

            if "lines" not in block:
                continue


            for line in block["lines"]:


                for span in line["spans"]:


                    field = {

                        "page": page_number,

                        "text": span["text"],


                        "rect": {

                            "x0": round(span["bbox"][0],2),
                            "y0": round(span["bbox"][1],2),
                            "x1": round(span["bbox"][2],2),
                            "y1": round(span["bbox"][3],2)

                        },


                        "font": {

                            "name": span["font"],

                            "size": round(
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
                                )

                        }

                    }


                    metadata["fields"].append(
                        field
                    )


    return metadata



def save_metadata(data, output):

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )



if __name__ == "__main__":


    if not TEMPLATE_PATH.exists():

        raise FileNotFoundError(
            f"Missing template: {TEMPLATE_PATH}"
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
        f"Pages: {metadata['pages']}"
    )

    print(
        f"Fields found: {len(metadata['fields'])}"
    )

    print(
        f"Saved: {OUTPUT_PATH}"
    )