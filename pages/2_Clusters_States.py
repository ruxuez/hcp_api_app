# 2_Cluster_States.py
import pandas as pd
import streamlit as st
import utils

st.title("Clusters States")

# Check if the required credentials exist in session state
if "HCP_URL" not in st.session_state or "HCP_API_ACCESS_KEY" not in st.session_state:
    st.warning("Please connect to your Hybrid Manager on the main page first.")
    st.info("Navigate back to the 'Connect to Hybrid Manager' page using the sidebar.")
else:
    # Retrieve credentials from session state
    hcp_url = st.session_state.HCP_URL
    hcp_api_access_key = st.session_state.HCP_API_ACCESS_KEY

    # Initialize session state for this page
    if "project_id_entered" not in st.session_state:
        st.session_state.project_id_entered = False
    if "delete_mode" not in st.session_state:
        st.session_state.delete_mode = False
    if "create_mode" not in st.session_state:
        st.session_state.create_mode = False
    if "clusters_df" not in st.session_state:
        st.session_state.clusters_df = pd.DataFrame()

    with st.sidebar.form(key="project_id_form"):
        st.subheader("Select a Project ID")
        # Check if project data is available in session state
        if 'projects_df' in st.session_state and not st.session_state.projects_df.empty:
            # Create a list of project IDs for the selectbox
            project_options = st.session_state.projects_df['projectId'].tolist()
            hcp_project_id = st.selectbox("HCP Project ID", options=project_options)
            project_submit = st.form_submit_button("List Clusters")
        else:
            st.warning("No projects found. Please go to the 'Projects States' page to list your projects first.")
            project_submit = False
            hcp_project_id = None
        
    if project_submit:
        if hcp_project_id:
            st.session_state.hcp_project_id = hcp_project_id
            st.session_state.project_id_entered = True

            # This is the new refresh logic for the button
            with st.spinner("Refreshing clusters..."):
                try:
                    st.session_state.clusters_df = utils.get_clusters(
                        hcp_url, hcp_api_access_key, st.session_state.hcp_project_id
                    )
                    st.success("Clusters refreshed successfully!")
                except Exception as e:
                    st.error(f"Failed to refresh clusters. Error: {e}")
                    st.session_state.clusters_df = pd.DataFrame()
        else:
            st.error("Please select a Project ID.")

    # Main content area
    if st.session_state.project_id_entered:
        st.header(f"Clusters for Project: `{st.session_state.hcp_project_id}`")
        
        c1, c2, c3, _ = st.columns([2, 2, 2, 8])
        create_button = c1.button("➕ Create Cluster")
        delete_button = c2.button("➖ Delete Cluster")
        refresh_button = c3.button("🔄 Refresh")

        # Logic to enter/exit create mode
        if create_button:
            st.session_state.create_mode = True
            st.session_state.delete_mode = False
        
        # Logic to enter/exit delete mode
        if delete_button:
            st.session_state.delete_mode = True
            st.session_state.create_mode = False

        # Refresh button logic
        if refresh_button:
            with st.spinner("Refreshing clusters..."):
                try:
                    st.session_state.clusters_df = utils.get_clusters(
                        hcp_url, hcp_api_access_key, st.session_state.hcp_project_id
                    )
                    st.success("Clusters refreshed successfully!")
                except Exception as e:
                    st.error(f"Failed to refresh clusters. Error: {e}")
                    st.session_state.clusters_df = pd.DataFrame()

        # Display the cluster table. Added a check for None before calling .empty
        if st.session_state.clusters_df is not None and not st.session_state.clusters_df.empty:
            st.dataframe(st.session_state.clusters_df)
        elif not st.session_state.create_mode and not st.session_state.delete_mode:
            st.info("No clusters found for this project.")

        if st.session_state.delete_mode:
            with st.form("delete_cluster_form"):
                cluster_to_delete = st.text_input("Enter Cluster ID to delete")
                submit_delete = st.form_submit_button("Submit Deletion")

                if submit_delete:
                    if cluster_to_delete:
                        with st.spinner(f"Deleting cluster `{cluster_to_delete}`..."):
                            try:
                                utils.delete_cluster(
                                    hcp_url, hcp_api_access_key, st.session_state.hcp_project_id, cluster_to_delete
                                )
                                # Refresh the list after successful deletion
                                st.session_state.clusters_df = utils.get_clusters(
                                    hcp_url, hcp_api_access_key, st.session_state.hcp_project_id
                                )
                                st.session_state.delete_mode = False # Exit delete mode
                            except Exception as e:
                                st.error(f"Failed to delete cluster. Error: {e}")
                                st.session_state.clusters_df = pd.DataFrame()
                    else:
                        st.warning("Please enter a Cluster ID.")

        # Create Cluster form logic
        if st.session_state.create_mode:
            st.subheader("Create a New Cluster")
            cluster_type = st.selectbox(
                "Select Cluster Type:",
                ["Single Node HCP Database Cluster", "1 Data Group PGD (Dist HA) Cluster", "2 Datagroup PGD (Dist HA) Cluster"]
            )
            
            if cluster_type == "Single Node HCP Database Cluster":
                with st.form("create_single_node_cluster"):
                    st.write("Enter parameters for the single node cluster:")
                    
                    cluster_name = st.text_input("Cluster Name", help="e.g., test-singlenode-api")
                    password = st.text_input("Password", type="password", help="Password must be at least 12 characters long.")
                    
                    st.write("Resource Request:")
                    memory = st.text_input("Memory", value="1Gi")
                    cpu = st.number_input("CPU Cores", min_value=0, value=1)

                    st.write("Storage Configuration:")
                    primary_storage_size = st.number_input("Primary Storage Size (GB)", min_value=1, value=10)
                    wal_storage_size = st.number_input("WAL Storage Size (GB)", min_value=1, value=10)
                    
                    backup_retention_period = st.text_input("Backup Retention Period", value="1d")
                    
                    submit_create = st.form_submit_button("Create Cluster")
                    cancel_create = st.form_submit_button("Cancel")

                    if submit_create:
                        if cluster_name and password:
                            with st.spinner(f"Creating cluster `{cluster_name}`..."):
                                try:
                                    utils.create_single_node(
                                        hcp_url=hcp_url,
                                        hcp_api_access_key=hcp_api_access_key,
                                        project_id=st.session_state.hcp_project_id,
                                        cluster_name=cluster_name,
                                        password=password,
                                        memory=memory,
                                        cpu=cpu,
                                        primary_storage_size=primary_storage_size,
                                        wal_storage_size=wal_storage_size,
                                        backup_retention_period=backup_retention_period,
                                    )
                                    st.success(f"Cluster `{cluster_name}` created successfully!")
                                    st.session_state.create_mode = False # Exit create mode
                                    # Refresh the cluster list after creation
                                    st.session_state.clusters_df = utils.get_clusters(
                                        hcp_url, hcp_api_access_key, st.session_state.hcp_project_id
                                    )
                                except Exception as e:
                                    st.error(f"Failed to create cluster. Error: {e}")
                        else:
                            st.warning("Please enter a Cluster Name and Password.")
                    
                    if cancel_create:
                        st.session_state.create_mode = False
            else:
                st.info("This cluster type is not yet implemented. Please select 'Single Node HCP Database Cluster'.")

    else:
        st.info("Please enter a Project ID in the sidebar and click 'List Clusters'.")