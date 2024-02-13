from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routers.curso import curso_router
from routers.userlog import userlog_router
from routers.estudiantes import estudiante_router
from routers.modulo import modulo_router


app = FastAPI()
app.title = "Universal Learning API"
app.version = "0.0.1"

app.include_router(curso_router)
app.include_router(userlog_router)
app.include_router(estudiante_router)
app.include_router(modulo_router)

@app.get('/', tags=['home'])
def message():
    return HTMLResponse('<h1>Universal Learning API</h1>')