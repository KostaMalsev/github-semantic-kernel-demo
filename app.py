import os
import datetime
from typing import Annotated, List
from dotenv import load_dotenv
from fastapi import (FastAPI)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.kernel import Kernel

# Import the refactored GitHub API
from github_api import GitHubFile, GitHubActions

from fetchurl import (get_content_from_url, extract_image_urls)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read the secret from a secret file which were injected by docker-compose
def read_secret(secret_name):
    try:
        with open(f'/run/secrets/{secret_name}', 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        return None

class PromptRequest(BaseModel):
    prompt: str

class Conversation(BaseModel):
    history: List[dict] = []

class GithubPlugin:
    """Plugin provides github api """
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN_GEN_AI')
        self.github_file = GitHubFile('', '')  # Initialize with empty strings
        self.github_actions = GitHubActions('', '')  # Initialize with empty strings

    
    @kernel_function(name="github_list_files", description="List files in a github repo directory")
    def github_list_files(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        directory_path: Annotated[str, "directory path (optional)"] = "",
                    ) -> Annotated[str, "The output is a string containing a list of files"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        files = self.github_file.list_files(directory_path)
        return "\n".join(files)
    
    
    @kernel_function(name="github_create_file", description="Create a new file in github repo")
    def github_create_file(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_path: Annotated[str, "file path"],
                        file_content: Annotated[str, "file content"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        commit_message = f"AI generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self.github_file.create_or_update_file(file_path, file_content, commit_message)

    @kernel_function(name="github_push", description="Push file to github repo")
    def github_push(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_path: Annotated[str, "file path"],
                        file_content: Annotated[str, "full fixed file content"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        commit_message = f"AI updated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self.github_file.create_or_update_file(file_path, file_content, commit_message)

    @kernel_function(name="github_get", description="Get file from github repo")
    def github_get(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_path: Annotated[str, "file path"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        return self.github_file.get_file(file_path)["content"]

    @kernel_function(name="github_get_actions_results", description="Get github actions results")
    def github_get_actions_results(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_actions = GitHubActions(repo_owner, repo_name)
        return self.github_actions.get_actions_results()

    @kernel_function(name="github_create_directory", description="Create a new empty directory in github repo")
    def github_create_directory(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        directory_path: Annotated[str, "directory path"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        return self.github_file.create_directory(directory_path)

    @kernel_function(name="create_github_action", description="Create a new GitHub Action workflow")
    def create_github_action(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        workflow_name: Annotated[str, "workflow file name"],
                        workflow_content: Annotated[str, "content of the workflow file"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_actions = GitHubActions(repo_owner, repo_name)
        return self.github_actions.create_or_update_workflow(workflow_name, workflow_content)

    @kernel_function(name="github_update_action", description="Update an existing GitHub Action workflow")
    def github_update_action(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        workflow_name: Annotated[str, "workflow file name"],
                        new_content: Annotated[str, "new content of the workflow file"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_actions = GitHubActions(repo_owner, repo_name)
        return self.github_actions.create_or_update_workflow(workflow_name, new_content)

    @kernel_function(name="get_readme_from_github", description="Get existing Readme from repo, use only for Readme files")
    def get_readme_from_github(self, 
                       repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        return self.github_file.get_file('README.md')

    @kernel_function(name="update_readme_on_github", description="Update existing Readme at repo, use only for Readme files")
    def update_readme_on_github(self, 
                       repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_content: Annotated[str, "full readme file content"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        return self.github_file.create_or_update_file('README.md', file_content, "Update README.md")

    @kernel_function(name="github_create_readme_file", description="Create new Readme in repo, use only for Readme files")
    def github_create_readme_file(self, 
                       repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_content: Annotated[str, "full readme file content"],
                    ) -> Annotated[str, "The output is a string"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        return self.github_file.create_or_update_file('README.md', file_content, "Create README.md")
    
    @kernel_function(name="github_rename_file", description="Rename a file in github repo")
    def github_rename_file(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        old_path: Annotated[str, "current file path"],
                        new_path: Annotated[str, "new file path"],
                    ) -> Annotated[str, "The output is a string message indicating success or describing an error"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        return self.github_file.rename_file(old_path, new_path)

    @kernel_function(name="github_rename_directory", description="Rename a directory in github repo")
    def github_rename_directory(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        old_path: Annotated[str, "current directory path"],
                        new_path: Annotated[str, "new directory path"],
                    ) -> Annotated[str, "The output is a string message indicating success or describing an error"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        return self.github_file.rename_directory(old_path, new_path)
    
    @kernel_function(name="github_delete_file", description="Delete a file from github repo")
    def github_delete_file(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_path: Annotated[str, "path of the file to delete"],
                    ) -> Annotated[str, "The output is a string message indicating success or describing an error"]:
        self.github_file = GitHubFile(repo_owner, repo_name)
        try:
            # First, get the file to retrieve its SHA
            file_info = self.github_file.get_file(file_path)
            
            # Now delete the file
            commit_message = f"Delete file {file_path}"
            self.github_file.delete_file(file_path, commit_message, file_info['sha'])
            
            return f"Successfully deleted file: {file_path}"
        except Exception as e:
            return f"Error deleting file {file_path}: {str(e)}"
        
    # The fetch utility functions:
    @kernel_function(name="github_get_html_content_from_url", description="Get html content from url")
    def github_get_html_content_from_url(self, url: Annotated[str, "The input url"]) -> Annotated[str, "The output is a string"]:
        return get_content_from_url(url, 'html', 1000)
    
    @kernel_function(name="github_get_text_content_from_url", description="Get text only content from url")
    def github_get_text_content_from_url(self, url: Annotated[str, "The input url"]) -> Annotated[str, "The output is a string"]:
        return get_content_from_url(url, 'text', 1000)
    
    @kernel_function(name="extract_image_urls", description="Get image only content from url")
    def extract_image_urls(self, url: Annotated[str, "The input url"]) -> Annotated[str, "The output is a list of url strings"]:
        return extract_image_urls(url)
    
    @kernel_function(name="check_credentials_to_github", description="Check credentials to github")
    def check_credentials_to_github(self) -> Annotated[str, "The output is result"]:
        if not self.github_token:
            return "no credentials to github"
        else:
            return "have credentials to github"
    
    @kernel_function(name="github_list_repositories", description="List repositories for a GitHub user or organization")
    def github_list_repositories(self, 
                                 owner: Annotated[str, "GitHub username or organization name"],
                                ) -> Annotated[str, "A formatted string containing information about all repositories"]:
        self.github_file = GitHubFile(owner, '')
        return self.github_file.list_repositories()

# Global variable to store the kernel
kernel = None

# To store history:
conversations = {}

async def setup_kernel():
    kernel = Kernel()
    
    def get_env_var(var_name):
        value = os.getenv(var_name)
        if not value:
            load_dotenv()
            value = os.getenv(var_name)
        if not value:
            value = read_secret(var_name)
        return value

    # Get API keys
    azure_api_key = get_env_var('AZURE_OPENAI_API_KEY')
    github_api_key = get_env_var('GITHUB_TOKEN_GEN_AI')
    
    azure_deployment_name = get_env_var('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME')
    azure_endpoint = get_env_var('AZURE_OPENAI_ENDPOINT')
    azure_global_llm_service = get_env_var('GLOBAL_LLM_SERVICE')
    

    # Set environment variables
    if azure_api_key:
        os.environ['AZURE_OPENAI_API_KEY'] = azure_api_key
    if github_api_key:
        os.environ['GITHUB_TOKEN_GEN_AI'] = github_api_key
        
    print(azure_deployment_name)

    # Check if we have the necessary API key
    if not azure_api_key:
        raise ValueError("AZURE_OPENAI_API_KEY is not set. Please check your environment variables, .env file, or secret files.")
    
    if not github_api_key:
        raise ValueError("GITHUB_TOKEN_GEN_AI is not set. Please check your environment variables, .env file, or secret files.")

    if not azure_endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not set. Please check your environment variables, .env file, or secret files.")

    if azure_global_llm_service != "AzureOpenAI":
        raise ValueError("This script is configured to use Azure OpenAI. Please check your .env file: GLOBAL_LLM_SERVICE")    
    
    
    service_id = "function_calling"
    
    ai_service = AzureChatCompletion(
        service_id=service_id,
        deployment_name=azure_deployment_name,
        endpoint=azure_endpoint,
        api_key=azure_api_key
    )
    
    kernel.add_service(ai_service)
    kernel.add_plugin(GithubPlugin(), plugin_name="githubapi")

    return kernel

def get_or_create_conversation(conversation_id: str):
    if conversation_id not in conversations:
        conversations[conversation_id] = Conversation()
    return conversations[conversation_id]

@app.on_event("startup")
async def startup_event():
    global kernel
    kernel = await setup_kernel()

@app.post("/demoprompt/{conversation_id}")
async def demo_prompt(conversation_id: str, request: PromptRequest):
    chat_completion : AzureChatCompletion = kernel.get_service(type=ChatCompletionClientBase)
    conversation = get_or_create_conversation(conversation_id)
    history = ChatHistory()

    for message in conversation.history:
        if message['role'] == 'user':
            history.add_user_message(message['content'])
        elif message['role'] == 'assistant':
            history.add_assistant_message(message['content'])

    history.add_user_message(request.prompt)

    execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=True, filters={})
    
    result = (await chat_completion.get_chat_message_contents(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
            arguments=KernelArguments(),
        ))[0]
   
    conversation.history.append({"role": "user", "content": request.prompt})
    conversation.history.append({"role": "assistant", "content": str(result)})

    return {"response": str(result)}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API. Static files are served under /static"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)