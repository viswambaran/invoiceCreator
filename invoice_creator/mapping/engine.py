from invoice_creator.models.invoice import (
    Invoice,
    InvoiceLine
)


VAT_RATE = 0.20


class MappingEngine:


    def __init__(
        self,
        mapping,
        rules
    ):

        self.mapping = mapping
        self.rules = rules



    def build_invoices(
        self,
        rows
    ):

        invoices = []


        grouped = self.group_invoices(
            rows
        )


        for invoice_no, invoice_rows in grouped.items():

            invoices.append(

                self.build_invoice(
                    invoice_rows
                )

            )


        return invoices



    def group_invoices(
        self,
        rows
    ):

        groups = {}


        for row in rows:


            invoice_no = row.get(
                "Invoice No"
            )


            if not invoice_no:

                continue


            if invoice_no not in groups:

                groups[invoice_no] = []


            groups[invoice_no].append(
                row
            )


        return groups



    def build_invoice(
        self,
        rows
    ):


        invoice_lines = []


        for row in rows:


            invoice_lines.extend(

                self.build_lines_from_row(
                    row
                )

            )



        first_row = rows[0]


        net_amount = sum(

            line.net

            for line in invoice_lines

        )


        vat = round(

            net_amount * VAT_RATE,

            2

        )


        invoice_total = round(

            net_amount + vat,

            2

        )


        return Invoice(

            invoice_no=self.get_invoice_value(
                first_row,
                "invoice_no"
            ),


            service_user=self.get_invoice_value(
                first_row,
                "service_user"
            ),


            assessor=self.get_invoice_value(
                first_row,
                "assessor"
            ),


            lines=invoice_lines,


            net_amount=net_amount,


            vat=vat,


            invoice_total=invoice_total

        )



    def build_lines_from_row(
        self,
        row
    ):


        lines = []


        charge_rules = (
            self.rules
            ["invoice_lines"]
            ["charge_types"]
        )


        for rule in charge_rules:


            source_column = (
                rule["source_column"]
            )


            value = row.get(
                source_column
            )


            if value and value > 0:


                lines.append(

                    InvoiceLine(

                        description=
                            rule["description"],


                        units=
                            self.get_units(),


                        rate=
                            value,


                        net=
                            value * self.get_units()

                    )

                )


        return lines

    def get_net(self, row):

        value = row.get(
            "Unnamed: 9"
        )

        if value:

            return float(value)

        return 0

    def get_units(
        self
    ):


        units = (
            self.mapping
            ["invoice_lines"]
            ["units"]
        )


        if units["type"] == "constant":

            return units["value"]


        raise ValueError(
            "Unsupported units mapping"
        )



    def get_invoice_value(
        self,
        row,
        field
    ):


        mapping = (
            self.mapping
            ["invoice"]
            [field]
        )


        if mapping["type"] == "column":

            return row[
                mapping["value"]
            ]


        if mapping["type"] == "constant":

            return mapping["value"]


        raise ValueError(
            f"Unknown mapping type {mapping['type']}"
        )