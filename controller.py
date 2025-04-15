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


def get_latest(userId: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT user_id, sleep_id, ts, temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = {userId} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {userId} ORDER BY ts DESC LIMIT 1)
            ORDER BY ts DESC
            LIMIT 1;
        """)
        return models.Latest(*cs.fetchone())


def get_user_efficiency(userId: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = {userId} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {userId} ORDER BY ts DESC LIMIT 1)
        """)
        result = cs.fetchall()
        if not result:
            abort(404)
        light, rem, deep = (result.count(stage)/len(result) for stage in ['Light', 'REM', 'Deep'])

        cs.execute(f"""
            SELECT TIMESTAMPDIFF(SECOND, MIN(ts), MAX(ts)) AS sleep_duration_seconds
            FROM sleep
            WHERE user_id = {userId} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {userId} ORDER BY ts DESC LIMIT 1)
        """)
        sleep_duration = cs.fetchone()[0]/3600

    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT age, gender, smoke, exercise
            FROM sleep_user_data
            WHERE user_id = {userId}
        """)
        age, gender, smoke, exercise = cs.fetchone()
        sleep_efficiency = apply_model(SLEEP_STAGE_MODEL, [age, sleep_duration, rem, deep, light, exercise, gender, smoke])
    return models.Efficiency(light, rem, deep, smoke, exercise, sleep_efficiency)
    
        
def get_user_efficiency_sleep_id(userId: int, sleepId: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = {userId} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {userId} ORDER BY ts DESC LIMIT 1)
        """)
        result = cs.fetchall()
        if not result:
            abort(404)
        light, rem, deep = (result.count(stage)/len(result) for stage in ['Light', 'REM', 'Deep'])

        cs.execute(f"""
            SELECT TIMESTAMPDIFF(SECOND, MIN(ts), MAX(ts)) AS sleep_duration_seconds
            FROM sleep
            WHERE user_id = {userId} AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = {userId} ORDER BY ts DESC LIMIT 1)
        """)
        sleep_duration = cs.fetchone()[0]/3600

    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT age, gender, smoke, exercise
            FROM sleep_user_data
            WHERE user_id = {userId}
        """)
        age, gender, smoke, exercise = cs.fetchone()
        sleep_efficiency = apply_model(SLEEP_STAGE_MODEL, [age, sleep_duration, rem, deep, light, exercise, gender, smoke])
    return models.Efficiency(light, rem, deep, smoke, exercise, sleep_efficiency)

    
def get_user_log(userId: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT sleep_id, ts, temperature, humidity, heartrate
            FROM sleep 
            WHERE user_id = {userId}
            """)
        result = cs.fetchall()
        if not result:
            return abort(404)
        result = [models.LogItem(*row) for row in result]
        return result
