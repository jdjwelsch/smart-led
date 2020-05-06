import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests

from sql_utils import create_devices_table, create_device_sql, \
    set_device_status_sql, \
    get_device_status_sql, get_device_list_sql, update_device_ip_sql


app = Flask(__name__, static_folder='frontend/dist/')
CORS(app, resources={r'/*': {'origins': '*'}})
socket = SocketIO(app, path='/ws/socket.io')
db_file = 'db/devices.db'



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

    New devices are expected to send a POST request with a json containing
    fields 'ip' and 'name'.
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
                               'rgb': (0, 0, 0)})
            print('device %s registered at %s.' % (name, ip))
            return Response("{'message': 'device created'}",
                            status=201,
                            mimetype='application/json')

    if request.method == 'GET':
        return jsonify(device_list)


# TODO: replace with sockets?
@app.route('/devices/<name>', methods=['GET', 'PUT'])
def device_status(name):
    """
    Endpoint for communication with frontend for setting device properties.
    :param name: Name of device whose properties shall be accessed.
    :return:
    """
    if request.method == 'GET':
        device_status = get_device_status_sql(db_file, name)[0]
        return jsonify(device_status)

    if request.method == 'PUT':
        status_dict = {}
        # TODO: refactor API on esp8266 to take rgb tuple
        for i, color in enumerate(['r', 'g', 'b']):
            color_value = request.json['rgb'][i]
            status_dict.update({color: color_value})

        # update server data base
        set_device_status_sql(db_file,
                              device_name=name,
                              status_dict={'rgb': request.json['rgb']})

        # send update to device
        # set_device_status(name)

        return Response("{'message': 'status changed'}",
                        status=201,
                        mimetype='application/json')


def set_device_status(device_name=None):
    """
    Set state of a wifi controlled device.

    :param device_name: Name the device has been registered with
    :param status_dict: dictionary containing key-value pairs to be set
    :return:
    """
    while True:
        # set all devices if not specified
        if device_name is None:
            devices = get_device_list_sql(db_file)
        else:
            devices = [device_name]
        device_info = get_device_status_sql(db_file, device_name)

        # send requests to LED strips
        for i, d in enumerate(devices):
            ip = device_info[i]['ip']
            url = 'http://' + ip + ':80/leds'
            print('send to %s' % url)

            status_dict = {}
            for j, color in enumerate(['r', 'g', 'b']):
                status_dict.update({color: device_info[i]['rgb'][j]})

            try:
                requests.put(url, json=status_dict)
            except requests.exceptions.ConnectionError:
                print('could not reach ' + url)

        # TODO: send only if something really changed
        # broadcast new status to all connected clients
        all_device_status = get_device_status_sql(db_file)
        socket.emit('stateUpdate', all_device_status, broadcast=True)
        eventlet.sleep(0.5)

# start thread for led stripe setting
eventlet.spawn(set_device_status)


@socket.on('connect')
def client_has_connected():
    print("A client has connected")


@socket.on('getState')
def send_all_devices_state():
    all_device_status = get_device_status_sql(db_file)
    emit('stateUpdate', all_device_status)


@app.route('/')
def welcome():
    # serve frontend application
    return send_from_directory('frontend/dist', 'index.html')
    # return 'Welcome to LED control backend'


if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True, port=4999)
    socket.run(app, host='0.0.0.0', debug=True, port=4999)
