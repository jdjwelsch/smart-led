import sqlite3


def _create_db_connection(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(e)

    return conn


def create_devices_table(db_path):
    conn = None
    try:
        # connect to database and create file, if it does not exist
        conn = _create_db_connection(db_path)

        # define table with SQL string
        create_table_sql = """ CREATE TABLE IF NOT EXISTS devices (
                               name text PRIMARY KEY,
                               ip text,
                               r integer,
                               g integer,
                               b integer);
                           """

        # set up table
        cursor = conn.cursor()
        cursor.execute(create_table_sql)

    except sqlite3.Error as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def create_device_sql(db_path, device_dict):

    conn = None
    try:
        print('Write device to sql database')
        conn = _create_db_connection(db_path)

        with conn:
            # write new device to db table
            device_values = (device_dict['name'],
                             device_dict['ip'],
                             device_dict['r'],
                             device_dict['g'],
                             device_dict['b'])

            sql = """ INSERT INTO devices(name, ip, r, g, b)
                     VALUES(?, ?, ?, ?, ?);
                  """
            cursor = conn.cursor()
            cursor.execute(sql, device_values)

    except sqlite3.Error as e:
        print(e)

    finally:
        if conn is not None:
            conn.close()


def update_device_ip_sql(db_path, device_name, ip):

    conn = None
    try:
        conn = _create_db_connection(db_path)

        with conn:
            sql = """ UPDATE devices
                      SET ip = ? WHERE name = ?"""

            cursor = conn.cursor()
            cursor.execute(sql, (ip, device_name))
            conn.commit()

    except sqlite3.Error as e:
        print(e)

    finally:
        if conn is not None:
            conn.close()


def set_device_status_sql(db_path, device_name, status_dict):

    conn = None
    try:
        conn = _create_db_connection(db_path)

        with conn:
            new_values = (status_dict['r'],
                          status_dict['g'],
                          status_dict['b'],
                          device_name)

            sql = """ UPDATE devices
                      SET r = ?,
                          g = ?,
                          b = ?
                      WHERE name = ?"""

            cursor = conn.cursor()
            cursor.execute(sql, new_values)
            conn.commit()

    except sqlite3.Error as e:
        print(e)

    finally:
        if conn is not None:
            conn.close()


def get_device_status_sql(db_path, device_name):
    conn = None
    try:
        conn = _create_db_connection(db_path)

        with conn:
            sql = "SELECT * FROM devices WHERE name = ?"
            cursor = conn.cursor()
            cursor.execute(sql, (device_name,))
            status = cursor.fetchall()
            return_dict = {
                'ip': status[0][1],
                'r': status[0][2],
                'g': status[0][3],
                'b': status[0][4],
            }
        return return_dict

    except sqlite3.Error as e:
        print(e)

    finally:
        if conn is not None:
            conn.close()


def get_device_list_sql(db_path):

    conn = None
    try:
        conn = _create_db_connection(db_path)

        with conn:
            sql = "SELECT name FROM devices"
            cursor = conn.cursor()
            cursor.execute(sql)
            devices = cursor.fetchall()

        device_list = [row[0] for row in devices]

        return device_list

    except sqlite3.Error as e:
        print(e)

    finally:
        if conn is not None:
            conn.close()

