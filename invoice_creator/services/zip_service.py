from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def create_pdf_zip(
    pdf_paths: list[Path],
) -> bytes:
    buffer = BytesIO()

    with ZipFile(
        buffer,
        mode="w",
        compression=ZIP_DEFLATED,
    ) as archive:
        for pdf_path in pdf_paths:
            archive.write(
                pdf_path,
                arcname=pdf_path.name,
            )

    buffer.seek(0)

    return buffer.getvalue()