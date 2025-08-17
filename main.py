from fastapi import FastAPI, Request
from api.routes import router as api_router
from web.routes import router as web_router

app = FastAPI(title="Aprendiz Mestre")

# registra rotas
app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(web_router, tags=["web"])

# modo dev
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
