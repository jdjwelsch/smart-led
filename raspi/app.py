from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import time

from sql_utils import create_devices_table, create_device_sql, set_device_status_sql, \
    get_device_status_sql, get_device_list_sql, update_device_ip_sql


app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})
db_file = 'db/devices.db'
# last time point at which a request was send: dirty way of ensuring that not too many requests are send
global last_request_send
last_request_send = 0


@app.before_first_request
def set_up_database():
    """
    Set up SQLite data base to store registered devices and their status.
    """
    print('Database set up started.')
    create_devices_table(db_file)


@app.route('/devices', methods=['GET', 'POST'])
def register_device():
    """
    Register new wifi-controlled devices on start up.

    New devices are expected to send a POST request with a json containing fields 'ip' and 'name'.
    :return:
    """
    device_list = get_device_list_sql(db_file)

    if request.method == 'POST':
        name = request.json['name']
        ip = request.json['ip']

        if name in device_list:
            update_device_ip_sql(db_file, name, ip)
            print('device %s already exists' % name)
            msg = {'message': 'device already exists'}
            return jsonify(msg)

        else:
            create_device_sql(db_file,
                              {'name': name,
                               'ip': ip,
                               'r': 0,
                               'g': 0,
                               'b': 0})
            print('device %s registered at %s.' % (name, ip))
            return Response("{'message': 'device created'}", status=201, mimetype='application/json')

    if request.method == 'GET':
        return jsonify(device_list)


@app.route('/devices/<name>', methods=['GET', 'PUT'])
def device_status(name):
    """
    Endpoint for communication with frontend for setting device properties.
    :param name: Name of device whose properties shall be accessed.
    :return:
    """
    if request.method == 'GET':
        device_status = get_device_status_sql(db_file, name)
        return jsonify(device_status)

    if request.method == 'PUT':
        status_dict = {}
        for color in ['r', 'g', 'b']:
            if color in request.json:
                color_value = request.json[color]
                status_dict.update({color: color_value})

        # update server data base
        set_device_status_sql(db_file, device_name=name, status_dict=status_dict)

        # send update to device
        set_device_status(name, status_dict)

        return Response("{'message': 'status changed'}", status=201, mimetype='application/json')


def set_device_status(device_name, status_dict):
    """
    Set state of a wifi controlled device.

    :param device_name: Name the device has been registered with
    :param status_dict: dictionary containing key-value pairs to be set
    :return:
    """
    global last_request_send
    current_time = time.time()
    if (current_time - last_request_send) > 0.2:
        last_request_send = current_time
        device_info = get_device_status_sql(db_file, device_name)
        ip = device_info['ip']
        url = 'http://' + ip + ':80/leds'
        print('send to %s' % url)
        requests.put(url, json=status_dict)
    else:
        print('too little time has passed')


@app.route('/')
def welcome():
    return 'Welcome to LED control backend'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=4999)
