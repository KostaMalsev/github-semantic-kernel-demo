import requests
import base64
import json
import re
import zipfile
import os
import io

#Implementation of github API





def github_push(repo_owner, repo_name, file_path, commit_message, file_content, github_token):
    
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

    if f"{github_token}" is  None:
        print(f"github push error: no token")
        return "Failed to push, no Authentication token"


    # Headers for authentication and specifying API version
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.request("GET", url, headers=headers)

    data = response.json()

    
    if 'sha' in data:
            sha = data['sha']
    else:
        print("Error: Unable to retrieve SHA of existing README.md")
        print(f"Available keys in response: {', '.join(data.keys())}")
        return "Failed to push"

    sha = data['sha']

    # Prepare the file content (must be base64 encoded)

    text = base64.b64encode(file_content.encode("utf-8"))

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/vnd.github+json",
        'Accept': 'application/vnd.github+json'
    }

    data = {
        "message": commit_message,
        "content": text.decode("utf-8"),
        "sha": sha
    }

    resp = requests.put(url, headers=headers, json=data)

    if resp.status_code == 200 or resp.status_code == 201:
        print(f"Successfully pushed changes to {file_path}")
        return f"Successfully pushed changes to {file_path}"
    else:
        print(f"Failed to push changes: {resp.status_code}, {resp.text}")
        return f"Failed to push changes: {resp.status_code}, {resp.text}" 






def github_get(repo_owner, repo_name, file_path, branch, github_token):
    
    # GitHub API endpoint
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

    # Parameters for the GET request
    params = {
        "ref": branch  # Specify the branch
    }

    # Headers for authentication and specifying API version
    headers = {
        "Content-Type": "application/vnd.github+json",
        'Accept': 'application/vnd.github+json'
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    # Make the GET request
    response = requests.get(api_url, params=params, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        content = response.json()
        if 'content' not in content:
            print("Error: 'content' field is missing.")
            return "Failed to get the file"
        else:
            file_content = base64.b64decode(content['content']).decode('utf-8')



        # The content is base64 encoded, so we need to decode it
        file_content = base64.b64decode(content['content']).decode('utf-8')

        return file_content
    else:
        print(f"Failed to get file: {response.status_code}, {response.text}")
        return f"Failed to get file: {response.status_code}, {response.text}"





def github_get_actions_results(owner, repo, github_token):
    
    # Get list of artifacts
    artifacts_url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/vnd.github+json",
        'Accept': 'application/vnd.github+json'
    }
    response = requests.get(artifacts_url, headers=headers)
    response.raise_for_status()
    
    artifacts = response.json()["artifacts"]

    artifact_name = "SummaryResult"
    
    # Find the "Summary results" artifact
    summary_artifact = next((a for a in artifacts if a["name"] == artifact_name), None)
    
    if not summary_artifact:
        print(f"No artifact named '{artifact_name}' found.")
        return f"Failed to get the artifact, '{artifact_name}' not found"
    
    # Download the artifact
    download_url = summary_artifact["archive_download_url"]
    response = requests.get(download_url, headers=headers)
    response.raise_for_status()
    
    # Extract the zip file
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall("temp_artifact")
    
    # Read the content of summary.md
    with open("temp_artifact/summary.md", "r") as f:
        content = f.read()
    
    # Clean up the temporary directory
    os.remove("temp_artifact/summary.md")
    os.rmdir("temp_artifact")
    
    return content
    


def get_readme_from_github(owner, repo, github_token):
    """
    Fetches the README.md file from a GitHub repository using the GitHub API.

    """

    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/vnd.github+json",
        'Accept': 'application/vnd.github+json'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content = response.json()["content"]
        decoded_content = base64.b64decode(content).decode("utf-8")
        return decoded_content
    else:
        return f"Failed to fetch README: {response.status_code}, {response.text}"




def update_readme_on_github(owner, repo, github_token, new_content):
    """
    Updates the README.md file in a GitHub repository using the GitHub API.
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {github_token}"
    }

    # First, get the current README to obtain its SHA
    current_readme = get_readme_from_github(owner, repo, github_token)

    # Prepare the update payload
    payload = {
        "message": "Update README.md",
        "content": base64.b64encode(new_content.encode()).decode(),
        "sha": current_readme["sha"]
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("README.md updated successfully")
        return "Successfully updated the readme"
    else:
        print(f"Failed to update README: {response.status_code}, {response.text}")
        return f"Failed to update readme: {response.status_code}, {response.text}"



def create_readme_file(repo_owner, repo_name, github_token, content):
    """
    Create a README.md file in the specified GitHub repository using the GitHub API.
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/README.md"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "message": "Create README.md",
        "content": content.encode("utf-8").b64encode().decode("utf-8")
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 201:
        print("README.md file created successfully.")
        return "Created successfully"
    else:
        print(f"Failed to create README.md file. Status code: {response.status_code}")
        print(f"Error message: {response.json().get('message', 'Unknown error')}")
        return f"Failed to create Readme: {response.status_code}"