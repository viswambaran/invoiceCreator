import streamlit as st

from datetime import date


def render_upload_tab():

    st.header("Upload")

    left,right=st.columns([2,1])

    with left:

        st.subheader("Source files")

        excel=st.file_uploader(

            "Excel Workbook",

            type=["xlsx"]

        )

        template=st.file_uploader(

            "PDF Template (optional)",

            type=["pdf"]

        )

        if excel:

            st.session_state.excel_file=excel

        if template:

            st.session_state.template_file=template

        st.divider()

        st.subheader("Invoice Date")

        mode=st.radio(

            "Date Source",

            [

                "Use one date for all invoices",

                "Read from Excel",

                "Assign later"

            ]

        )

        if mode=="Use one date for all invoices":

            st.session_state.invoice_date=st.date_input(

                "Invoice Date",

                value=date.today(),

                format="DD/MM/YYYY"

            )

    with right:

        st.subheader("Current Session")

        st.metric(

            "Excel",

            "Loaded" if st.session_state.excel_file else "None"

        )

        st.metric(

            "Template",

            "Default"

            if st.session_state.template_file is None

            else "Uploaded"

        )

        st.metric(

            "Invoices",

            len(st.session_state.invoices)

        )