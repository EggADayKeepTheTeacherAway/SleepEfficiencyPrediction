import sys
from flask import abort
import pymysql
from dbutils.pooled_db import PooledDB
from config import OPENAPI_STUB_DIR, DB_HOST, DB_USER, DB_PASSWD, DB_NAME
from models import SLEEP_STAGE_MODEL, SLEEP_QUALITY_MODEL

sys.path.append(OPENAPI_STUB_DIR)
from stub.swagger_server import models


pool = PooledDB(creator=pymysql,
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWD,
                database=DB_NAME,
                maxconnections=1,
                blocking=True)


def apply_model(model, data):
    return model.predict(data)


def get_latest(user_id: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT user_id, sleep_id, ts, temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = {user_id} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {user_id} ORDER BY ts DESC LIMIT 1)
            ORDER BY ts DESC
            LIMIT 1;
        """)
        result = cs.fetchone()
        if not result:
            return abort(404)
        return models.Latest(*result)


def get_user_efficiency(user_id: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = {user_id} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {user_id} ORDER BY ts DESC LIMIT 1)
        """)
        result = cs.fetchall()
        if not result:
            abort(400)
        result = apply_model(SLEEP_STAGE_MODEL, result).tolist()
        light, rem, deep = (result.count(stage)/len(result) for stage in ['Light', 'REM', 'Deep'])

        cs.execute(f"""
            SELECT TIMESTAMPDIFF(SECOND, MIN(ts), MAX(ts)) AS sleep_duration_seconds
            FROM sleep
            WHERE user_id = {user_id} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {user_id} ORDER BY ts DESC LIMIT 1)
        """)
        sleep_duration = cs.fetchone()[0]/3600

    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT age, gender, smoke, exercise
            FROM sleep_user_data
            WHERE user_id = {user_id}
        """)
        age, gender, smoke, exercise = cs.fetchone()
        sleep_efficiency = apply_model(SLEEP_QUALITY_MODEL, [[age, sleep_duration, rem, deep, light, exercise, gender == 'male', smoke]])[0]
    return models.Efficiency(light, rem, deep, smoke, exercise, sleep_efficiency)
    
        
def get_user_efficiency_sleep_id(user_id: int, sleepId: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = {user_id} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {user_id} ORDER BY ts DESC LIMIT 1)
        """)
        result = cs.fetchall()
        if not result:
            abort(400)
        light, rem, deep = (result.count(stage)/len(result) for stage in ['Light', 'REM', 'Deep'])

        cs.execute(f"""
            SELECT TIMESTAMPDIFF(SECOND, MIN(ts), MAX(ts)) AS sleep_duration_seconds
            FROM sleep
            WHERE user_id = {user_id} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {user_id} ORDER BY ts DESC LIMIT 1)
        """)
        sleep_duration = cs.fetchone()[0]/3600

    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT age, gender, smoke, exercise
            FROM sleep_user_data
            WHERE user_id = {user_id}
        """)
        result = cs.fetchone()
        if not result:
            return abort(400)
        age, gender, smoke, exercise = result
        sleep_efficiency = apply_model(SLEEP_STAGE_MODEL, [age, sleep_duration, rem, deep, light, exercise, gender, smoke])
    return models.Efficiency(light, rem, deep, smoke, exercise, sleep_efficiency)

    
def get_user_log(user_id: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT user_id,sleep_id, ts, temperature, humidity, heartrate
            FROM sleep 
            WHERE user_id = {user_id}
            """)
        result = cs.fetchall()
        if not result:
            return abort(400)
        result = [models.LogItem(*row) for row in result]
        return result


def user_register(username: str, password: str, age: int, gender: str, smoke: bool, exercise: int):
    if (len(username) > 255 or 
        len(password) > 255 or 
        age <= 0 or 
        gender not in ['male', 'female'] or
        exercise < 0 or 7 < exercise):
        return abort(400)

    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            INSERT INTO `sleep_user_data` (`username`, `password`, `age`, `gender`, `smoke`, `exercise`) 
                   VALUES (NULL, '{username}', '{password}', '{age}', '{gender}', '{smoke}', '{exercise}')
            """)
        result = cs.fetchall()
        if not result:
            return abort(400)
        result = [models.LogItem(*row) for row in result]
        return result
    

def user_login(username: str, password: str):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT user_id
            FROM sleep_user_data
            WHERE username = {username} AND password = {password}
            """)
        if cs.fetchone():
            return "Success", 200, {"Access-Control-Allow-Origin": "*"} 
        return abort(400)

