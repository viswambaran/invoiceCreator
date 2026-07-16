import json

from invoice_creator.importers.excel import (
    ExcelImporter
)

from invoice_creator.mapping.engine import (
    MappingEngine
)



MAPPING_FILE = (
    "templates/mapping.json"
)

RULES_FILE = (
    "templates/mapping_rules.json"
)

EXCEL_FILE = (
    "sample_invoice.xlsx"
)



def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



if __name__ == "__main__":


    mapping = load_json(
        MAPPING_FILE
    )


    rules = load_json(
        RULES_FILE
    )


    importer = ExcelImporter(
        EXCEL_FILE
    )


    rows = importer.load_rows()



    engine = MappingEngine(

        mapping,

        rules

    )


    invoices = engine.build_invoices(
        rows
    )


print()

print("Invoices Generated")
print("------------------")


for invoice in invoices:


    print()

    print(
        invoice.invoice_no
    )

    print(
        invoice.service_user
    )

    print(
        invoice.assessor
    )

    print()


    for line in invoice.lines:

        print(
            line.description,
            "|",
            line.units,
            "|",
            line.rate,
            "|",
            line.net
        )


    print()

    print(
        "Net:",
        invoice.net_amount
    )

    print(
        "VAT:",
        invoice.vat
    )

    print(
        "Total:",
        invoice.invoice_total
    )
