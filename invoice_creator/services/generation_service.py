from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from invoice_creator.models.invoice import Invoice
from invoice_creator.pdf.writer import InvoicePDFWriter
from invoice_creator.services.app_paths import (
    PDF_DIRECTORY,
    SHARED_DIRECTORY,
)


DEFAULT_TEMPLATE_PATH = (
    PDF_DIRECTORY
    / "Invoice Template.pdf"
)

DEFAULT_FIELDS_PATH = (
    SHARED_DIRECTORY
    / "template_fields.json"
)

DEFAULT_TABLE_PATH = (
    SHARED_DIRECTORY
    / "table_metadata.json"
)

ProgressCallback = Callable[[int, int, str], None]


@dataclass
class GeneratedInvoice:
    invoice_no: str
    filename: str
    path: Path


@dataclass
class GenerationFailure:
    invoice_no: str
    message: str


@dataclass
class GenerationResult:
    output_directory: Path
    generated: list[GeneratedInvoice] = field(default_factory=list)
    failures: list[GenerationFailure] = field(default_factory=list)


class InvoiceGenerationError(Exception):
    pass


def _safe_filename(invoice_no: str) -> str:
    cleaned = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        invoice_no.strip(),
    )
    cleaned = cleaned.rstrip(". ")
    return cleaned or "invoice"


def _validate_required_file(path: Path, description: str) -> None:
    if not path.exists():
        raise InvoiceGenerationError(
            f"{description} was not found: {path}"
        )

    if not path.is_file():
        raise InvoiceGenerationError(
            f"{description} is not a file: {path}"
        )


def generate_invoices(
    invoices: Iterable[Invoice],
    template_path: Path | None = None,
    output_directory: Path | None = None,
    fields_path: Path | None = None,
    table_path: Path | None = None,
    progress_callback: ProgressCallback | None = None,
    overwrite_existing: bool = True,
) -> GenerationResult:
    invoice_list = list(invoices)
    total_invoices = len(invoice_list)

    if not invoice_list:
        raise InvoiceGenerationError(
            "No invoices were supplied for generation."
        )

    if output_directory is None:
        output_directory = Path(
            tempfile.mkdtemp(prefix="invoice_creator_")
        )
    else:
        output_directory = Path(output_directory).expanduser()

    output_directory.mkdir(parents=True, exist_ok=True)

    resolved_fields_path = fields_path or DEFAULT_FIELDS_PATH
    resolved_table_path = table_path or DEFAULT_TABLE_PATH

    _validate_required_file(
        resolved_fields_path,
        "Template field metadata",
    )
    _validate_required_file(
        resolved_table_path,
        "Table metadata",
    )

    # template_path = _prepare_template(
    #     output_directory=output_directory,
    #     template_bytes=template_bytes,
    # )

    _validate_required_file(
        template_path,
        "Invoice template",
    )
    
    writer = InvoicePDFWriter(
        template_path=template_path,
        fields_path=resolved_fields_path,
        table_path=resolved_table_path,
    )

    result = GenerationResult(
        output_directory=output_directory
    )
    used_filenames: set[str] = set()

    for index, invoice in enumerate(
        invoice_list,
        start=1,
    ):
        invoice_no = str(invoice.invoice_no).strip()
        base_filename = _safe_filename(invoice_no)
        candidate = base_filename
        counter = 2

        while candidate.casefold() in used_filenames:
            candidate = f"{base_filename}_{counter}"
            counter += 1

        used_filenames.add(candidate.casefold())
        filename = f"{candidate}.pdf"
        output_path = output_directory / filename

        if not overwrite_existing:
            while output_path.exists():
                candidate = f"{base_filename}_{counter}"
                counter += 1
                filename = f"{candidate}.pdf"
                output_path = output_directory / filename

            used_filenames.add(candidate.casefold())

        try:
            writer.generate(
                invoice=invoice,
                output_path=output_path,
            )

            if not output_path.exists():
                raise InvoiceGenerationError(
                    "The PDF writer completed but did not create an output file."
                )

            result.generated.append(
                GeneratedInvoice(
                    invoice_no=invoice_no,
                    filename=filename,
                    path=output_path,
                )
            )

        except Exception as exc:
            result.failures.append(
                GenerationFailure(
                    invoice_no=invoice_no,
                    message=str(exc),
                )
            )

        finally:
            if progress_callback is not None:
                progress_callback(
                    index,
                    total_invoices,
                    invoice_no,
                )

    uploaded_copy = output_directory / "_uploaded_template.pdf"
    if uploaded_copy.exists():
        try:
            uploaded_copy.unlink()
        except OSError:
            pass

    return result
