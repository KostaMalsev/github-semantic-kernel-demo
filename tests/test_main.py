import asyncio
import pytest
from fastapi.testclient import TestClient
from app import app, setup_kernel, PromptRequest

client = TestClient(app)

@pytest.mark.asyncio
async def test_demo_prompt():
    await setup_kernel()
    conversation_id = "test_convo"
    request_prompt = {"prompt": "Test message"}

    response = client.post(f"/demoprompt/{conversation_id}", json=request_prompt)
    assert response.status_code == 200
    assert "response" in response.json()

@pytest.mark.asyncio
async def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API. Static files are served under /static"}

if __name__ == "__main__":
    asyncio.run(test_demo_prompt())
    asyncio.run(test_read_root())
