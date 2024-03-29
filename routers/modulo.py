from datetime import date
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, Query, Depends
from jwt_manager import JWTBearer

max_lenght_username = 12
max_lenght_courseshortname = 37

load_dotenv()
usuario = os.getenv("USER_DB")
contrasena = os.getenv("PASS_DB")
host = os.getenv("HOST_DB")
nombre_base_datos = os.getenv("NAME_DB")

contrasena_codificada = quote_plus(contrasena)
DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{contrasena_codificada}@{host}/{nombre_base_datos}"
engine = create_engine(DATABASE_URL)

modulo_router = APIRouter()

@modulo_router.get("/modulo/", tags=['modulos'], status_code=200, dependencies=[Depends(JWTBearer())])
def modulos_curso(id: str = Query(max_length=max_lenght_username), curso: str = Query(max_length=max_lenght_courseshortname)):
    with engine.connect() as connection:
        consulta_sql = text(f"""
            SELECT  subconsulta.quiz_id as quiz_id, subconsulta.quiz_name as quiz_name, subconsulta.attempt_count as quiz_attempt_count,
                    subconsulta.Progress as quiz_status, qo.groupid as groupid, g.name as groupname, c1.shortname as courseshortname
            FROM    (SELECT q.id AS quiz_id, q.name AS quiz_name, COUNT(qa.id) AS attempt_count,
                    CASE    WHEN cmc.completionstate = 0 THEN 'In Progress'
                            WHEN cmc.completionstate = 1 THEN 'Completed'
                            WHEN cmc.completionstate = 2 THEN 'Completed with Pass'
                            WHEN cmc.completionstate = 3 THEN 'Completed with Fail'
                    ELSE    'Desconocido'
                    END AS  'Progress'
                    FROM    mdl_quiz q
                    JOIN    mdl_course c ON (q.course = c.id) AND (c.shortname = :curso)
                    JOIN    mdl_quiz_attempts qa ON qa.quiz = q.id
                    JOIN    mdl_user u ON (qa.userid = u.id) AND (u.username = :id)
                    JOIN    mdl_course_modules cm ON (cm.course = c.id) AND (q.id = cm.instance)
                    JOIN    mdl_modules m ON cm.module = m.id
                    LEFT JOIN mdl_course_modules_completion cmc ON (cmc.userid = u.id) AND (cmc.coursemoduleid = cm.id)
                    GROUP BY q.id) as subconsulta
            JOIN    mdl_quiz_overrides as qo ON (subconsulta.quiz_id=qo.quiz)
            JOIN    mdl_groups as g ON (qo.groupid=g.id)
            JOIN    mdl_course as c1 ON (g.courseid=c1.id)
            WHERE   (subconsulta.attempt_count>=4) AND ((subconsulta.Progress='Completed with Fail') OR (subconsulta.Progress='Desconocido'));
            """).params(curso=curso, id=id)
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        if rows:
            module_data = [{'quiz_name': row[1], 'status': row[3], 'group_id': row[4], 'group_name': row[5]} for row in rows]
            return JSONResponse(status_code=200, content={'modulos': module_data, 'message': "Los modulos del curso han sido encontrados."})
        else:
            return JSONResponse(status_code=404, content={'message': "No existen modulos perdidos para el curso consultado"})

#Servicio para crear el registro del estudiante en el grupo de ampliación de un modulo de un curso en especifico
@modulo_router.post("/modulo/ampliar/", tags=['modulos'], status_code=200, dependencies=[Depends(JWTBearer())])
def ampliar_intentos(groupid: str = Query(max_length=max_lenght_username), userid: str = Query(max_length=max_lenght_username)):
     with engine.connect() as connection:
        consulta_sql = text(f"""
            INSERT INTO mdl_groups_members
                (groupid, userid, timeadded, itemid)
            VALUES
                ( :groupid, :userid, UNIX_TIMESTAMP(), 0);
            """).params(groupid=groupid, userid=userid)
        try:
            connection.execute(consulta_sql)
            connection.commit()
            return JSONResponse(status_code=201, content={'message': "Los datos fueron agregados exitosamente."})
        except Exception as e:
            return e#JSONResponse(status_code=400, content={'message': e})