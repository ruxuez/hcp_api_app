import requests
import pandas as pd
import streamlit as st
import json

def get_current_user_access_key(HCP_URL, HCP_API_ACCESS_KEY):
    api_url = f"{HCP_URL}/api/v1/auth/access-keys"
    headers = {
        "Content-Type": "application/json",
        "x-access-key": HCP_API_ACCESS_KEY,
    }
    try:
        response = requests.get(api_url, headers=headers, verify=False)  # verify=False car ton curl utilise --insecure
        st.write("Below is the cURL command executed:")
        st.code(api_url, language="bash")
        if response.status_code == 200:
            data = response.json()
            # On accède à la liste des projets
            projects = data.get("data", [])
            # Construire un DataFrame
            df = pd.DataFrame(projects)
            st.success(f"Connected successfully to {HCP_URL}! Here is your current Access Key:")
            return df
        else:
            st.error(f"Erreur {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"Connection Error : {e}")

def get_projects(HCP_URL, HCP_API_ACCESS_KEY):
    api_url = f"{HCP_URL}/api/v1/projects"
    headers = {
        "Content-Type": "application/json",
        "x-access-key": HCP_API_ACCESS_KEY,
    }
    try:
        response = requests.get(api_url, headers=headers, verify=False)  # verify=False car ton curl utilise --insecure
        st.write("Below is the cURL command executed:")
        st.code(api_url, language="bash")
        if response.status_code == 200:
            data = response.json()
            # On accède à la liste des projets
            projects = data.get("data", [])

            # Transformer les tags en liste de tagName
            for p in projects:
                if p.get("tags"):
                    p["tags"] = [t["tagName"] for t in p["tags"]]
                else:
                    p["tags"] = []

            # Construire un DataFrame
            df = pd.DataFrame(projects)
            return df

        else:
            st.error(f"Erreur {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"Connection Error : {e}")
        raise Exception(f"API request failed: {e}")
    

def get_clusters(HCP_URL, HCP_API_ACCESS_KEY, HCP_PROJECT_ID):
    api_url = f"{HCP_URL}/api/v1/projects/{HCP_PROJECT_ID}/clusters"
    headers = {
        "Content-Type": "application/json",
        "x-access-key": HCP_API_ACCESS_KEY,
    }
    try:
        response = requests.get(api_url, headers=headers, verify=False)
        st.write("Below is the cURL command executed:")
        st.code(f"{api_url}", language="bash")
        
        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        data = response.json()
        clusters = data.get("data", [])
        
        # On extrait uniquement les champs voulus
        simplified = []
        for c in clusters:
            psr = c.get("psr", {})
            delete_time = psr.get("deleteTime")

            phase = "Deleted" if delete_time else psr.get("phase")

            simplified.append({
                "clusterId": c.get("clusterId"),
                "name": c.get("name"),
                "instances": psr.get("instances"),
                "phase": phase,
                "pgType": psr.get("pgType"),
                "majorVersion": psr.get("majorVersion"),
                "createdTime": psr.get("createTime"),
                "deletedTime": psr.get("deleteTime"),
            })

        df = pd.DataFrame(simplified)
        # Convert createdTime to datetime for proper sorting
        df["createdTime"] = pd.to_datetime(df["createdTime"])
        df = df.sort_values(by="createdTime", ascending=False)
        return df
        
    except requests.exceptions.HTTPError as e:
        # This block catches errors like 404 Not Found or 401 Unauthorized
        st.error(f"API Error ({e.response.status_code}): {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        # This block catches all other request errors (e.g., connection issues)
        st.error(f"Connection Error: {e}")
        raise


def delete_cluster(HCP_URL, HCP_API_ACCESS_KEY, HCP_PROJECT_ID, cluster_id):
    api_url = f"{HCP_URL}/api/v1/projects/{HCP_PROJECT_ID}/clusters/{cluster_id}"
    headers = {
        "Content-Type": "application/json",
        "x-access-key": HCP_API_ACCESS_KEY,
    }
    st.text("deleting cluster....")
    try:
        response = requests.delete(api_url, headers=headers, verify=False)  # verify=False car ton curl utilise --insecure
        st.write("Below is the cURL command executed:")
        st.code(api_url, language="bash")
        if response.status_code == 200 or response.status_code == 204:
                st.success(f"Cluster {cluster_id} deleted successfully!")
        else:
            st.error(f"Error deleting cluster: {response.status_code} {response.text}")

    except Exception as e:
        st.error(f"Connection Error: {e}")


def create_single_node(
    hcp_url,
    hcp_api_access_key,
    project_id,
    cluster_name,
    password,
    memory,
    cpu,
    primary_storage_size,
    wal_storage_size,
    backup_retention_period,
):
    """
    Constructs the JSON payload for a single-node cluster and
    makes the API call to create it.
    """
    payload = {
        "psr": {
            "clusterName": cluster_name,
            "password": password,
            "location_id": "managed-default-location",
            "clusterData": {
                "instances": 1,
                "resourceRequest": {
                    "request": {
                        "memory": memory,
                        "cpu": cpu
                    }
                },
                "storageConfiguration": {
                    "primaryStorage": {
                        "size": str(primary_storage_size),
                        "storageClass": "gp2"
                    },
                    "walStorage": {
                        "size": str(wal_storage_size),
                        "storageClass": "gp2"
                    }
                },
                "image": {
                    "url": "docker.enterprisedb.com/pgai-platform/postgresql:17.5-2508141944-full",
                    "digest": "sha256:b4c956ed3d95e05df1511dd4f562fcf22631f4b39996782f31ed3564d33a3ea5"
                },
                "backupRetentionPeriod": backup_retention_period,
                "backupSchedule": "0 20 4 * * *",
                "networkAccessType": "NetworkAccessTypePublic"
            }
        },
        "projectId": project_id
    }

    # Placeholder for the actual API call
    api_url = f"{hcp_url}/api/v1/projects/{project_id}/clusters"
    headers = {
        "Content-Type": "application/json",
        "x-access-key": hcp_api_access_key,
    }

    st.text(f"API URL: {api_url}")
    st.text(f"Payload: {json.dumps(payload, indent=2)}")

    # # Uncomment this block for a real API call
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating cluster: {e}")
        raise