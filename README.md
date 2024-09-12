# GitHub Semantic Kernel Demo

This repository demonstrates the usage of a semantic kernel for GitHub operations. The project leverages various APIs and tools to interact with GitHub and process data. 

## Table of Contents

- [Setup](#setup)
- [Usage](#usage)
- [Files](#files)
- [Kernel Functions](#kernel-functions)
- [Docker Instructions](#docker-instructions)
- [License](#license)

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/KostaMalsev/github-semantic-kernel-demo.git
    cd github-semantic-kernel-demo
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file based on the `.env.example`:
    ```bash
    cp .env.example .env
    ```

    Update the `.env` file with your configurations.

4. Add your API keys in the `api-key.txt` and `git-api-key.txt` files.

## Usage

- Run the application:
    ```bash
    python app.py
    ```

## Files

- `.env`: Environment configuration file.
- `.env.example`: Example environment configuration file.
- `.github/workflows/run-tests.yml`: GitHub Actions workflow for running tests.
- `.gitignore`: Specifies files and directories to be ignored by git.
- `Dockerfile`: Dockerfile for building the project.
- `README.md`: This readme file.
- `api-key.txt`: File to store API keys.
- `app.py`: Main application file.
- `docker-compose.yml`: Docker Compose configuration file.
- `fetchurl.py`: Script to fetch URLs.
- `gen-api-key.txt`: File to store generated API keys.
- `git-api-key.txt`: File to store GitHub API key.
- `github_api/__init__.py`: Initialize GitHub API module.
- `github_api/actions.py`: Handles GitHub Actions API.
- `github_api/auth.py`: Handles GitHub authentication.
- `github_api/files.py`: Handles file operations with GitHub.
- `github_api/utils.py`: Utility functions for GitHub API.
- `requirements.txt`: Python package requirements.
- `static/`: Directory to store static files.
  - `fixer.png`: Example image file.
  - `webclient.html`: Example web client file.
- `tests/`: Directory for test files.
  - `test_fetchurl.py`: Test suite for `fetchurl.py`.
  - `test_gitapi.py`: Test suite for `gitapi.py`.
  - `test_main.py`: Test suite for main application.

## Kernel Functions

Implemented in `app.py` via `GithubPlugin`:

1. **GitHub Operations**
   - `github_list_files`: List files in a GitHub repo directory.
   - `github_create_file`: Create a new file in GitHub repo.
   - `github_push`: Push file to GitHub repo.
   - `github_get`: Get file from GitHub repo.
   - `github_get_actions_results`: Get GitHub Actions results.
   - `github_create_directory`: Create a new empty directory in GitHub repo.
   - `create_github_action`: Create a new GitHub Action workflow.
   - `update_github_action`: Update an existing GitHub Action workflow.
   - `get_readme_from_github`: Get existing README from repo.
   - `update_readme_on_github`: Update existing README in repo.
   - `create_readme_file`: Create a new README in the repo.

2. **Fetch Operations**
   - `github_get_html_content_from_url`: Get HTML content from URL.
   - `github_get_text_content_from_url`: Get text content from URL.
   - `extract_image_urls`: Get image URLs from URL.

3. **Authentication**
   - `check_credentials_to_github`: Check credentials to GitHub.

## Docker Instructions

1. Build the Docker image:
    ```bash
    docker build -t github-semantic-kernel-demo .
    ```

2. Run the Docker container:
    ```bash
    docker run -d -p 5000:5000 --env-file .env github-semantic-kernel-demo
    ```

3. Alternatively, use Docker Compose to build and run the project:
    ```bash
    docker-compose up --build
    ```

### Docker Compose Details

The project uses the `docker-compose.yml` configuration to set up the application.

- **Service:** `repofixer`
  - **Build Context:** Current directory (`.`).
  - **Dockerfile:** `Dockerfile` in the current directory.
  - **Image:** `kostyamalsev/repofixer:latest` (for ARM architecture).
  - **Command:** Runs `uvicorn app:app --host 0.0.0.0 --port 8000 --reload` inside the container.
  - **Environment Variables:**
    - `GLOBAL_LLM_SERVICE=AzureOpenAI`
    - `AZURE_OPENAI_ENDPOINT=https://ai-kostyamalsevai4154623923737068.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview`
    - `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o`
  - **Ports:**
    - `8000:8000`
  - **Secrets:**
    - `AZURE_OPENAI_API_KEY` (from `./gen-api-key.txt`)
    - `GITHUB_TOKEN_GEN_AI` (from `./git-api-key.txt`)

## License

This project is licensed under the MIT License.
