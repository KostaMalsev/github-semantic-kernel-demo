import requests
from .auth import get_github_token
from .utils import (make_github_request,encode_content)
import zipfile
import io
import os


class GitHubActions:
    def __init__(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.token = get_github_token()
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_actions_results(self, artifact_name="SummaryResult"):
        artifacts_url = f"{self.base_url}/actions/artifacts"
        artifacts = make_github_request("GET", artifacts_url, self._get_headers())["artifacts"]

        summary_artifact = next((a for a in artifacts if a["name"] == artifact_name), None)
        if not summary_artifact:
            raise ValueError(f"No artifact named '{artifact_name}' found.")

        download_url = summary_artifact["archive_download_url"]
        response = requests.get(download_url, headers=self._get_headers())
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall("temp_artifact")

        with open("temp_artifact/summary.md", "r") as f:
            content = f.read()

        os.remove("temp_artifact/summary.md")
        os.rmdir("temp_artifact")

        return content

    def create_or_update_workflow(self, workflow_name, workflow_content, branch="main"):
        file_path = f".github/workflows/{workflow_name}"
        url = f"{self.base_url}/contents/{file_path}"
        
        data = {
            "message": f"Update GitHub Action workflow: {workflow_name}",
            "content": encode_content(workflow_content),
            "branch": branch
        }

        try:
            existing_file = make_github_request("GET", url, self._get_headers(), {"ref": branch})
            data["sha"] = existing_file["sha"]
        except requests.exceptions.HTTPError:
            pass  # Workflow doesn't exist, creating new workflow

        return make_github_request("PUT", url, self._get_headers(), data)
