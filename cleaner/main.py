from typing import List, Union
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from cleanup import orchestrator


class RepositoriesRequest(BaseModel):
    repositories: Union[str, List[str]] = Field(...)


app = FastAPI(title="Remove untagged container images")


@app.post("/")
async def clean_request(request: RepositoriesRequest):
    orchestrator(request.repositories)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
