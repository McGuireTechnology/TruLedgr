from fastapi import FastAPI

app = FastAPI(title="TruLedgr API", version="0.1.0")


@app.get("/")
async def root():
    return {"message": "Bonjour from TruLedgr API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Bonjour, TruLedgr is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
