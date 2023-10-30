import sqlite3 as sl


def init_db():
    """Initialize the database"""

    con = sl.connect("train.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS location(id STRING PRIMARY KEY, 
                                                        timestamp STRING, 
                                                        latitude_value FLOAT, 
                                                        latitude_type STRING, 
                                                        longitude_value FLOAT, 
                                                        longitude_type STRING, 
                                                        gps_fix_status INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS ping(id STRING PRIMARY KEY, 
                                                    timestamp STRING, 
                                                    min_ping INTEGER, 
                                                    max_ping INTEGER, 
                                                    mean_ping INTEGER, 
                                                    network_name STRING)""")
    con.commit()

    return "Done"
