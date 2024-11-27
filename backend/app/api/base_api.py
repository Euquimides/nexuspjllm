from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sys
sys.path.append("app")
from ..main import NexusPJLLM
from utils.ingerir import extractor, sintetizador_respuesta, guardar_nodos, embedding_model
from utils.logs import logger

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

class ConsultaRequest(BaseModel):
    consulta: str

class Respuesta(BaseModel):
    respuesta: str

class NodosResponse(BaseModel):
    nodos: list

nexus = NexusPJLLM()

@app.post("/extraer", response_model=NodosResponse)
async def extraer(request: ConsultaRequest):
    try:
        consulta = request.consulta
        nodes = extractor(consulta, embedding_model)
        
        # Handle case where extractor returns None or empty results
        if not nodes:
            return {"nodos": []}
            
        retrieved_nodes = nexus.procesar_consulta(consulta)
        guardar_nodos(nodes)
        
        return {
            "nodos": [
                {"metadata": node.metadata, "texto": node.text} 
                for node in retrieved_nodes
            ]
        }
    except Exception as e:
        logger.error(f"Error procesando consulta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando consulta: {str(e)}"
        )

@app.post("/sintetizar", response_model=Respuesta)
async def sintetizar(request: ConsultaRequest):
    try:
        consulta = request.consulta
        retrieved_nodes = nexus.procesar_consulta(consulta, reranker=True)
        respuesta = sintetizador_respuesta(consulta, retrieved_nodes)
        respuesta = str(respuesta)
        return {"respuesta": respuesta}
    except Exception as e:
        logger.error(f"Error en opción 2: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en opción 2: {str(e)}")

@app.post("/buscar", response_model=NodosResponse)
async def buscar(request: ConsultaRequest):
    try:
        consulta = request.consulta
        retrieved_nodes = nexus.procesar_consulta(consulta, reranker=True)
        return {"nodos": [{"metadata": node.metadata, "texto": node.text} for node in retrieved_nodes]}
    except Exception as e:
        logger.error(f"Error en opción 3: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en opción 3: {str(e)}")