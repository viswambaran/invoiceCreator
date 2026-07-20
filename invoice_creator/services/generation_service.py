from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from invoice_creator.pdf.writer import InvoicePDFWriter


@dataclass
class GenerationFailure:
    invoice_no: str
    error: str


@dataclass
class GenerationResult:
    output_directory: Path
    generated_files: list[Path] = field(default_factory=list)
    failures: list[GenerationFailure] = field(default_factory=list)


def _safe_filename(invoice_no: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", invoice_no.strip())
    name = name.rstrip(". ")
    return name or "invoice"


def generate_invoices(
    invoices: Iterable,
    template_path: Path,
    fields_path: Path,
    table_path: Path,
    output_directory: Path | None = None,
) -> GenerationResult:

    if output_directory is None:
        output_directory = Path(
            tempfile.mkdtemp(prefix="invoice_creator_")
        )

    output_directory.mkdir(parents=True, exist_ok=True)

    result = GenerationResult(output_directory)

    writer = InvoicePDFWriter(
        template_path=template_path,
        fields_path=fields_path,
        table_path=table_path,
    )

    used_names: set[str] = set()

    for invoice in invoices:

        invoice_no = str(invoice.invoice_no)

        filename = _safe_filename(invoice_no)

        candidate = filename
        counter = 2

        while candidate.lower() in used_names:
            candidate = f"{filename}_{counter}"
            counter += 1

        used_names.add(candidate.lower())

        output_pdf = output_directory / f"{candidate}.pdf"

        try:

            #
            # THIS IS THE IMPORTANT LINE
            #

            writer.generate(
                invoice=invoice,
                output_path=output_pdf,
            )

            result.generated_files.append(output_pdf)

        except Exception as exc:

            result.failures.append(
                GenerationFailure(
                    invoice_no=invoice_no,
                    error=str(exc),
                )
            )

    return result