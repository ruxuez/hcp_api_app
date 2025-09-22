# 1_Projects_States.py
from logzero import logger
import pandas as pd
import streamlit as st
import utils
from time import sleep

st.markdown(
    """
    <style>
    .small-font {
        font-size:12px;
        font-style: italic;
        color: #b1a7a6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

TABLE_PAGE_LEN = 10

st.title("Projects States")

# Check if the required credentials exist in session state
if "HCP_URL" not in st.session_state or "HCP_API_ACCESS_KEY" not in st.session_state:
    st.warning("Please connect to your Hybrid Manager on the main page first.")
    st.info("Navigate back to the 'Connect to Hybrid Manager' page using the sidebar.")
else:
    # Retrieve credentials from session state
    hcp_url = st.session_state.HCP_URL
    hcp_api_access_key = st.session_state.HCP_API_ACCESS_KEY

    # Use st.spinner to show a temporary message while data is being fetched
    with st.spinner("Fetching projects..."):
        try:
            # Call the data_munging function using the stored credentials
            projects_df = utils.get_projects(st.session_state.HCP_URL, st.session_state.HCP_API_ACCESS_KEY)
            st.header("Project List")
            if not projects_df.empty:
                st.dataframe(projects_df)
            else:
                st.info("No projects found.")
        except Exception as e:
            st.error(f"Failed to retrieve projects. Please check your credentials and network connection. Error: {e}")