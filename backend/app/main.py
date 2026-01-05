from fastapi import FastAPI

app = FastAPI(title="Test App")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}
