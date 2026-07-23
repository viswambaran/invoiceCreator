from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from invoice_creator.services.generation_service import generate_invoices
from invoice_creator.services.settings_service import save_settings
from invoice_creator.services.zip_service import create_pdf_zip
from invoice_creator.ui.state import (
    clear_generation_results,
    queue_toast,
    request_workflow_step,
)


OUTPUT_FOLDER = "Save to folder"
OUTPUT_ZIP = "Download ZIP"
OUTPUT_BOTH = "Folder + ZIP"


def _persist_output_settings() -> None:
    save_settings(
        {
            "output_mode": st.session_state.output_mode,
            "output_folder": st.session_state.output_folder,
            "create_timestamped_folder": st.session_state.create_timestamped_folder,
            "overwrite_existing_pdfs": st.session_state.overwrite_existing_pdfs,
            "open_folder_when_finished": st.session_state.open_folder_when_finished,
        }
    )


def _validation_lookup() -> dict[int, object]:
    return {result.row_id: result for result in st.session_state.validation}


def _selected_invoices() -> list:
    validation_by_row = _validation_lookup()
    selected = []

    for invoice in st.session_state.invoices:
        if not st.session_state.invoice_selection.get(invoice.row_id, False):
            continue

        validation = validation_by_row.get(invoice.row_id)
        if validation is not None and validation.status == "Blocked":
            continue

        selected.append(invoice)

    return selected


def _default_output_folder() -> Path:
    """Return a portable per-user output folder without hardcoded usernames."""
    home = Path.home()
    documents = home / "Documents"
    base = documents if documents.exists() else home
    return base / "Invoice Creator" / "Generated Invoices"


def _choose_folder(initial_folder: Path) -> str | None:
    """Open a native folder picker when the app is running locally."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(
            initialdir=str(initial_folder.expanduser()),
            title="Choose invoice output folder",
        )
        root.destroy()
        return selected or None
    except Exception:
        return None


def _open_folder(path: Path) -> None:
    resolved = path.expanduser().resolve()

    if not resolved.exists():
        raise FileNotFoundError(f"Output folder does not exist: {resolved}")

    if sys.platform.startswith("win"):
        os.startfile(str(resolved))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(resolved)])
    else:
        subprocess.Popen(["xdg-open", str(resolved)])


def _render_selection_summary(invoices: list) -> None:
    blocked_count = sum(
        result.status == "Blocked" for result in st.session_state.validation
    )
    warning_count = sum(
        result.status == "Warning"
        and st.session_state.invoice_selection.get(result.row_id, False)
        for result in st.session_state.validation
    )

    column_one, column_two, column_three = st.columns(3)
    column_one.metric("Selected for generation", len(invoices))
    column_two.metric("Selected with warnings", warning_count)
    column_three.metric("Blocked", blocked_count)


def _resolved_output_directory() -> Path | None:
    mode = st.session_state.output_mode

    if mode == OUTPUT_ZIP:
        return None

    base = Path(st.session_state.output_folder).expanduser()

    if st.session_state.create_timestamped_folder:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        return base / timestamp

    return base


def _generate(invoices: list) -> None:
    clear_generation_results()

    output_mode = st.session_state.output_mode
    output_directory = _resolved_output_directory()

    progress = st.progress(0, text="Preparing PDF generation...")
    status_placeholder = st.empty()

    with status_placeholder.container():
        with st.status("Generating invoice PDFs...", expanded=True) as status:
            status.write("Loading template and metadata.")

            def update_progress(completed: int, total: int, invoice_no: str) -> None:
                percentage = 100 if total <= 0 else int((completed / total) * 100)
                progress.progress(
                    percentage,
                    text=f"Invoice {completed} of {total}: {invoice_no}",
                )
                status.write(f"Processed {completed} of {total}: {invoice_no}")

            try:
                job = st.session_state.current_job

                if job is None or job.profile is None:
                    raise RuntimeError(
                        "No invoice profile has been selected."
                    )

                result = generate_invoices(
                    invoices=invoices,
                    template_path=job.profile.template_path,
                    output_directory=output_directory,
                    progress_callback=update_progress,
                    overwrite_existing=st.session_state.overwrite_existing_pdfs,
                    generation_mode=job.profile.generation_mode
                )

                generated_paths = [item.path for item in result.generated]
                generated_zip = None

                if output_mode in {OUTPUT_ZIP, OUTPUT_BOTH} and generated_paths:
                    status.write("Creating the ZIP archive.")
                    generated_zip = create_pdf_zip(generated_paths)

                st.session_state.generation_result = result
                st.session_state.generated_zip = generated_zip
                st.session_state.last_output_directory = str(result.output_directory)

                if (
                    output_mode in {OUTPUT_FOLDER, OUTPUT_BOTH}
                    and st.session_state.open_folder_when_finished
                    and result.generated
                ):
                    try:
                        _open_folder(result.output_directory)
                    except Exception:
                        # The completed page still provides an Open Folder button.
                        pass

                progress.progress(100, text="PDF generation complete.")

                if result.failures:
                    status.update(
                        label="Generation completed with some failures",
                        state="error",
                        expanded=True,
                    )
                    queue_toast(
                        f"{len(result.generated)} PDFs generated and "
                        f"{len(result.failures)} failed.",
                        icon="⚠️",
                    )
                else:
                    status.update(
                        label=f"Generation complete — {len(result.generated)} PDFs created",
                        state="complete",
                        expanded=False,
                    )
                    queue_toast(
                        f"{len(result.generated)} invoice PDFs generated successfully.",
                        icon="✅",
                    )

                request_workflow_step("Generate")
                st.rerun()

            except Exception as exc:
                progress.empty()
                status.update(
                    label="PDF generation failed",
                    state="error",
                    expanded=True,
                )
                st.error(
                    "Invoice Creator could not generate the PDFs. "
                    "Check the destination folder and template, then try again."
                )
                with st.expander("Technical details"):
                    st.code(f"{type(exc).__name__}: {exc}", language=None)


def _render_generation_results() -> None:
    result = st.session_state.generation_result
    if result is None:
        return

    st.divider()
    st.subheader("🎉 Generation complete")

    generated_count = len(result.generated)
    failure_count = len(result.failures)
    column_one, column_two = st.columns(2)
    column_one.metric("PDFs created", generated_count)
    column_two.metric("Failed", failure_count)

    if result.generated:
        st.success(
            f"{generated_count} invoice "
            f"{'PDF was' if generated_count == 1 else 'PDFs were'} generated successfully.",
            icon="✅",
        )

        if st.session_state.output_mode in {OUTPUT_FOLDER, OUTPUT_BOTH}:
            output_path = Path(result.output_directory)
            st.markdown("**Saved to**")
            st.code(str(output_path), language=None)

            if st.button("📂 Open folder", type="primary", width="stretch"):
                try:
                    _open_folder(output_path)
                except Exception as exc:
                    st.error("The output folder could not be opened automatically.")
                    with st.expander("Technical details"):
                        st.code(f"{type(exc).__name__}: {exc}", language=None)

        zip_data = st.session_state.generated_zip
        if zip_data:
            st.download_button(
                "📦 Download all PDFs as ZIP",
                data=zip_data,
                file_name=f"Invoices_{datetime.now():%Y-%m-%d}.zip",
                mime="application/zip",
                type="primary" if st.session_state.output_mode == OUTPUT_ZIP else "secondary",
                width="stretch",
            )

        generated_dataframe = pd.DataFrame(
            [
                {"Invoice": item.invoice_no, "Filename": item.filename}
                for item in result.generated
            ]
        )
        st.dataframe(generated_dataframe, hide_index=True, width="stretch")

    if result.failures:
        st.error(
            f"{failure_count} invoice "
            f"{'failed' if failure_count == 1 else 'invoices failed'} to generate."
        )
        failure_dataframe = pd.DataFrame(
            [
                {"Invoice": failure.invoice_no, "Reason": failure.message}
                for failure in result.failures
            ]
        )
        st.dataframe(failure_dataframe, hide_index=True, width="stretch")

    if st.button("Generate another batch", width="stretch"):
        clear_generation_results()
        st.rerun()


def _render_output_settings() -> None:
    # A folder chosen from the native dialog must be applied before the
    # text_input widget using the output_folder key is instantiated.
    pending_folder = st.session_state.pop("pending_output_folder", None)
    if pending_folder:
        st.session_state.output_folder = pending_folder

    st.subheader("📦 Output")
    st.caption("Choose where the completed invoice PDFs should be delivered.")

    st.radio(
        "Output method",
        options=[OUTPUT_FOLDER, OUTPUT_ZIP, OUTPUT_BOTH],
        key="output_mode",
        horizontal=True,
        on_change=_persist_output_settings,
        help=(
            "Save to folder is recommended for normal desktop use. "
            "ZIP is useful for sharing or archiving a batch."
        ),
    )

    if st.session_state.output_mode == OUTPUT_ZIP:
        st.info(
            "The PDFs will be created temporarily and offered as one ZIP download.",
            icon="📦",
        )
        return

    folder_column, browse_column = st.columns([5, 1])

    with folder_column:
        st.text_input(
            "Destination folder",
            key="output_folder",
            help=(
                "This defaults to the current computer user's Documents folder. "
                "It does not contain a hardcoded username."
            ),
            on_change=_persist_output_settings,
        )

    with browse_column:
        st.write("")
        st.write("")
        if st.button("Browse…", width="stretch"):
            selected = _choose_folder(Path(st.session_state.output_folder))
            if selected:
                st.session_state.pending_output_folder = selected
                save_settings(
                    {
                        "output_mode": st.session_state.output_mode,
                        "output_folder": selected,
                        "create_timestamped_folder": st.session_state.create_timestamped_folder,
                        "overwrite_existing_pdfs": st.session_state.overwrite_existing_pdfs,
                        "open_folder_when_finished": st.session_state.open_folder_when_finished,
                    }
                )
                st.rerun()
            else:
                st.info(
                    "The native folder picker was unavailable or no folder was selected. "
                    "You can type or paste the path instead."
                )

    option_one, option_two, option_three = st.columns(3)

    with option_one:
        st.checkbox(
            "Create timestamped folder",
            key="create_timestamped_folder",
            help="Creates a new subfolder such as 2026-07-21_143015 for each batch.",
            on_change=_persist_output_settings,
        )

    with option_two:
        st.checkbox(
            "Overwrite existing PDFs",
            key="overwrite_existing_pdfs",
            help="When disabled, duplicate filenames receive a numbered suffix.",
            on_change=_persist_output_settings,
        )

    with option_three:
        st.checkbox(
            "Open folder when finished",
            key="open_folder_when_finished",
            on_change=_persist_output_settings,
        )

    resolved = _resolved_output_directory()
    if resolved is not None:
        st.caption(f"This batch will be saved to: {resolved}")


def render_generate_tab() -> None:
    st.header("🚀 Generate invoice PDFs")

    if not st.session_state.invoices:
        st.info("Build invoices from the Upload step first.")
        if st.button("Go to Upload", width="stretch"):
            request_workflow_step("Upload")
            st.rerun()
        return

    invoices = _selected_invoices()
    _render_selection_summary(invoices)

    if st.session_state.generation_result is not None:
        _render_generation_results()
        return

    if not invoices:
        st.warning("No eligible invoices are currently selected for generation.")
        if st.button("Return to Review", width="stretch"):
            request_workflow_step("Review")
            st.rerun()
        return

    st.info(
        f"{len(invoices)} "
        f"{'invoice is' if len(invoices) == 1 else 'invoices are'} ready to generate.",
        icon="🧾",
    )

    _render_output_settings()

    left_column, right_column = st.columns(2)

    with left_column:
        if st.button("Return to Review", width="stretch"):
            request_workflow_step("Review")
            st.rerun()

    with right_column:
        if st.button("Generate PDFs", type="primary", width="stretch"):
            _generate(invoices)
