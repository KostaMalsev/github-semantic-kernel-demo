import os
from typing import Annotated
from dotenv import load_dotenv
import asyncio
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import (
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.kernel import Kernel

from fetchurl import fetch_text_content_from_url

# Load environment variables from .env file
load_dotenv()

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


class PromptRequest(BaseModel):
    prompt: str

#Definition of the custom fetch plugin:
class FetchPlugin:
    """Plugin provides fetch of content from url."""

    @kernel_function(name="get_content_from_url", description="Get the content from url")
    def get_content_from_url(self, url: Annotated[str, "The input url"]) -> Annotated[str, "The output is a string"]:
        return fetch_text_content_from_url(url)


# Global variable to store the kernel
kernel = None


# Read the secret from a secret file which were injected by docker-compose
def read_secret(secret_name):
    try:
        with open(f'/run/secrets/AZURE_OPENAI_API_KEY', 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        return None



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
    kernel.add_plugin(FetchPlugin(), plugin_name="fetchurl")

    return kernel


@app.on_event("startup")
async def startup_event():
    global kernel
    kernel = await setup_kernel()


#Endpoint for chat prompts:
@app.post("/demoprompt")
async def demo_prompt(request: PromptRequest):
    settings: OpenAIChatPromptExecutionSettings = kernel.get_prompt_execution_settings_from_service_id(
        service_id="function_calling"
    )
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto(filters={"included_plugins": ["fetchurl"]})

    result = await kernel.invoke_prompt(
        function_name="get_content_from_url",
        plugin_name="fetchurl",
        prompt=request.prompt,
        settings=settings,
    )
    
    return {"response": str(result)}



#Serving a simple chat webpage:

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API. Static files are served under /static"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
