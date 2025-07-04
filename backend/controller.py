import sys
from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import pandas as pd
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
    print(f"get_user_id called with username: '{username}', password: '{password}'")
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT user_id
            FROM sleep_user_data
            WHERE username = %s AND password = %s
            """, (username, password))

        result = cs.fetchone()
        print(f"get_user_id query result: {result}")
        if not result:
            print("get_user_id: No user found for the given credentials.")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        print(f"get_user_id returning user_id: {result[0]}")
        return result[0]

async def get_latest_sleep_id(user_id):
    """Returns (sleep_id, ts)"""
    print(f"get_latest_sleep_id called for user_id: {user_id}")
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT sleep_id, ts
            FROM sleep
            WHERE user_id = %s
            ORDER BY ts DESC
            LIMIT 1
            """, (user_id,))
        result = cs.fetchone()
        print(f"get_latest_sleep_id query result: {result}")
        if not result:
            print(f"get_latest_sleep_id: No sleep data found for user_id: {user_id}")
            raise HTTPException(status_code=400, detail="Invalid user_id")
        return result


# Routes
@app.get("/sleep-api/latest/{user_id}", response_model=Latest)
async def get_latest(user_id: int):
    print(f"get_latest called for user_id: {user_id}")
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT user_id, sleep_id, ts, temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = %s AND sleep_id = (SELECT sleep_id FROM sleep WHERE user_id = %s ORDER BY ts DESC LIMIT 1)
            ORDER BY ts DESC
            LIMIT 1;
        """, (user_id, user_id))
        result = cs.fetchone()
        print(f"get_latest query result: {result}")
        if not result:
            raise HTTPException(status_code=404, detail="Data not found")
        user_id, sleep_id, ts, temp, humidity, heartrate = result
        return Latest(
            user_id=user_id,
            sleep_id=sleep_id,
            ts=ts.strftime("%d-%m-%Y %H:%M:%S"),
            temperature=temp,
            humidity=humidity,
            heartrate=heartrate
        )

@app.get("/sleep-api/efficiency/{user_id}", response_model=List[Efficiency])
async def get_user_efficiency(user_id: int):
    print(f"get_user_efficiency called for user_id: {user_id}")
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

    return_list = []
    try:
        max_sleep_info = await get_latest_sleep_id(user_id)
        max_sleep_id = max_sleep_info[0]
        for sleep_id in range(max_sleep_id + 1):
            with pool.connection() as conn, conn.cursor() as cs:
                cs.execute("""
                    SELECT heartrate, temperature, humidity
                    FROM sleep
                    WHERE user_id = %s AND sleep_id = %s
                """, (user_id, sleep_id))
                rows = cs.fetchall()
                print("log for effi : ", rows)
                df = pd.DataFrame(rows, columns=["heartrate", "temperature", "humidity"])
                stage_results = apply_model(SLEEP_STAGE_MODEL, df).tolist()
                light, rem, deep = (stage_results.count(stage)/len(stage_results) if stage_results else 0 for stage in ['Light', 'REM', 'Deep'])

                cs.execute("""
                    SELECT TIMESTAMPDIFF(SECOND, MIN(ts), MAX(ts)) AS sleep_duration_seconds, MIN(ts), MAX(ts)
                    FROM sleep
                    WHERE user_id = %s AND sleep_id = %s
                """, (user_id, sleep_id))
                sleep_data = cs.fetchone()
                print("sleep data effi : ", sleep_data)
                if sleep_data:
                    sleep_duration, start_time, end_time = sleep_data
                    sleep_duration = sleep_duration/3600
                    input_df = pd.DataFrame([{
                        "Age": age,
                        "Sleep duration": sleep_duration,
                        "REM sleep percentage": rem,
                        "Deep sleep percentage": deep,
                        "Light sleep percentage": light,
                        "Exercise frequency": exercise,
                        "Gender_Male": gender == 'male',
                        "Smoking status_Yes": smoke
                    }])

                    sleep_efficiency = apply_model(SLEEP_QUALITY_MODEL, input_df)[0]

                    return_list.append(
                        Efficiency(
                            light=light,
                            rem=rem,
                            deep=deep,
                            smoke=bool(smoke),
                            exercise=exercise,
                            efficiency=sleep_efficiency,
                            sleep_duration=sleep_duration,
                            start_time=start_time.strftime("%d-%m-%Y %H:%M:%S"),
                            end_time=end_time.strftime("%d-%m-%Y %H:%M:%S")
                    ))
        print(f"get_user_efficiency user data query result: {return_list}")
    except HTTPException as e:
        print(f"get_user_efficiency: HTTPException - {e}")
        # Decide if you want to return an empty list or re-raise
        return []
    except Exception as e:
        print(f"get_user_efficiency: Unexpected error - {e}")
        return []
    return return_list

@app.get("/sleep-api/efficiency/{user_id}/{sleep_id}", response_model=Efficiency)
async def get_user_efficiency_sleep_id(user_id: int, sleep_id: int):
    print(f"get_user_efficiency_sleep_id called for user_id: {user_id}, sleep_id: {sleep_id}")
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT age, gender, smoke, exercise
            FROM sleep_user_data
            WHERE user_id = %s
        """, (user_id,))
        result = cs.fetchone()
        print(f"get_user_efficiency_sleep_id user data query result: {result}")
        if not result:
            raise HTTPException(status_code=400, detail="Invalid request")
        age, gender, smoke, exercise = result

    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT heartrate, temperature, humidity
            FROM sleep
            WHERE user_id = %s AND sleep_id = %s
        """, (user_id, sleep_id))
        rows = cs.fetchall()
        df = pd.DataFrame(rows, columns=["heartrate", "temperature","humidity"])
        stage_results = apply_model(SLEEP_STAGE_MODEL, df).tolist()
        light, rem, deep = (stage_results.count(stage)/len(stage_results) if stage_results else 0 for stage in ['Light', 'REM', 'Deep'])

        cs.execute("""
            SELECT TIMESTAMPDIFF(SECOND, MIN(ts), MAX(ts)) AS sleep_duration_seconds, MIN(ts), MAX(ts)
            FROM sleep
            WHERE user_id = %s AND sleep_id = %s
        """, (user_id, sleep_id))
        sleep_data = cs.fetchone()
        if sleep_data:
            sleep_duration, start_time, end_time = sleep_data
            sleep_duration = sleep_duration/3600
            input_df = pd.DataFrame([{
                "Age": age,
                "Sleep duration": sleep_duration,
                "REM sleep percentage": rem,
                "Deep sleep percentage": deep,
                "Light sleep percentage": light,
                "Exercise frequency": exercise,
                "Gender_Male": gender == 'male',
                "Smoking status_Yes": smoke
            }])

            sleep_efficiency = apply_model(SLEEP_QUALITY_MODEL, input_df)[0]

            return Efficiency(
                    light=light,
                    rem=rem,
                    deep=deep,
                    smoke=bool(smoke),
                    exercise=exercise,
                    efficiency=sleep_efficiency,
                    sleep_duration=sleep_duration,
                    start_time=start_time.strftime("%d-%m-%Y %H:%M:%S"),
                    end_time=end_time.strftime("%d-%m-%Y %H:%M:%S")
                    )
        else:
            raise HTTPException(status_code=404, detail=f"Sleep data not found for user {user_id} and sleep_id {sleep_id}")

@app.get("/sleep-api/log/{user_id}", response_model=List[LogItem])
async def get_user_log(user_id: int):
    print(f"get_user_log (all) called for user_id: {user_id}")
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT user_id, sleep_id, ts, temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = %s
            """, (user_id,))
        result = cs.fetchall()
        # print(f"get_user_log (all) query result: {result}")
        if not result:
            raise HTTPException(status_code=404, detail="No log data found for this user")

        return [
            LogItem(
                user_id=row[0],
                sleep_id=row[1],
                ts=row[2].strftime("%d-%m-%Y %H:%M:%S"),
                temperature=row[3],
                humidity=row[4],
                heartrate=row[5]
            ) for row in result
        ]

@app.get("/sleep-api/log/{user_id}/{sleep_id}", response_model=List[LogItem])
async def get_user_log(user_id: int, sleep_id: int):
    print(f"get_user_log (by sleep_id) called for user_id: {user_id}, sleep_id: {sleep_id}")
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT user_id, sleep_id, ts, temperature, humidity, heartrate
            FROM sleep
            WHERE user_id = %s AND sleep_id = %s
            """, (user_id, sleep_id))
        result = cs.fetchall()
        # print(f"get_user_log (by sleep_id) query result: {result}")
        if not result:
            raise HTTPException(status_code=404, detail=f"Log data not found for user {user_id} and sleep_id {sleep_id}")

        return [
            LogItem(
                user_id=row[0],
                sleep_id=row[1],
                ts=row[2].strftime("%d-%m-%Y %H:%M:%S"),
                temperature=row[3],
                humidity=row[4],
                heartrate=row[5]
            ) for row in result
        ]


@app.post("/sleep-api/log")
async def send_data(data: IncomingData):
    print(f"send_data received data: {data}")
    try:
        user_id = await get_user_id(data.username, data.password)
        print(f"send_data got user_id: {user_id}")
        current_time = datetime.now()
        try:
            sleep_id, ts = await get_latest_sleep_id(user_id)
            print(f"send_data got latest sleep info: sleep_id={sleep_id}, ts={ts}")  # Fixed variable name
            ts_datetime = datetime.fromisoformat(str(ts))  # Added str() to ensure compatibility
            time_diff = current_time - ts_datetime
            if time_diff >= timedelta(hours=1):
                sleep_id += 1
        except HTTPException as e:
            if e.detail == "Invalid user_id":
                print("send_data: No previous sleep data found, initializing sleep_id to 1")
                sleep_id = 0
            else:
                raise  # Re-raise other HTTPExceptions

        with pool.connection() as conn, conn.cursor() as cs:
            cs.execute("""
                INSERT INTO `sleep` (`sleep_id`, `ts`, `temperature`, `humidity`, `heartrate`, `user_id`)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                sleep_id,
                current_time,
                data.temperature,
                data.humidity,
                data.heartrate,
                user_id  # Ensure user_id is included
            ))
            conn.commit()
            print("send to sleep : ", sleep_id,
                current_time,
                data.temperature,
                data.humidity,
                data.heartrate,
                user_id )

        return {"message": "Data Inserted"}

    except HTTPException as e:
        print(f"send_data caught HTTPException: {e}")
        raise e  # Raise instead of return
    except Exception as e:
        print(f"send_data caught unexpected exception: {e}")
        raise


@app.get("/sleep-api/sessions/{user_id}", response_model=List[SessionInfo])
async def get_user_sessions(user_id: int):
    print(f"get_user_sessions called for user_id: {user_id}")
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT sleep_id, MIN(ts) AS start_time, MAX(ts) AS end_time
            FROM sleep
            WHERE user_id = %s
            GROUP BY sleep_id;
            """, [user_id])
        result = cs.fetchall()
        print(f"get_user_sessions query result: {result}")
        if not result:
            raise HTTPException(status_code=404, detail="No sleep sessions found for this user")

        return [
            SessionInfo(
                sleep_id=row[0],
                start_time=str(row[1]),
                end_time=str(row[2])
            ) for row in result
        ]

@app.post("/sleep-api/user/register")
async def user_register(user: UserRegister):
    print(f"user_register called with data: {user}")
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
    print(f"user_edit called with data: {user}")
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
        db_id = await get_user_id(user.username, user.password)
        with pool.connection() as conn, conn.cursor() as cs:
            if db_id != user.user_id:
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
        return {"user_id": user_id, "message": "Success"}
    except HTTPException as e:
        raise e  # Raise the exception instead of returning it


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
