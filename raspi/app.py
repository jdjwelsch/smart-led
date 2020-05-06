import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from sql_utils import create_devices_table, create_device_sql, \
    set_device_status_sql, \
    get_device_status_sql, get_device_list_sql, update_device_ip_sql


app = Flask(__name__, static_folder='frontend/dist/')
CORS(app, resources={r'/*': {'origins': '*'}})
socket = SocketIO(app, path='/ws/socket.io')
db_file = 'db/devices.db'

# set up HTTPAdapter to use for requests. Plain request does not allow to set
# the number of retries attempted for an http request.

# set max retries to 1, as put requests send to LEDs are send twice a
# second anyway
retry_strategy = Retry(total=1)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)


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

        return Response("{'message': 'status changed'}",
                        status=201,
                        mimetype='application/json')


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


def set_device_status(device_name=None):
    """
    Set state of a wifi controlled device.

    :param device_name: Name the device has been registered with. If None set
    device status of all devices in database
    """
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
            http.put(url, json=status_dict)
        except requests.exceptions.ConnectionError:
            print('could not reach ' + url)

    # broadcast new status to all connected clients
    all_device_status = get_device_status_sql(db_file)
    socket.emit('stateUpdate', all_device_status, broadcast=True)


def update_leds_continuously():
    """
    Sends the current setting to all LED devices in database twice per second.
    """
    while True:
        set_device_status()
        eventlet.sleep(0.5)


if __name__ == '__main__':
    # start thread for led stripe setting
    eventlet.spawn(update_leds_continuously)
    # start app
    socket.run(app, host='0.0.0.0', debug=True, port=4999)
