import streamlit as st


def load_styles():

    st.markdown(
        """
<style>

.block-container{

padding-top:2rem;

padding-bottom:2rem;

padding-left:2rem;

padding-right:2rem;

}

div[data-testid="stMetric"]{

background:#fafafa;

padding:15px;

border-radius:8px;

border:1px solid #e5e5e5;

}

div.stButton>button{

width:100%;

}

</style>
""",
        unsafe_allow_html=True
    )