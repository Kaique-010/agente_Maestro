import logging

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from api.routes import router as api_router
from web.routes import router as web_router

app = FastAPI(title="Aprendiz Mestre")

# registra rotas com prefixo /api
app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(web_router, tags=["web"])

# Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# modo dev
if __name__ == "__main__":
    import uvicorn
    logging.info("Iniciando o servidor FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
    logging.info("Servidor em execução com sucesso.")

