import uvicorn
from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="Assistente Financeiro",
    description="API para extrair dados de faturas de cartão de crédito em PDF",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
