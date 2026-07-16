from invoice_creator.pdf.text_writer import write_text



def write_lines(
    page,
    invoice,
    table_metadata,
    font
):


    table = (
        table_metadata
        ["invoice_lines"]
    )


    y = table["first_row_y"]


    for line in invoice.lines:


        values = {

            "description":
                line.description,

            "units":
                line.units,

            "rate":
                line.rate,

            "net":
                line.net

        }


        for column, value in values.items():


            if column not in table["columns"]:

                continue


            position = (
                table["columns"]
                [column]
                ["write_position"]
            )


            write_text(

                page,

                value,

                {
                    "x": position["x"],
                    "y": y
                },

                font,

                table["columns"][column].get("clear_area")

            )


        y += table["row_height"]