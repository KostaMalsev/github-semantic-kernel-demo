import os
import datetime
from typing import Annotated,List
from dotenv import load_dotenv
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import (
    OpenAIChatPromptExecutionSettings,
)

#for auto selecting the functions:
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments



from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.kernel import Kernel

from gitapi import (github_get,
                    github_push,
                    get_readme_from_github,
                    github_get_actions_results,
                    update_readme_on_github,
                    create_readme_file
                    )

from fetchurl import get_content_from_url
from fetchurl import extract_image_urls





app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Read the secret from a secret file which were injected by docker-compose
def read_secret(secret_name):
    try:
        with open(f'/run/secrets/AZURE_OPENAI_API_KEY', 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        return None

class PromptRequest(BaseModel):
    prompt: str

class Conversation(BaseModel):
    history: List[dict] = []


#Definition of the custom fetch plugin:
class GithubPlugin:
    """Plugin provides github api """

    @kernel_function(name="github_pushf", description="Push file from github repo")
    def github_pushf(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_path: Annotated[str, "file path"],
                        file_content: Annotated[str, "full fixed file content"],
                    ) -> Annotated[str, "The output is a string"]:
        comment  = f"AI generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return github_push(repo_owner,repo_name,file_path,comment,file_content,os.getenv('GITHUB_TOKEN_GEN_AI'))

    
    @kernel_function(name="github_getf", description="Get file from github repo")
    def github_getf(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_path: Annotated[str, "file path"],
                    ) -> Annotated[str, "The output is a string"]:
        
        return github_get(repo_owner,repo_name,file_path,"main",os.getenv('GITHUB_TOKEN_GEN_AI'))
    
    
    @kernel_function(name="github_get_actions_resultsf", description="Get github actions results")
    def github_get_actions_resultsf(self, 
                        repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                    ) -> Annotated[str, "The output is a string"]:
        return github_get_actions_results(repo_owner,repo_name,os.getenv('GITHUB_TOKEN_GEN_AI'))
    
    
    @kernel_function(name="get_readme_from_githubf", description="Get existing Readme from repo, use only for Readme files")
    def get_readme_from_githubf(self, 
                       repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                    ) -> Annotated[str, "The output is a string"]:
            
            return get_readme_from_github(repo_owner, repo_name, os.getenv('GITHUB_TOKEN_GEN_AI'))
    
    
    @kernel_function(name="update_readme_on_githubf", description="Update existing Readme at repo, use only for Readme files")
    def update_readme_on_githubf(self, 
                       repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_content: Annotated[str, "full readme file content"],
                    ) -> Annotated[str, "The output is a string"]:
            
            return update_readme_on_github(repo_owner, 
                                           repo_name, 
                                           os.getenv('GITHUB_TOKEN_GEN_AI'), 
                                           file_content)

    @kernel_function(name="create_readme_filef", description="Create new Readme in repo, use only for Readme files")
    def create_readme_filef(self, 
                       repo_owner: Annotated[str, "repository owner"],
                        repo_name: Annotated[str, "repository name"],
                        file_content: Annotated[str, "full readme file content"],
                    ) -> Annotated[str, "The output is a string"]:
            
            return update_readme_on_github(repo_owner, 
                                           repo_name,
                                           file_content, 
                                           os.getenv('GITHUB_TOKEN_GEN_AI')
                                           )
    
    @kernel_function(name="github_get_html_content_from_urlf", description="Get html content from url")
    def github_get_html_content_from_urlf(self, url: Annotated[str, "The input url"]) -> Annotated[str, "The output is a string"]:
        return get_content_from_url(url,'html',1000)
    
    @kernel_function(name="github_get_text_content_from_urlf", description="Get text only content from url")
    def github_get_text_content_from_urlf(self, url: Annotated[str, "The input url"]) -> Annotated[str, "The output is a string"]:
        return get_content_from_url(url,'text',1000)
    
    @kernel_function(name="extract_image_urlsf", description="Get image only content from url")
    def extract_image_urlsf(self, url: Annotated[str, "The input url"]) -> Annotated[str, "The output is a list of url strings"]:
        return extract_image_urls(url)



# Global variable to store the kernel
kernel = None

#To store history:
conversations = {} 



async def setup_kernel():
    kernel = Kernel()

    # Check if we're using Azure OpenAI
    if os.getenv('GLOBAL_LLM_SERVICE') != "AzureOpenAI":
        raise ValueError("This script is configured to use Azure OpenAI. Please check your .env file.")

    #Check if the secret key is defined in environment variable (for dev perposes)
    if 'AZURE_OPENAI_API_KEY' in os.environ:
        azure_api_key= os.getenv('AZURE_OPENAI_API_KEY')
    else:
        #get the key from the secret file:
        azure_api_key = read_secret('AZURE_OPENAI_API_KEY')

    service_id = "function_calling"
    
    # Azure OpenAI setup
    ai_service = AzureChatCompletion(
        service_id=service_id,
        deployment_name=os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'),
        endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
        api_key= azure_api_key
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
    # Load environment variables from .env file
    load_dotenv()

    kernel = await setup_kernel()


#Endpoint for chat prompts:
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

    # Enable automatic function calling
    execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
    execution_settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(auto_invoke=True, filters={})

    result = (await chat_completion.get_chat_message_contents(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
            arguments=KernelArguments(),
        ))[0]
   
    # Add the message from the agent to the chat history
    conversation.history.append({"role": "user", "content": request.prompt})
    conversation.history.append({"role": "assistant", "content": str(result)})

    return {"response": str(result)}




#Serving a simple chat webpage:
@app.get("/")
async def read_root():
    return {"message": "Welcome to the API. Static files are served under /static"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
