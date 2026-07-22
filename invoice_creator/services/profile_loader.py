from __future__ import annotations

import json
from pathlib import Path

from invoice_creator.models.invoice_profile import InvoiceProfile


TEMPLATES_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "templates"
)

PROFILE_FILE = (
    TEMPLATES_DIRECTORY
    / "invoice_profiles.json"
)


class ProfileLoader:

    def __init__(self) -> None:
        with PROFILE_FILE.open(
            "r",
            encoding="utf-8",
        ) as f:
            self._profiles = json.load(f)

    def all(self) -> list[InvoiceProfile]:
        return [
            self.get(profile_id)
            for profile_id in self._profiles
        ]

    def get(self, profile_id: str) -> InvoiceProfile:

        data = self._profiles[profile_id]

        return InvoiceProfile(
            id=profile_id,
            display_name=data["display_name"],
            template_path=(
                TEMPLATES_DIRECTORY
                / data["template"]
            ),
            generation_mode=data["generation_mode"],
        )