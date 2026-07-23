from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd


ExcelSource = (
    str
    | Path
    | bytes
    | bytearray
    | BinaryIO
)


class ExcelImporter:
    def __init__(
        self,
        source: ExcelSource,
        sheet_name: str | int = 0,
    ) -> None:
        self.source = source
        self.sheet_name = sheet_name

    def _create_source(self):
        if isinstance(
            self.source,
            (bytes, bytearray),
        ):
            return BytesIO(self.source)

        if hasattr(self.source, "seek"):
            self.source.seek(0)

        return self.source

    def load_dataframe(self) -> pd.DataFrame:
        source = self._create_source()

        dataframe = pd.read_excel(
            source,
            sheet_name=self.sheet_name,
        )

        dataframe.columns = [
            str(column).strip()
            for column in dataframe.columns
        ]

        dataframe = dataframe.dropna(
            how="all",
        ).reset_index(
            drop=True
        )

        return dataframe

    def load_rows(self) -> list[dict]:
        dataframe = self.load_dataframe()

        return dataframe.to_dict(
            orient="records"
        )

    def get_sheet_names(self) -> list[str]:
        source = self._create_source()

        workbook = pd.ExcelFile(source)

        return list(workbook.sheet_names)