import sys
from flask import abort
import pymysql
from dbutils.pooled_db import PooledDB
from config import OPENAPI_STUB_DIR, DB_HOST, DB_USER, DB_PASSWD, DB_NAME

sys.path.append(OPENAPI_STUB_DIR)
from swagger_server import models

pool = PooledDB(creator=pymysql,
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWD,
                database=DB_NAME,
                maxconnections=1,
                blocking=True)

def get_basins():
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT basin_id, ename, area
            FROM basin
        """)
        result = [models.Basin(*row) for row in cs.fetchall()]
        return result

def get_basin_details(basin_id):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT basin_id, ename, area
            FROM basin
            WHERE basin_id=%s
        """, [basin_id])
        result = cs.fetchone()
    if result:
        basin_id, name, area = result
        return models.Basin(*result)
    else:
        abort(404)

def get_stations_in_basin(basin_id):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT station_id, basin_id, ename, lat, lon
            FROM station WHERE basin_id=%s
            """, [basin_id])
        result = [models.Station(*row) for row in cs.fetchall()]
        return result

def get_station_details(station_id):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT station_id, basin_id, ename, lat, lon
            FROM station
            WHERE station_id=%s
            """, [station_id])
        result = cs.fetchone()
    if result:
        return models.Station(*result)
    else:
        abort(404)

def get_basin_annual_rainfall(basin_id, year):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT SUM(daily_avg)
            FROM (
                SELECT r.year, r.month, r.day, AVG(r.amount) as daily_avg
                FROM rainfall r
                INNER JOIN station s ON r.station_id=s.station_id
                INNER JOIN basin b ON b.basin_id=s.basin_id
                WHERE b.basin_id=%s AND r.year=%s
                GROUP BY r.year, r.month, r.day
            ) daily_avg
        """, [basin_id, year])
        result = cs.fetchone()
    if result and result[0]:
        amount = round(result[0], 2)
        return amount
    else:
        abort(404)

def get_basin_monthly_average(basin_id):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT month, AVG(monthly_amount)
            FROM (
                SELECT SUM(r.amount) as monthly_amount, month
                FROM rainfall r
                INNER JOIN station s ON r.station_id=s.station_id
                INNER JOIN basin b ON s.basin_id=b.basin_id
                WHERE b.basin_id=%s
                GROUP BY r.station_id, month, year
            ) monthly
            GROUP BY month
            ORDER BY month ASC
            """, [basin_id])
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        result = [
            models.MonthlyAverage(months[month-1], month, round(amount, 2))
            for month, amount in cs.fetchall()
        ]
        return result

def get_basin_annual_average(basin_id):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT year, AVG(year_amt)
            FROM (
                SELECT SUM(r.amount) as year_amt, year
                FROM rainfall r
                INNER JOIN station s ON r.station_id=s.station_id
                WHERE s.basin_id=%s
                GROUP BY r.station_id, year
            ) yearly
            GROUP BY year
            ORDER BY year DESC;
            """, [basin_id])
        result = [
            models.AnnualRainfall(year, round(amount, 2))
            for year, amount in cs.fetchall()
        ]
        return result
    
    