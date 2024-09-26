from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routers.curso import curso_router
from routers.userlog import userlog_router
from routers.estudiantes import estudiante_router
from routers.modulo import modulo_router
from routers.correo import correo_router
from routers.comparacion_json import comparacion_router


app = FastAPI()
app.title = "Universal Learning API"
app.version = "0.0.1"

app.include_router(curso_router)
app.include_router(userlog_router)
app.include_router(estudiante_router)
app.include_router(modulo_router)
app.include_router(correo_router)
app.include_router(comparacion_router)

@app.get('/', tags=['home'])
def message():
    return HTMLResponse('<h1>Universal Learning API</h1>')