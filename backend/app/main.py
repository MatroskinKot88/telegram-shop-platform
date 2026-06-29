from fastapi import FastAPI

app = FastAPI(title="Telegram Shop API")

@app.get("/")
async def root():
    return {"message": "API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}