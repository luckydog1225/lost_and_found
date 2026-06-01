from fastapi import FastAPI

app = FastAPI(title="失物招领")

@app.get("/health")
def health():
    return {"status": "ok"}
