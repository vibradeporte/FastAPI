import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, Query, Depends
from jwt_manager import JWTBearer

max_lenght_username = 12
max_lenght_courseshortname = 37
ge_days = 1
le_days = 50

load_dotenv()
usuario = os.getenv("USER_DB")
contrasena = os.getenv("PASS_DB")
host = os.getenv("HOST_DB")
nombre_base_datos = os.getenv("NAME_DB")

contrasena_codificada = quote_plus(contrasena)
DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{contrasena_codificada}@{host}/{nombre_base_datos}"
engine = create_engine(DATABASE_URL)

estudiante_router = APIRouter()

#Consulta para devolver la informacion de un estudiante
@estudiante_router.get("/estudiante/", tags=['estudiante'], status_code=200, dependencies=[Depends(JWTBearer())])
def info_estudiante(id: str = Query(max_length=max_lenght_username)):
    with engine.connect() as connection:
        consulta_sql = text(f"""
            SELECT  id as user_id, username as user_username, firstname as user_firstname,
                    lastname as user_lastname, email as user_email, phone1 as user_phone1,
                    city as user_city, country as user_country
            FROM    mdl_user
            WHERE   username = {id};
        """)
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        if rows:
            student_data = [{'userid': row[0], 'firstname': row[2], 'lastname': row[3], 'email': row[4], 'phone': row[5], 'city': row[6], 'country': row[7]} for row in rows]
            return JSONResponse(status_code=200, content={'info': student_data, 'message': "La información del estudiante fue encontrada exitosamente."})
        else:
            return JSONResponse(status_code=404, content={'message': "La información del estudiante no pudo ser encontrada"})
        

#Devuelve la fecha de vencimiento de la matricula de un estudiante en un curso en particular
@estudiante_router.get("/estudiante/fecha_matricula/", tags=['estudiante'], status_code=200, dependencies=[Depends(JWTBearer())])
def fechaVencimiento(id: str = Query(max_length=max_lenght_username), curso: str = Query(max_length=max_lenght_courseshortname)):
    with engine.connect() as connection:
        consulta_sql = text(f"""
            SELECT  FROM_UNIXTIME(ue.timeend) AS end_enroll_date
            FROM    mdl_user u
            JOIN    mdl_user_enrolments ue ON u.id = ue.userid
            JOIN    mdl_enrol e ON ue.enrolid = e.id
            JOIN    mdl_course c ON e.courseid = c.id
            WHERE   u.username = :id AND c.shortname = :curso;
        """).params(curso=curso, id=id)
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        if rows:
            student_date = [{'date': row[0]} for row in rows]
            return student_date#JSONResponse(status_code=200, content={'info': student_date, 'message': "La información del estudiante fue encontrada exitosamente."})
        else:
            return JSONResponse(status_code=404, content={'message': "La información del estudiante no pudo ser encontrada"})
        
#Servicio para devolver la url del certificado de un curso completado
@estudiante_router.get("/estudiante/certificado/", tags=['estudiante'], status_code=200, dependencies=[Depends(JWTBearer())])
def certi_estudiante(id: str = Query(max_length=max_lenght_username), curso: str = Query(max_length=max_lenght_courseshortname)):
    with engine.connect() as connection:
        consulta_sql = text(f"""
            SELECT  CONCAT('https://elaulavirtual.com/ins/mod/customcert/view.php?id=',cm.id,'&downloadissue=',u.id) as url_downoload
            FROM    mdl_user u, mdl_course_modules cm
            JOIN    mdl_course c on (cm.course=c.id)
            WHERE   (cm.module=24) AND (u.username= :id) AND (c.shortname= :curso);
        """).params(curso=curso, id=id)
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        if rows:
            cert_url = [{'url': row[0]} for row in rows]
            return JSONResponse(status_code=200, content={'url': cert_url, 'message': "La url del certificado del estudiante fue encontrada exitosamente."})
        else:
            return JSONResponse(status_code=404, content={'message': "El certificado del estudiante no pudo ser encontrado"})

#Servicio para actualizar la fecha de finalización de matricula de un estudiante en un curso
@estudiante_router.put("/estudiante/ampliar_matricula/", tags=['estudiante'], status_code=200, dependencies=[Depends(JWTBearer())])
def ampliar_matricula(dias: int = Query(ge=ge_days, le=le_days), id: str = Query(max_length=max_lenght_username), curso: str = Query(max_length=max_lenght_courseshortname)):
    with engine.connect() as connection:
        update_sql = text(f"""
            UPDATE  mdl_user_enrolments
            SET     timeend =   timeend + ( :dias * 86400) -- 86400 segundos = 1 día
            WHERE   userid =    (SELECT u.id as userid FROM mdl_user as u WHERE u.username = :id)
            AND     enrolid =   (SELECT ue.enrolid as enrolid
                                FROM    mdl_user_enrolments as ue
                                JOIN    mdl_user as u ON (u.id=ue.userid)
                                JOIN    mdl_enrol as e ON (ue.enrolid=e.id)
                                JOIN    mdl_course as c ON (c.id=e.courseid)
                                WHERE   (c.shortname = :curso) AND (u.username = :id));
        """).params(dias=dias, curso=curso, id=id)
        try:
            connection.execute(update_sql)
            connection.commit()
            return JSONResponse(status_code=200, content={'message': "Los datos fueron actualizados exitosamente."})
        except Exception as e:
            return e#JSONResponse(status_code=400, content={'message': e})