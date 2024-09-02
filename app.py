import os
import datetime
from typing import Annotated
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

from gitapi import github_get
from gitapi import github_push
from gitapi import github_get_actions_results

from fetchurl import get_content_from_url





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
        #comment  = print(f"AI generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
    

    @kernel_function(name="get_content_from_urlf", description="Get github actions results")
    def get_content_from_urlf(self, url: Annotated[str, "The input url"]) -> Annotated[str, "The output is a string"]:
        return get_content_from_url(url)




# Global variable to store the kernel
kernel = None



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





@app.on_event("startup")
async def startup_event():
    global kernel
    # Load environment variables from .env file
    load_dotenv()

    kernel = await setup_kernel()


#Endpoint for chat prompts:
@app.post("/demoprompt")
async def demo_prompt(request: PromptRequest):

    chat_completion : AzureChatCompletion = kernel.get_service(type=ChatCompletionClientBase)

    history = ChatHistory()
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
    history.add_message(result)

    return {"response": str(result)}




#Serving a simple chat webpage:

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API. Static files are served under /static"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
