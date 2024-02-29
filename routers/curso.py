import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, Query, Depends
from jwt_manager import JWTBearer

max_lenght_username = 12
max_lenght_courseshortname = 25

load_dotenv()
usuario = os.getenv("USER_DB")
contrasena = os.getenv("PASS_DB")
host = os.getenv("HOST_DB")
nombre_base_datos = os.getenv("NAME_DB")

contrasena_codificada = quote_plus(contrasena)
DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{contrasena_codificada}@{host}/{nombre_base_datos}"
engine = create_engine(DATABASE_URL)

curso_router = APIRouter()

#Consultar en cuales cursos esta registrado un usuario.
@curso_router.get("/cursos/", tags=['cursos'], status_code=200, dependencies=[Depends(JWTBearer())])
def read_courses(id : str = Query(max_length=max_lenght_username)):
    with engine.connect() as connection:
        consulta_sql = text(f"""
            SELECT c.shortname AS "Nombre Corto del curso", c.fullname AS "Nombre Largo del curso"
            FROM mdl_user u
            JOIN mdl_user_enrolments ue ON ue.userid = u.id
            JOIN mdl_enrol e ON e.id = ue.enrolid
            JOIN mdl_course c ON c.id = e.courseid
            WHERE u.username = {id};
        """)
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        if rows:
            course_data = [{'shortname': row[0], 'largename': row[1]} for row in rows]
            return JSONResponse(status_code=200, content={'courses': course_data, 'message': "Los cursos en los que se encuentra matriculado el usuario han sido obtenidos correctamente"})
        else:
            return JSONResponse(status_code=404, content={'message': "El usuario digitado no se encuentra matriculado en ningún curso o el usuario no existe"})

#Consulta que devuelve los cursos que un estudiante ha certificado con la fecha de certificación
@curso_router.get("/cursos_certificados/", tags=['cursos'], status_code=200, dependencies=[Depends(JWTBearer())])
def read_courses_certi(id : str = Query(max_length=max_lenght_username)):
    with engine.connect() as connection:
        consulta_sql = text(f"""
            SELECT  c.shortname as shortname, c.fullname as fullname, FROM_UNIXTIME(cci.timecreated) as issuedate
            FROM    mdl_course c
            JOIN    mdl_user u
            JOIN    mdl_customcert_issues cci on (u.id = cci.userid)
            JOIN    mdl_course_modules cm on (cm.course=c.id) AND (cm.module=24) AND (cm.instance=cci.customcertid)
            WHERE   (u.username = :id);
        """).params(id=id)
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        if rows:
            course_data = [{'shortname': row[0], 'timecreated': row[2]} for row in rows]
            return course_data#JSONResponse(status_code=200, content={'courses': course_data, 'message': "Los cursos certificados del usuario han sido obtenidos correctamente"})
        else:
            return JSONResponse(status_code=404, content={'message': "El usuario digitado no se encuentra certificado en ningún curso o el usuario no existe"})