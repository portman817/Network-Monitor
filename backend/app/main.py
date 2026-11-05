from fastapi import FastAPI

app = FastAPI(title="Network Monitor")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
