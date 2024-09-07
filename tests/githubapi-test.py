import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions from your file
from gitapi import (
    github_push,
    github_get,
    github_create_file,
    github_get_actions_results,
    get_readme_from_github,
    update_readme_on_github,
    create_readme_file,
    github_create_directory,
    create_github_action,
    update_github_action
)

class TestGitHubFunctions(unittest.TestCase):

    def setUp(self):
        # Load environment variables from .env file
        load_dotenv()
        self.repo_owner = "KostaMalsev"
        self.repo_name = "https://github.com/KostaMalsev/demo-repo-actions"
        self.file_path = "test_file.txt"
        self.github_token = os.getenv('GITHUB_TOKEN_GEN_AI')

    @patch('requests.put')
    def test_github_create_directory(self, mock_put):
        mock_put.return_value.status_code = 201
        mock_put.return_value.json.return_value = {"content": {"name": "new_directory"}}

        result = github_create_directory(self.repo_owner, self.repo_name, "new_directory", self.github_token)
        self.assertIsNotNone(result)
        self.assertEqual(result["content"]["name"], "new_directory")

    @patch('requests.put')
    def test_create_github_action(self, mock_put):
        mock_put.return_value.status_code = 201
        mock_put.return_value.json.return_value = {"content": {"name": "new_workflow.yml"}}

        result = create_github_action(self.repo_owner, self.repo_name, "new_workflow.yml", self.github_token, "workflow content")
        self.assertIsNotNone(result)
        self.assertEqual(result["content"]["name"], "new_workflow.yml")

    @patch('requests.get')
    @patch('requests.put')
    def test_update_github_action(self, mock_put, mock_get):
        mock_get.return_value.json.return_value = {"sha": "existing_sha"}
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {"content": {"name": "updated_workflow.yml"}}

        result = update_github_action(self.repo_owner, self.repo_name, "updated_workflow.yml", "new workflow content", self.github_token)
        self.assertIsNotNone(result)
        self.assertEqual(result["content"]["name"], "updated_workflow.yml")

if __name__ == '__main__':
    unittest.main()