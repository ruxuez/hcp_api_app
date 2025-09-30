import streamlit as st
import utils
import os

st.set_page_config(
    page_title="Hybrid Manager Clusters Management",
    layout="wide",
    page_icon="🚀"
)

st.title("Welcome to the Cluster Management App!")
st.write(
    """
    This app allows users to manage Postgres clusters through the Hybrid Manager API.
    """
)
st.write("Please use the sidebar to navigate between pages.")

st.title("Connect to Hybrid Manager")

# --- 1. Attempt to read environment variables ---
env_hcp_url = os.environ.get("HCP_URL", "")
env_hcp_api_access_key = os.environ.get("HCP_API_ACCESS_KEY", "")


# Check if credentials are already in session state
if "HCP_URL" in st.session_state and "HCP_API_ACCESS_KEY" in st.session_state:
    st.success("You are already connected to Hybrid Manager! Use the sidebar to navigate.")
    st.markdown("---")
    st.dataframe(utils.get_current_user_access_key(st.session_state.HCP_URL, st.session_state.HCP_API_ACCESS_KEY))

else:
    st.warning("Please enter your credentials below or set environment variables (HCP_URL, HCP_API_ACCESS_KEY) before lauching the app.")

    with st.form(key="credentials_form"):
        st.subheader("Enter your API Credentials")
        hcp_url = st.text_input("HCP_URL", env_hcp_url, help="The URL for your Hybrid Manager API.")
        hcp_api_access_key = st.text_input("HCP_API_ACCESS_KEY", env_hcp_api_access_key, type="password", help="Your access key for the API.")

        connect_button = st.form_submit_button("Connect to your Hybrid Manager")

    if connect_button:
        if hcp_url and hcp_api_access_key:
            # Save credentials to session state
            st.session_state.HCP_URL = hcp_url
            st.session_state.HCP_API_ACCESS_KEY = hcp_api_access_key
            st.dataframe(utils.get_current_user_access_key(st.session_state.HCP_URL, st.session_state.HCP_API_ACCESS_KEY))
            st.success("You can now navigate to other pages.")
            # Optionally, you can add a redirect or other logic here.
        else:
            st.error("Please enter both the URL and Access Key to connect.")