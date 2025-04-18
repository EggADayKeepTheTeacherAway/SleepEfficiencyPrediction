from pydantic import BaseModel, Field


# Pydantic models
class Latest(BaseModel):
    user_id: int
    sleep_id: int
    ts: str
    temperature: float
    humidity: float
    heartrate: int

class Efficiency(BaseModel):
    light: float
    rem: float
    deep: float
    smoke: bool
    exercise: int
    efficiency: float

class LogItem(BaseModel):
    user_id: int
    sleep_id: int
    ts: str
    temperature: float
    humidity: float
    heartrate: int

class SessionInfo(BaseModel):
    sleep_id: int
    start_time: str
    end_time: str

class UserRegister(BaseModel):
    username: str
    password: str
    age: int
    gender: str
    smoke: bool
    exercise: int

class UserEdit(BaseModel):
    user_id: int
    username: str
    password: str
    age: int
    gender: str
    smoke: bool
    exercise: int

class UserDelete(BaseModel):
    user_id: int
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str