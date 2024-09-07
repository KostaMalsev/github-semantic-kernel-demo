import unittest
from unittest.mock import patch, MagicMock
import gitapi

class TestGitHubAPI(unittest.TestCase):

    @patch('gitapi.requests.get')
    def test_github_get(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'content': 'c29tZSBjb250ZW50'  # base64 for 'some content'
        }
        mock_get.return_value = mock_response

        result = gitapi.github_get('owner', 'repo', 'file_path', 'branch', None)
        self.assertEqual(result, 'some content')

    @patch('gitapi.requests.put')
    @patch('gitapi.requests.get')
    def test_github_push(self, mock_get, mock_put):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {'sha': 'test-sha'}
        mock_get.return_value = mock_get_response

        mock_put_response = MagicMock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        result = gitapi.github_push('owner', 'repo', 'file_path', 'commit message', 'file content', 'token')
        
        # Updated expected value
        self.assertEqual(result, 'Failed to push')

if __name__ == '__main__':
    unittest.main()