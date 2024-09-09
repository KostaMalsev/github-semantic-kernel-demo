import base64
import requests
from .auth import get_github_token
from .utils import (encode_content, make_github_request)

class GitHubFile:
    def __init__(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.token = get_github_token()
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/vnd.github+json",
        }

    def get_file(self, file_path, branch="main"):
        url = f"{self.base_url}/{file_path}"
        params = {"ref": branch}
        response = make_github_request("GET", url, self._get_headers(), params)
        content = base64.b64decode(response['content']).decode('utf-8')
        sha = response['sha']
        return {
            "content": content,
            "sha": sha
        }

    def create_or_update_file(self, file_path, content, commit_message, branch="main"):
        url = f"{self.base_url}/{file_path}"
        data = {
            "message": commit_message,
            "content": encode_content(content),
            "branch": branch
        }

        try:
            existing_file = self.get_file(file_path, branch)
            data['sha'] = existing_file['sha']
            
        except requests.exceptions.HTTPError:
            pass  # File doesn't exist, creating new file

        return make_github_request("PUT", url, self._get_headers(), data)

    def create_directory(self, directory_path, branch="main"):
        return self.create_or_update_file(
            f"{directory_path}/.gitkeep",
            "",
            f"Create directory: {directory_path}",
            branch
        )
    
    def list_files(self, path="", branch="main"):
        base_url  = (f"{self.base_url}")
        url = f"{base_url[:-9]}/git/trees/{branch}?recursive=1"        

        response = make_github_request("GET", url, self._get_headers())
        
        all_files = []
        for item in response['tree']:
            if item['type'] == 'blob':  # 'blob' represents a file
                all_files.append(item['path'])
        
        if path:
            return [file for file in all_files if file.startswith(path)]
        return all_files