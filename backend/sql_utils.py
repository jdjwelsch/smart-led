import sqlite3
import logging
from contextlib import contextmanager

log = logging.getLogger(__name__)


@contextmanager
def _managed_db_connection(db_path):
    """
    Manage connection to data base, ensuring that it is always closed after use.

    :param db_path: string, path to .db file
    """
    conn = sqlite3.connect(db_path)
    try:
        yield conn

    finally:
        conn.close()


def create_devices_table(db_path):
    """
    Creates a SQL table in which device properties are stored.

    Table is created in database found at db_path. If the table already exists,
    nothing happens.

    :param db_path: string, path to .db file
    """

    # connect to database and create file, if it does not exist
    with _managed_db_connection(db_path) as conn:

        # define table with SQL string
        create_table_sql = """ CREATE TABLE IF NOT EXISTS devices (
                               name text PRIMARY KEY,
                               ip text,
                               r integer,
                               g integer,
                               b integer,
                               power integer);
                           """

        # set up table
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()


def create_device_sql(db_path, device_dict):
    """
    Create row for new device in devices table.

    :param db_path: string, path to .db file
    :param device_dict: dictionary containing keys 'name', 'ip', 'r', 'g', 'b',
    'power' for new device
    """
    with _managed_db_connection(db_path) as conn:
        log.debug('Write device to sql database')

        # write new device to db table
        device_values = (device_dict['name'],
                         device_dict['ip'],
                         device_dict['rgb'][0],
                         device_dict['rgb'][1],
                         device_dict['rgb'][2],
                         device_dict['power'])

        sql = """ INSERT INTO devices(name, ip, r, g, b, power)
                 VALUES(?, ?, ?, ?, ?, ?)
              """
        cursor = conn.cursor()
        cursor.execute(sql, device_values)
        conn.commit()


def update_device_ip_sql(db_path, device_name, ip):
    """
    Update the ip adress of an already existing device.

    :param db_path: string, path to .db file
    :param device_name: string, name of the device whose IP address will be
    updated
    :param ip: string, new ip address
    """
    with _managed_db_connection(db_path) as conn:
        sql = """ UPDATE devices
                  SET ip = ? WHERE name = ?"""

        cursor = conn.cursor()
        cursor.execute(sql, (ip, device_name))
        conn.commit()


def set_device_status_sql(db_path, device_name, status_dict):
    """
    Set the status (i. e. RGB and power values) of a device.

    :param db_path: string, path to .db file
    :param device_name: string, name of device
    :param status_dict: dict, containing keys 'rgb' and 'power'
    """
    with _managed_db_connection(db_path) as conn:
        new_values = (status_dict['rgb'][0],
                      status_dict['rgb'][1],
                      status_dict['rgb'][2],
                      status_dict['power'],
                      device_name)

        sql = """ UPDATE devices
                  SET r = ?,
                      g = ?,
                      b = ?,
                      power = ?
                  WHERE name = ?"""

        cursor = conn.cursor()
        cursor.execute(sql, new_values)
        conn.commit()


def get_device_status_sql(db_path, device_name=None):
    """
    Get properties of a device.

    :param db_path: string, path to .db file
    :param device_name: string, name of device, if None return list of status
    dictionaries for all registered devices
    :return: list of dicts, containing keys 'ip', 'rgb', and 'power' for device
    with device_name
    """
    with _managed_db_connection(db_path) as conn:
        if device_name is not None:
            sql = "SELECT * FROM devices WHERE name = ?"
            cursor = conn.cursor()
            cursor.execute(sql, (device_name,))

        else:
            sql = "SELECT * FROM devices"
            cursor = conn.cursor()
            cursor.execute(sql)

        status = cursor.fetchall()
        status_list = []
        for i in range(len(status)):
            return_dict = {
                'name': status[i][0],
                'ip': status[i][1],
                'rgb': (status[i][2],
                        status[i][3],
                        status[i][4]),
                'power': status[i][5]
            }
            status_list.append(return_dict)
        return status_list


def get_device_list_sql(db_path):
    """
    Get list of all devices registered in database.

    :param db_path: string, path to .db file
    :return: list of strings, containing all device_names present in data base.
    """
    with _managed_db_connection(db_path) as conn:
        sql = "SELECT name FROM devices"
        cursor = conn.cursor()
        cursor.execute(sql)
        devices = cursor.fetchall()

        device_list = [row[0] for row in devices]

        return device_list
