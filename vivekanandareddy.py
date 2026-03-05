
import sqlite3
import random
import os
from datetime import datetime, timedelta

DB_PATH = "vivekanandareddy_drone_delivery.db"

SCHEMA_SQL = """

DROP TABLE IF EXISTS delivery_logs;
DROP TABLE IF EXISTS delivery_packages;
DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS packages;
DROP TABLE IF EXISTS drones;
DROP TABLE IF EXISTS warehouses;

CREATE TABLE warehouses(
 warehouse_id TEXT PRIMARY KEY,
 warehouse_name TEXT,
 city TEXT,
 region TEXT,
 latitude REAL,
 longitude REAL,
 capacity_packages INTEGER
);

CREATE TABLE drones(
 drone_id TEXT PRIMARY KEY,
 model TEXT,
 drone_type TEXT,
 max_payload_kg REAL,
 battery_capacity_wh REAL,
 range_km REAL,
 status TEXT
);

CREATE TABLE packages(
 package_id TEXT PRIMARY KEY,
 category TEXT,
 fragile INTEGER,
 weight_kg REAL,
 declared_value_usd REAL,
 recipient_postcode TEXT,
 recipient_age_band TEXT
);

CREATE TABLE deliveries(
 delivery_id TEXT PRIMARY KEY,
 warehouse_id TEXT,
 drone_id TEXT,
 scheduled_departure_utc TEXT,
 delivery_priority TEXT,
 distance_km REAL,
 fee_usd REAL,
 status TEXT
);

CREATE TABLE delivery_packages(
 delivery_id TEXT,
 package_id TEXT,
 quantity INTEGER,
 PRIMARY KEY(delivery_id,package_id)
);

CREATE TABLE delivery_logs(
 delivery_id TEXT,
 log_time_utc TEXT,
 latitude REAL,
 longitude REAL,
 altitude_m REAL,
 speed_mps REAL,
 battery_pct REAL,
 gps_status TEXT,
 event TEXT,
 PRIMARY KEY(delivery_id,log_time_utc)
);

"""

def random_time(start,end):
    diff=end-start
    seconds=random.randint(0,int(diff.total_seconds()))
    return start+timedelta(seconds=seconds)

def main():

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn=sqlite3.connect(DB_PATH)
    cur=conn.cursor()
    cur.executescript(SCHEMA_SQL)

    cities=[
        ("London","South East",51.5,-0.1),
        ("Manchester","North West",53.4,-2.2),
        ("Birmingham","Midlands",52.4,-1.8),
        ("Leeds","Yorkshire",53.7,-1.5),
        ("Bristol","South West",51.4,-2.6)
    ]

    warehouses=[]
    for i,c in enumerate(cities):
        wid=f"W{i+1:03d}"
        warehouses.append((wid,c[0]+" Hub",c[0],c[1],c[2],c[3],random.randint(5000,20000)))
    cur.executemany("INSERT INTO warehouses VALUES (?,?,?,?,?,?,?)",warehouses)

    drone_types=["Quadcopter","FixedWing","VTOL"]
    drones=[]
    for i in range(30):
        drones.append((
            f"D{i+1:04d}",
            random.choice(["SkyDrop","Courier","WingLite"]),
            random.choice(drone_types),
            round(random.uniform(1,5),2),
            random.randint(300,600),
            random.randint(10,40),
            random.choice(["Active","Maintenance"])
        ))
    cur.executemany("INSERT INTO drones VALUES (?,?,?,?,?,?,?)",drones)

    categories=["Grocery","Pharmacy","Electronics","Documents"]
    packages=[]
    for i in range(800):
        age=None if random.random()<0.2 else random.choice(["18-24","25-34","35-44","45-54"])
        packages.append((
            f"PKG{i+1:05d}",
            random.choice(categories),
            random.randint(0,1),
            round(random.uniform(0.1,3),2),
            round(random.uniform(10,200),2),
            "AB"+str(random.randint(10,99)),
            age
        ))
    cur.executemany("INSERT INTO packages VALUES (?,?,?,?,?,?,?)",packages)

    start=datetime(2025,1,1)
    end=datetime(2026,1,1)

    deliveries=[]
    for i in range(400):
        deliveries.append((
            f"DLV{i+1:05d}",
            random.choice(warehouses)[0],
            random.choice(drones)[0],
            random_time(start,end).isoformat(),
            random.choice(["Low","Medium","High"]),
            round(random.uniform(1,15),2),
            round(random.uniform(5,40),2),
            random.choice(["Delivered","Failed","Cancelled"])
        ))
    cur.executemany("INSERT INTO deliveries VALUES (?,?,?,?,?,?,?,?)",deliveries)

    dp=[]
    for d in deliveries:
        for p in random.sample(packages,random.randint(1,3)):
            dp.append((d[0],p[0],1))
    cur.executemany("INSERT INTO delivery_packages VALUES (?,?,?)",dp)

    logs=[]
    events=["Takeoff","EnRoute","Dropoff","Return"]

    for i in range(1800):
        d=random.choice(deliveries)[0]
        t=random_time(start,end).isoformat()

        lat=51+random.random()
        lon=-0.1+random.random()

        if random.random()<0.03:
            lat=None
            lon=None

        logs.append((
            d,t,lat,lon,
            round(random.uniform(30,120),2),
            round(random.uniform(5,20),2),
            round(random.uniform(20,100),2),
            random.choice(["Good","Degraded"]),
            random.choice(events)
        ))

    cur.executemany("INSERT INTO delivery_logs VALUES (?,?,?,?,?,?,?,?,?)",logs)

    conn.commit()
    conn.close()

    print("Database created:",DB_PATH)

if __name__=="__main__":
    main()
