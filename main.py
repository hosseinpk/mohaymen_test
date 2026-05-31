from fastapi import FastAPI
from datetime import datetime,timezone

app = FastAPI()


@app.get("/health",summary="health check")
async def health_check():
    return {"status":"ok","datetime":datetime.now(timezone.utc).isoformat()}