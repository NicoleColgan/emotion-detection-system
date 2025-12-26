from fastapi import FastAPI, Query
from pydantic import BaseModel
# create api app
app = FastAPI()

@app.get("/items")
def health(limit: int = Query(10, gt=0), name: str | None = Query(None)):   
    # Note you need to provide the query types above
    # Query can validate with regex, max/min, gt/lt etc.
    # Query(default, constraint)
    # gt = must be greater than 0
    return {
        "limit": limit,
        "name": name
    }

# http://127.0.0.1:8000/items_without_Query?limit=3&name=%22me%22
@app.get("/items_without_Query")
def get_name(limit: int, name: str | None = None):
    # default for name makes it optional
    return {
        "limit": limit,
        "name": name
    }

class ItemPayload(BaseModel):
    # post needs to accept json in request body
    limit: int
    name: str | None = None

# curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d "{ \"limit\": 10, \"name\": \"nifole\"}
@app.post("/items")
def post_name(payload: ItemPayload):
    return payload

    

# run
# uvicorn main:app --reload