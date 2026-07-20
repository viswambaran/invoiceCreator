from __future__ import annotations

import pandas as pd
import streamlit as st

from invoice_creator.services.generation_service import (
    generate_invoices,
)
from invoice_creator.services.zip_service import (
    create_pdf_zip,
)
from invoice_creator.ui.state import (
    clear_generation_results,
    queue_toast,
    request_workflow_step,
)


def _validation_lookup() -> dict[int, object]:
    return {
        result.row_id: result
        for result in (
            st.session_state.validation
        )
    }


def _selected_invoices() -> list:
    validation_by_row = (
        _validation_lookup()
    )

    selected = []

    for invoice in (
        st.session_state.invoices
    ):
        is_selected = (
            st.session_state
            .invoice_selection
            .get(
                invoice.row_id,
                False,
            )
        )

        if not is_selected:
            continue

        validation = validation_by_row.get(
            invoice.row_id
        )

        if (
            validation is not None
            and validation.status
            == "Blocked"
        ):
            continue

        selected.append(
            invoice
        )

    return selected


def _render_selection_summary(
    invoices: list,
) -> None:
    blocked_count = sum(
        result.status == "Blocked"
        for result in (
            st.session_state.validation
        )
    )

    warning_count = sum(
        (
            result.status == "Warning"
            and st.session_state
            .invoice_selection
            .get(
                result.row_id,
                False,
            )
        )
        for result in (
            st.session_state.validation
        )
    )

    column_one, column_two, column_three = (
        st.columns(3)
    )

    column_one.metric(
        "Selected for generation",
        len(invoices),
    )

    column_two.metric(
        "Selected with warnings",
        warning_count,
    )

    column_three.metric(
        "Blocked",
        blocked_count,
    )


def _generate(
    invoices: list,
) -> None:
    clear_generation_results()

    progress = st.progress(
        0,
        text="Preparing PDF generation...",
    )

    status_placeholder = st.empty()

    with status_placeholder.container():
        with st.status(
            "Generating invoice PDFs...",
            expanded=True,
        ) as status:
            status.write(
                "Loading template and metadata."
            )

            def update_progress(
                completed: int,
                total: int,
                invoice_no: str,
            ) -> None:
                if total <= 0:
                    percentage = 100
                else:
                    percentage = int(
                        (
                            completed
                            / total
                        )
                        * 100
                    )

                progress.progress(
                    percentage,
                    text=(
                        f"Generating invoice "
                        f"{completed} of {total}: "
                        f"{invoice_no}"
                    ),
                )

                status.write(
                    (
                        f"Processed {completed} of "
                        f"{total}: {invoice_no}"
                    )
                )

            try:
                result = generate_invoices(
                    invoices=invoices,
                    template_bytes=(
                        st.session_state
                        .template_bytes
                    ),
                    progress_callback=(
                        update_progress
                    ),
                )

                status.write(
                    "Creating the ZIP download."
                )

                generated_paths = [
                    generated.path
                    for generated
                    in result.generated
                ]

                generated_zip = create_pdf_zip(
                    generated_paths
                )

                st.session_state.generation_result = (
                    result
                )

                st.session_state.generated_zip = (
                    generated_zip
                )

                progress.progress(
                    100,
                    text="PDF generation complete.",
                )

                if result.failures:
                    status.update(
                        label=(
                            "Generation completed "
                            "with some failures"
                        ),
                        state="error",
                        expanded=True,
                    )

                    queue_toast(
                        (
                            f"{len(result.generated)} PDFs "
                            f"generated and "
                            f"{len(result.failures)} failed."
                        ),
                        icon="⚠️",
                    )

                else:
                    status.update(
                        label=(
                            f"Generation complete — "
                            f"{len(result.generated)} "
                            f"PDFs created"
                        ),
                        state="complete",
                        expanded=False,
                    )

                    queue_toast(
                        (
                            f"{len(result.generated)} invoice "
                            f"PDFs generated successfully."
                        ),
                        icon="✅",
                    )

                request_workflow_step(
                    "Generate"
                )

                st.rerun()

            except Exception as exc:
                progress.empty()

                status.update(
                    label="PDF generation failed",
                    state="error",
                    expanded=True,
                )

                st.error(
                    (
                        "An unexpected error occurred "
                        "during PDF generation."
                    )
                )

                st.exception(exc)


def _render_generation_results() -> None:
    result = (
        st.session_state.generation_result
    )

    if result is None:
        return

    st.divider()

    st.subheader(
        "Generation results"
    )

    generated_count = len(
        result.generated
    )

    failure_count = len(
        result.failures
    )

    column_one, column_two = (
        st.columns(2)
    )

    column_one.metric(
        "Generated",
        generated_count,
    )

    column_two.metric(
        "Failed",
        failure_count,
    )

    if result.generated:
        st.success(
            (
                f"{generated_count} invoice "
                f"{'PDF was' if generated_count == 1 else 'PDFs were'} "
                "generated successfully."
            ),
            icon="✅",
        )

        zip_data = (
            st.session_state.generated_zip
        )

        if zip_data:
            st.download_button(
                "Download All PDFs as ZIP",
                data=zip_data,
                file_name="Invoices.zip",
                mime="application/zip",
                type="primary",
                width="stretch",
            )

        generated_dataframe = (
            pd.DataFrame(
                [
                    {
                        "Invoice": (
                            generated.invoice_no
                        ),
                        "Filename": (
                            generated.filename
                        ),
                    }
                    for generated
                    in result.generated
                ]
            )
        )

        st.dataframe(
            generated_dataframe,
            hide_index=True,
            width="stretch",
        )

    if result.failures:
        st.error(
            (
                f"{failure_count} invoice "
                f"{'failed' if failure_count == 1 else 'invoices failed'} "
                "to generate."
            )
        )

        failure_dataframe = (
            pd.DataFrame(
                [
                    {
                        "Invoice": (
                            failure.invoice_no
                        ),
                        "Reason": (
                            failure.message
                        ),
                    }
                    for failure
                    in result.failures
                ]
            )
        )

        st.dataframe(
            failure_dataframe,
            hide_index=True,
            width="stretch",
        )

    if st.button(
        "Generate Again",
        width="stretch",
    ):
        clear_generation_results()

        st.rerun()


def render_generate_tab() -> None:
    st.header(
        "Generate PDFs"
    )

    if not st.session_state.invoices:
        st.info(
            (
                "Build invoices from the "
                "Upload step first."
            )
        )

        if st.button(
            "Go to Upload",
            width="stretch",
        ):
            request_workflow_step(
                "Upload"
            )

            st.rerun()

        return

    invoices = (
        _selected_invoices()
    )

    _render_selection_summary(
        invoices
    )

    existing_result = (
        st.session_state.generation_result
    )

    if existing_result is not None:
        _render_generation_results()
        return

    if not invoices:
        st.warning(
            (
                "No eligible invoices are currently "
                "selected for generation."
            )
        )

        if st.button(
            "Return to Review",
            width="stretch",
        ):
            request_workflow_step(
                "Review"
            )

            st.rerun()

        return

    st.info(
        (
            f"{len(invoices)} "
            f"{'invoice is' if len(invoices) == 1 else 'invoices are'} "
            "ready to generate."
        ),
        icon="🧾",
    )

    left_column, right_column = (
        st.columns(2)
    )

    with left_column:
        if st.button(
            "Return to Review",
            width="stretch",
        ):
            request_workflow_step(
                "Review"
            )

            st.rerun()

    with right_column:
        if st.button(
            "Generate PDFs",
            type="primary",
            width="stretch",
        ):
            _generate(
                invoices
            )