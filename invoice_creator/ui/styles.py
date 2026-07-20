import streamlit as st


def load_styles() -> None:
    st.markdown(
        """
        <style>
            .block-container {
                max-width: 1500px;
                padding-top: 2rem;
                padding-bottom: 3rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }

            section[data-testid="stSidebar"] {
                border-right: 1px solid #e5e7eb;
            }

            section[data-testid="stSidebar"] .block-container {
                padding-top: 1.5rem;
                padding-left: 1.25rem;
                padding-right: 1.25rem;
            }

            div[data-testid="stMetric"] {
                background: #fafafa;
                padding: 1rem;
                border: 1px solid #e5e7eb;
                border-radius: 0.75rem;
            }

            div.stButton > button {
                width: 100%;
                border-radius: 0.5rem;
            }

            div[data-testid="stAlert"] {
                border-radius: 0.75rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )