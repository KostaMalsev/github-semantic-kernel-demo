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
    

    def rename_file(self, old_path, new_path, commit_message=None, branch="main"):
        """
        Rename a file using the Git Trees API.
        """
        try:
            # Get the latest commit SHA
            branch_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/branches/{branch}"
            branch_data = make_github_request("GET", branch_url, self._get_headers())
            latest_commit_sha = branch_data['commit']['sha']

            # Get the tree of the latest commit
            tree_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{latest_commit_sha}?recursive=1"
            tree_data = make_github_request("GET", tree_url, self._get_headers())

            # Find the file to rename and prepare the new tree
            file_to_rename = None
            new_tree = []
            for item in tree_data['tree']:
                if item['path'] == old_path:
                    file_to_rename = item
                elif item['path'] != new_path:  # Exclude the new path if it already exists
                    new_tree.append(item)

            if file_to_rename is None:
                return f"Error: File {old_path} not found in the repository"

            # Add the renamed file to the new tree
            new_tree.append({
                "path": new_path,
                "mode": file_to_rename['mode'],
                "type": file_to_rename['type'],
                "sha": file_to_rename['sha']
            })

            # Create a new tree
            new_tree_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees"
            new_tree_data = {
                "base_tree": latest_commit_sha,
                "tree": new_tree
            }
            
            new_tree_response = make_github_request("POST", new_tree_url, self._get_headers(), new_tree_data)

            # Create a new commit
            new_commit_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/commits"
            new_commit_data = {
                "message": commit_message or f"Rename file from {old_path} to {new_path}",
                "tree": new_tree_response['sha'],
                "parents": [latest_commit_sha]
            }
            
            new_commit_response = make_github_request("POST", new_commit_url, self._get_headers(), new_commit_data)

            # Update the reference
            ref_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch}"
            ref_data = {
                "sha": new_commit_response['sha']
            }
            make_github_request("PATCH", ref_url, self._get_headers(), ref_data)

            return f"Successfully renamed file from {old_path} to {new_path}"

        except Exception as e:
            return f"An error occurred while renaming the file: {str(e)}"
        
    
    
    
    def rename_directory(self, old_path, new_path, commit_message=None, branch="main"):
        """
        Rename a directory using the Git Trees API.

        """
        try:
            
            # Ensure old_path and new_path don't have trailing slashes
            old_path = old_path.rstrip('/')
            new_path = new_path.rstrip('/')

            # Get the latest commit SHA
            branch_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/branches/{branch}"
            branch_data = make_github_request("GET", branch_url, self._get_headers())
            latest_commit_sha = branch_data['commit']['sha']

            # Get the tree of the latest commit
            tree_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{latest_commit_sha}?recursive=1"
            tree_data = make_github_request("GET", tree_url, self._get_headers())

            # Prepare the new tree
            new_tree = []
            directory_renamed = False
            for item in tree_data['tree']:
                if item['path'].startswith(f"{old_path}/"):
                    directory_renamed = True
                    new_item_path = item['path'].replace(old_path, new_path, 1)
                    new_tree.append({
                        "path": new_item_path,
                        "mode": item['mode'],
                        "type": item['type'],
                        "sha": item['sha']
                    })
                elif item['path'] != old_path and not item['path'].startswith(f"{new_path}/"):
                    new_tree.append(item)

            if not directory_renamed:
                return f"Error: Directory {old_path} not found or is empty"

            # Create a new tree
            new_tree_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees"
            new_tree_data = {
                "base_tree": latest_commit_sha,
                "tree": new_tree
            }
            new_tree_response = make_github_request("POST", new_tree_url, self._get_headers(), new_tree_data)

            # Create a new commit
            new_commit_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/commits"
            new_commit_data = {
                "message": commit_message or f"Rename directory from {old_path} to {new_path}",
                "tree": new_tree_response['sha'],
                "parents": [latest_commit_sha]
            }
            new_commit_response = make_github_request("POST", new_commit_url, self._get_headers(), new_commit_data)

            # Update the reference
            ref_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch}"
            ref_data = {
                "sha": new_commit_response['sha']
            }
            make_github_request("PATCH", ref_url, self._get_headers(), ref_data)

            return f"Successfully renamed directory from {old_path} to {new_path}"

        except Exception as e:
            return f"An error occurred while renaming the directory: {str(e)}"
        
        
    def delete_file(self, file_path, commit_message, sha):
        url = f"{self.base_url}/{file_path}"
        data = {
            "message": commit_message,
            "sha": sha
        }
        response = requests.delete(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    
    
    def list_repositories(self, per_page=100):
        """
        List repositories for the owner specified in the GitHubFile instance.

        Args:
        per_page (int): Number of repositories to return per page (max 100).

        Returns:
        str: A formatted string containing information about all repositories.
        """
        base_url = f"https://api.github.com/users/{self.owner}/repos"
        
        params = {
            "per_page": per_page,
            "sort": "updated",
            "direction": "desc"
        }

        all_repos = []
        page = 1

        while True:
            params["page"] = page
            response = make_github_request("GET", base_url, self._get_headers(), params)
            
            repos = response
            if not repos:
                break

            all_repos.extend(repos)
            page += 1

            if len(repos) < per_page:
                break

        # Format the results as a string
        result = f"Repositories for {self.owner}:\n"
        for repo in all_repos:
            result += f"- {repo['name']}\n"
            result += f"  Description: {repo['description'] or 'No description'}\n"
            result += f"  URL: {repo['html_url']}\n"
            result += f"  Stars: {repo['stargazers_count']}\n"
            result += f"  Forks: {repo['forks_count']}\n"
            result += f"  Last updated: {repo['updated_at']}\n\n"

        return result   
    