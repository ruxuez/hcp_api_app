# 1_Projects_States.py
import streamlit as st
import utils
import pandas as pd

st.title("Projects States")

# Check if the required credentials exist in session state
if "HCP_URL" not in st.session_state or "HCP_API_ACCESS_KEY" not in st.session_state:
    st.warning("Please connect to your Hybrid Manager on the main page first.")
    st.info("Navigate back to the 'Connect to Hybrid Manager' page using the sidebar.")
else:
    # Retrieve credentials from session state
    hcp_url = st.session_state.HCP_URL
    hcp_api_access_key = st.session_state.HCP_API_ACCESS_KEY

    # Add a refresh button
    refresh_button = st.button("🔄 Refresh Projects")

    # If the refresh button is clicked, or if the projects_df is empty, fetch the data
    if refresh_button or 'projects_df' not in st.session_state or st.session_state.projects_df.empty:
    # Use st.spinner to show a temporary message while data is being fetched
        with st.spinner("Fetching projects..."):
            try:
                # Call the data_munging function using the stored credentials
                projects_df = utils.get_projects(st.session_state.HCP_URL, st.session_state.HCP_API_ACCESS_KEY)
                st.session_state.projects_df = projects_df # Save the DataFrame to session state
                st.success("Projects list refreshed!")
            except Exception as e:
                st.error(f"Failed to retrieve projects. Please check your credentials and network connection. Error: {e}")
                st.session_state.projects_df = pd.DataFrame() # Ensure session state is empty dataframe on failure

st.header("Project List")
if 'projects_df' in st.session_state and not st.session_state.projects_df.empty:
    st.dataframe(st.session_state.projects_df)
else:
    st.info("No projects found.")