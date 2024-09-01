import requests
import base64
import json

#Implementation of github API





def github_push(repo_owner, repo_name, file_path, commit_message, file_content, github_token):
    
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

    if f"{github_token}" is  None:
        print(f"github push error: no token")
        return None


    # Headers for authentication and specifying API version
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.request("GET", url, headers=headers)

    data = response.json()

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
    else:
        print(f"Failed to push changes: {resp.status_code}, {resp.text}")






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

        # The content is base64 encoded, so we need to decode it
        file_content = base64.b64decode(content['content']).decode('utf-8')

        return file_content
    else:
        print(f"Failed to get file: {response.status_code}, {response.text}")
        return None



def github_get_actions_results(owner, repo, github_token):
    """
    Retrieve the latest GitHub Actions workflow runs for a repository.
    
    :param owner: GitHub username or organization name
    :param repo: Repository name
    :param github_token: GitHub Personal Access Token
    :return: List of recent workflow runs with their status
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/vnd.github+json",
        'Accept': 'application/vnd.github+json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    workflow_runs = data.get('workflow_runs', [])

    results = []
    for run in workflow_runs:
        results.append({
            'id': run['id'],
            'name': run['name'],
            'status': run['status'],
            'conclusion': run['conclusion'],
            'branch': run['head_branch'],
            'commit_message': run['head_commit']['message'] if run['head_commit'] else 'N/A',
            'url': run['html_url']
        })

    return results


