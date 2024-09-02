# GitHub Semantic Kernel Demo

This repository demonstrates the usage of a semantic kernel for GitHub operations. The project leverages various APIs and tools to interact with GitHub and process data. 

## Table of Contents

- [Setup](#setup)
- [Usage](#usage)
- [Files](#files)
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
- `.gitignore`: Specifies files and directories to be ignored by git.
- `Dockerfile`: Dockerfile for building the project.
- `Readme.md`: This readme file.
- `api-key.txt`: File to store API keys.
- `app.py`: Main application file.
- `docker-compose.yml`: Docker Compose configuration file.
- `fetchurl.py`: Script to fetch URLs.
- `git-api-key.txt`: File to store GitHub API key.
- `gitapi.py`: Script to interact with GitHub API.
- `requirements.txt`: Python package requirements.
- `static/`: Directory to store static files.

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

## License

This project is licensed under the MIT License.