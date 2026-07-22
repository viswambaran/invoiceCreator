from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


GenerationMode = Literal["single", "grouped"]


@dataclass(slots=True, frozen=True)
class InvoiceProfile:
    """
    Defines how invoices should be generated for a client profile.
    """

    id: str
    display_name: str
    template_path: Path
    generation_mode: GenerationMode

    @property
    def grouped(self) -> bool:
        return self.generation_mode == "grouped"

    @property
    def single(self) -> bool:
        return self.generation_mode == "single"