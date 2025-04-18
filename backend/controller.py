import sys
from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
import pymysql
from dbutils.pooled_db import PooledDB
from typing import List, Optional
from schemas import *
from config import OPENAPI_STUB_DIR, DB_HOST, DB_USER, DB_PASSWD, DB_NAME
from models import SLEEP_STAGE_MODEL, SLEEP_QUALITY_MODEL
from datetime import datetime, timedelta

sys.path.append(OPENAPI_STUB_DIR)

# Database connection pool
pool = PooledDB(creator=pymysql,
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWD,
                database=DB_NAME,
                maxconnections=1,
                blocking=True)

# Create FastAPI app
app = FastAPI(
    title="Sleep Efficiency API",
    description="This API provides Real-time analysis of your sleep. Raw data provided by 2 Kaggle datasets.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper function
def apply_model(model, data):
    return model.predict(data)

async def get_user_id(username, password):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT user_id
            FROM sleep_user_data
            WHERE username = %s AND password = %s
            """, (username, password))
        
        result = cs.fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        return result[0]
    
async def get_latest_sleep_id(user_id):
    """Returns (sleep_id, ts)"""
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT sleep_id, ts
            FROM sleep
            WHERE user_id = %s
            ORDER BY ts DESC
            LIMIT 1
            """, (user_id,))
        result = cs.fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="Invalid user_id")
        return result
        


async def check_credential(username, password):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT user_id
            FROM sleep_user_data
            WHERE username = %s AND password = %s
            """, (username, password))
        
        result = cs.fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="Invalid credentials")

# Routes
@app.get("/sleep-api/latest/{user_id}", response_model=Latest)
async def get_latest(user_id: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT user_id, sleep_id, ts, temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = %s AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = %s ORDER BY ts DESC LIMIT 1)
            ORDER BY ts DESC
            LIMIT 1;
        """, (user_id, user_id))
        result = cs.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Data not found")
        return Latest(
            user_id=result[0],
            sleep_id=result[1],
            ts=result[2],
            temperature=result[3],
            humidity=result[4],
            heartrate=result[5]
        )

@app.get("/sleep-api/efficiency/{user_id}", response_model=List[Efficiency])
async def get_user_efficiency(user_id: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT age, gender, smoke, exercise
            FROM sleep_user_data
            WHERE user_id = %s
        """, (user_id,))
        result = cs.fetchone()
        age, gender, smoke, exercise = result
        if not result:
            raise HTTPException(status_code=400, detail="Invalid request")
        
    return_list = []    
    for sleep_id in range(await get_latest_sleep_id()[0]):
        with pool.connection() as conn, conn.cursor() as cs:
            cs.execute("""
                SELECT temperature, humidity, heartrate
                FROM sleep
                WHERE user_id = %s AND sleep_id = %s
            """, (user_id, sleep_id))
            result = apply_model(SLEEP_STAGE_MODEL, cs.fetchall()).tolist()
            light, rem, deep = (result.count(stage)/len(result) for stage in ['Light', 'REM', 'Deep'])
            sleep_efficiency = apply_model(SLEEP_QUALITY_MODEL, [[age, sleep_duration, rem, deep, light, exercise, gender == 'male', smoke]])[0]

            cs.execute("""
                SELECT TIMESTAMPDIFF(SECOND, MIN(ts), MAX(ts)) AS sleep_duration_seconds, MIN(ts), MAX(ts)
                FROM sleep
                WHERE user_id = %s AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = %s ORDER BY ts DESC LIMIT 1)
            """, (user_id, user_id))
            sleep_duration, start_time, end_time = cs.fetchone()
            sleep_duration = sleep_duration/3600
            return_list.append(
                Efficiency(
                    light=light,
                    rem=rem,
                    deep=deep,
                    smoke=bool(smoke),
                    exercise=exercise,
                    efficiency=sleep_efficiency,
                    sleep_duration=sleep_duration,
                    start_time=start_time,
                    end_time=end_time
            ))
    return return_list

@app.get("/sleep-api/efficiency/{user_id}/{sleep_id}", response_model=Efficiency)
async def get_user_efficiency_sleep_id(user_id: int, sleep_id: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT age, gender, smoke, exercise
            FROM sleep_user_data
            WHERE user_id = %s
        """, (user_id,))
        result = cs.fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="Invalid request")
        age, gender, smoke, exercise = result

    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = %s AND sleep_id = %s
        """, (user_id, sleep_id))
        result = apply_model(SLEEP_STAGE_MODEL, cs.fetchall()).tolist()
        light, rem, deep = (result.count(stage)/len(result) for stage in ['Light', 'REM', 'Deep'])
        sleep_efficiency = apply_model(SLEEP_QUALITY_MODEL, [[age, sleep_duration, rem, deep, light, exercise, gender == 'male', smoke]])[0]

        cs.execute("""
            SELECT TIMESTAMPDIFF(SECOND, MIN(ts), MAX(ts)) AS sleep_duration_seconds, MIN(ts), MAX(ts)
            FROM sleep
            WHERE user_id = %s AND sleep_id = %s
        """, (user_id, sleep_id))
        sleep_duration, start_time, end_time = cs.fetchone()
        sleep_duration = sleep_duration/3600
        sleep_efficiency = apply_model(SLEEP_QUALITY_MODEL, [[age, sleep_duration, rem, deep, light, exercise, gender == 'male', smoke]])[0]
    
        return Efficiency(
                light=light,
                rem=rem,
                deep=deep,
                smoke=bool(smoke),
                exercise=exercise,
                efficiency=sleep_efficiency,
                sleep_duration=sleep_duration,
                start_time=start_time,
                end_time=end_time
                )

@app.get("/sleep-api/log/{user_id}", response_model=List[LogItem])
async def get_user_log(user_id: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT user_id, sleep_id, ts, temperature, humidity, heartrate
            FROM sleep 
            WHERE user_id = %s
            """, (user_id,))
        result = cs.fetchall()
        if not result:
            raise HTTPException(status_code=400, detail="Invalid request")
        
        return [
            LogItem(
                user_id=row[0],
                sleep_id=row[1],
                ts=row[2],
                temperature=row[3],
                humidity=row[4],
                heartrate=row[5]
            ) for row in result
        ]
    
@app.get("/sleep-api/log/{user_id}/{sleep_id}", response_model=List[LogItem])
async def get_user_log(user_id: int, sleep_id: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT user_id, sleep_id, ts, temperature, humidity, heartrate
            FROM sleep 
            WHERE user_id = %s AND sleep_id = %s
            """, (user_id, sleep_id))
        result = cs.fetchall()
        if not result:
            raise HTTPException(status_code=400, detail="Invalid request")
        
        return [
            LogItem(
                user_id=row[0],
                sleep_id=row[1],
                ts=row[2],
                temperature=row[3],
                humidity=row[4],
                heartrate=row[5]
            ) for row in result
        ]
    

@app.post("/sleep-api/log")
async def send_data(data: IncomingData):
    try:
        user_id = await get_user_id(data['username'], data['password'])
        sleep_id, ts = get_latest_sleep_id(user_id)
        ts_datetime = datetime.fromisoformat(ts)
        current_time = datetime.now()
        time_diff = current_time - ts_datetime
        if time_diff >= timedelta(hours=1):
            sleep_id += 1    

        with pool.connection() as conn, conn.cursor() as cs:
            cs.execute("""
                INSERT INTO `sleep` (`sleep_id`, `ts`, `temperature`, `humidity`, `heartrate`) 
                VALUES (%s, %s, %s, %s, %s) 
            """, (
                sleep_id,
                current_time,
                data.temperature,
                data.humidity,
                data.heartrate
            ))
            conn.commit()

        return {"message": "Data Inserted"}
    
    except HTTPException as e:
        return e

@app.get("/sleep-api/sessions/{user_id}", response_model=List[SessionInfo])
async def get_user_sessions(user_id: int):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT sleep_id, MIN(ts) AS start_time, MAX(ts) AS end_time
            FROM sleep
            WHERE user_id = %s
            GROUP BY sleep_id;
            """, [user_id])
        result = cs.fetchall()
        print(result)
        if not result:
            raise HTTPException(status_code=400, detail="Invalid request")
        
        return [
            SessionInfo(
                sleep_id=row[0],
                start_time=str(row[1]),
                end_time=str(row[2])
            ) for row in result
        ]

@app.post("/sleep-api/user/register")
async def user_register(user: UserRegister):
    # Validation
    if (len(user.username) > 255 or 
        len(user.password) > 255 or 
        user.age <= 0 or 
        user.gender not in ['male', 'female'] or
        user.exercise < 0 or 7 < user.exercise):
        raise HTTPException(status_code=400, detail="Invalid Values")
    
    with pool.connection() as conn, conn.cursor() as cs:
        # Check if username exists
        cs.execute("""
            SELECT user_id
            FROM sleep_user_data
            WHERE username = %s
            """, (user.username,))
        
        if cs.fetchone():
            raise HTTPException(status_code=400, detail="Username taken")

        # Insert new user
        cs.execute("""
            INSERT INTO `sleep_user_data` (`username`, `password`, `age`, `gender`, `smoke`, `exercise`) 
            VALUES (%s, %s, %s, %s, %s, %s) 
        """, (
            user.username,
            user.password,
            user.age,
            user.gender,
            int(user.smoke),
            user.exercise
        ))
        conn.commit()
    
    return {"message": "User Registered"}

@app.post("/sleep-api/user/edit")
async def user_edit(user: UserEdit):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            UPDATE `sleep_user_data`
            SET `username` = %s,
                `password` = %s,
                `age` = %s,
                `gender` = %s,
                `smoke` = %s,
                `exercise` = %s
            WHERE `user_id` = %s
        """, (
            user.username,
            user.password,
            user.age,
            user.gender,
            int(user.smoke),
            user.exercise,
            user.user_id
        ))
        conn.commit()
    
    return {"message": "Success"}


@app.post("/sleep-api/user/delete")
async def user_edit(user: UserDelete):
    try:
        db_id = await get_user_id(user['username'], user['password'])
        with pool.connection() as conn, conn.cursor() as cs:
            if db_id != user['user_id']:
                raise HTTPException(400, 'Invalid Credentials')
            cs.execute("""
                DELETE FROM sleep_user_data WHERE `sleep_user_data`.`user_id` = %s
            """, (
                user.user_id,
            ))
            conn.commit()
        return {"message": "User deleted"}
    except HTTPException as e:
        return e


@app.post("/sleep-api/user/login")
async def user_login(user: UserLogin):
    try:
        user_id = await get_user_id(user.username, user.password)
        return {"message": "Success", "user_id": user_id }

    except HTTPException as e:
        return e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)