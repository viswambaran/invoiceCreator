import streamlit as st


DEFAULTS = {

    "excel_file":None,

    "template_file":None,

    "invoices":[],

    "validation":[],

    "mapping":None,

    "layout":None,

    "selected_invoice":None,

    "invoice_date":None,

    "generated_files":[]

}


def initialise_state():

    for key,value in DEFAULTS.items():

        if key not in st.session_state:

            st.session_state[key]=value