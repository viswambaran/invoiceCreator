from invoice_creator.importers.excel import ExcelImporter
from invoice_creator.mapping.engine import MappingEngine
from invoice_creator.pdf.writer import InvoicePDFWriter

import json



# load excel

importer = ExcelImporter(
    "data/29.04.2026.xlsx"
)


rows = importer.load_rows()



# load mappings

with open(
    "templates/mapping.json"
) as f:

    mapping = json.load(f)



with open(
    "templates/mapping_rules.json"
) as f:

    rules = json.load(f)



engine = MappingEngine(
    mapping,
    rules
)


invoices = engine.build_invoices(
    rows
)



writer = InvoicePDFWriter(

    "templates/Invoice Template.pdf",

    "templates/template_fields.json",

    "templates/table_metadata.json"

)



writer.generate(

    invoices[0],

    "output/test_invoice.pdf"

)


print(
    "PDF created"
)